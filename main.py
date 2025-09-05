import json
from src.system import Task
from src.analysis import (
    analyze_lo_mode_schedulability,
    analyze_hi_mode_schedulability,
    analyze_transition_schedulability_rtb,
)
from src.simulator import Simulator, Scenario

TASK_SET_FILE = "task_set.json"

def main():
    """Main function to run the full analysis and simulation pipeline."""
    # Load the generated task set
    try:
        with open(TASK_SET_FILE, "r") as f:
            tasks_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Task set file '{TASK_SET_FILE}' not found.")
        print("   Please run 'make data' first.")
        return

    task_set = [Task(**data) for data in tasks_data]
    
    # --- 1. Theoretical Analysis ---
    print("--- 🚀 Starting Theoretical Schedulability Analysis ---")
    r_lo_values = analyze_lo_mode_schedulability(task_set)
    if not r_lo_values:
        print("\n--- ⏹️ Analysis stopped: Task set is unschedulable in LO-mode. ---")
        return

    if not analyze_hi_mode_schedulability(task_set):
        print("\n--- ⏹️ Analysis stopped: Task set is unschedulable in stable HI-mode. ---")
        return

    if not analyze_transition_schedulability_rtb(task_set, r_lo_values):
        print("\n--- ⏹️ Analysis stopped: Task set is unschedulable during LO->HI transition. ---")
        return
        
    print("\n--- 🎉 SUCCESS: The task set is theoretically schedulable under AMC-rtb! ---")

    # --- 2. Simulation ---
    print("\n\n--- 🚀 Starting Discrete-Event Simulation ---")
    
    # Find the hyperperiod for a reasonable simulation time
    hyperperiod = max(t.period for t in task_set)
    simulation_duration = 2 * hyperperiod

    # Scenario 1: LO-Mode
    print(f"\n--- Running LO-Mode Scenario (Duration: {simulation_duration}) ---")
    simulator_lo = Simulator(task_set)
    simulator_lo.run(simulation_duration, Scenario.LO_MODE)

    # Scenario 2: HI-Mode (with criticality switch)
    print(f"\n--- Running HI-Mode Scenario (Duration: {simulation_duration}) ---")
    simulator_hi = Simulator(task_set)
    simulator_hi.run(simulation_duration, Scenario.HI_MODE)

if __name__ == "__main__":
    main()