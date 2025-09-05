import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Tuple

from src.system import Task
from src.analysis import (
    analyze_lo_mode_schedulability,
    analyze_hi_mode_schedulability,
    analyze_transition_schedulability_rtb,
)
from src.simulator import Simulator, Scenario

TASK_SET_FILE = "task_set.json"

def plot_gantt_chart(history: List[Tuple[int, str, str]], task_set: List[Task], scenario: Scenario, max_time: int):
    """Generates and saves a Gantt chart from the simulation history."""
    print(f"--- 📊 Generating Gantt Chart for {scenario.name} ---")
    
    df = pd.DataFrame(history, columns=['Timestamp', 'Task', 'Criticality'])
    
    tasks = sorted(list(set(df.Task.unique()) - {'Idle'}), key=lambda x: next(t.priority for t in task_set if t.name == x))
    task_y_map = {task: i for i, task in enumerate(tasks)}
    
    plt.figure(figsize=(20, 6))
    
    colors = {'LO': 'C0', 'HI': 'C3', 'N/A': 'gray'}

    for task_name, y_pos in task_y_map.items():
        task_df = df[df.Task == task_name]
        if not task_df.empty:
            crit = task_df.Criticality.iloc[0]
            plt.barh(y=y_pos, left=task_df.Timestamp, width=1, color=colors[crit], align='center', edgecolor=colors[crit])

    # Plot Idle time
    idle_df = df[df.Task == 'Idle']
    if not idle_df.empty:
        plt.barh(y=-1, left=idle_df.Timestamp, width=1, color=colors['N/A'], align='center', label='Idle', edgecolor=colors['N/A'])

    # Add job release markers
    for task in task_set:
        if task.name in task_y_map:
            y_pos = task_y_map[task.name]
            for t in range(0, max_time, task.period):
                plt.plot(t, y_pos, 'k^', markersize=8, label=f'Release' if t==0 else "")

    plt.yticks(list(task_y_map.values()), list(task_y_map.keys()))
    plt.xlabel("Time (ticks)")
    plt.title(f"AMC-RTB Scheduler Gantt Chart ({scenario.name})")
    plt.grid(axis='x', linestyle='--')
    
    # Create legend
    handles = [plt.Rectangle((0,0),1,1, color=colors[c]) for c in ['LO', 'HI']]
    labels = ['LO-Criticality', 'HI-Criticality']
    plt.legend(handles, labels)
    
    filename = f"gantt_chart_{scenario.name.lower()}.png"
    plt.savefig(filename)
    print(f"✅ Chart saved to '{filename}'")
    plt.close()


def main():
    """Main function to run the full analysis and simulation pipeline."""
    try:
        with open(TASK_SET_FILE, "r") as f:
            tasks_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Task set file '{TASK_SET_FILE}' not found. Please run 'make data' first.")
        return

    task_set = [Task(**data) for data in tasks_data]
    
    print("--- 🚀 Starting Theoretical Schedulability Analysis ---")
    r_lo_values = analyze_lo_mode_schedulability(task_set)
    if not r_lo_values: return

    if not analyze_hi_mode_schedulability(task_set): return
    if not analyze_transition_schedulability_rtb(task_set, r_lo_values): return
        
    print("\n--- 🎉 SUCCESS: The task set is theoretically schedulable! ---")

    # --- Simulation ---
    print("\n\n--- 🚀 Starting Discrete-Event Simulation ---")
    hyperperiod = max(t.period for t in task_set if t.period > 0) if any(t.period for t in task_set) else 100
    simulation_duration = hyperperiod 

    # Scenario 1: LO-Mode
    print(f"\n--- Running LO-Mode Scenario (Duration: {simulation_duration}) ---")
    simulator_lo = Simulator(task_set)
    simulator_lo.run(simulation_duration, Scenario.LO_MODE)
    print(simulator_lo.get_log_dataframe().head())
    plot_gantt_chart(simulator_lo.execution_history, task_set, Scenario.LO_MODE, simulation_duration)

    # Scenario 2: HI-Mode
    print(f"\n--- Running HI-Mode Scenario (Duration: {simulation_duration}) ---")
    simulator_hi = Simulator(task_set)
    simulator_hi.run(simulation_duration, Scenario.HI_MODE)
    print(simulator_hi.get_log_dataframe().head())
    plot_gantt_chart(simulator_hi.execution_history, task_set, Scenario.HI_MODE, simulation_duration)

if __name__ == "__main__":
    main()