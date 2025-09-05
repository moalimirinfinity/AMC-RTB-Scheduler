import json
import random
from typing import Dict, List, Any

# --- Constants ---
WCET_DATA_FILE = "wcet_data.json"
TASK_SET_FILE = "task_set.json"

# Probability of a task being assigned HI-criticality.
CRITICALITY_HI_PROB = 0.4
# Range for the factor by which a task's period exceeds its WCET(LO).
PERIOD_FACTOR_RANGE = (8, 15)
# Range for the factor by which WCET(HI) exceeds WCET(LO) for HI-crit tasks.
C_HI_FACTOR_RANGE = (1.5, 2.0)

def generate_task_set(wcet_data: Dict[str, int]) -> List[Dict[str, Any]]:
    """
    Generates a mixed-criticality task set based on measured WCET data.
    """
    tasks = []
    
    # Sort benchmarks by WCET to help with assigning priorities later.
    sorted_benchmarks = sorted(wcet_data.items(), key=lambda item: item[1])

    for i, (name, wcet_lo) in enumerate(sorted_benchmarks):
        is_hi_crit = random.random() < CRITICALITY_HI_PROB
        
        # --- FIX: Ensure a non-zero period ---
        # If wcet_lo is 0 (due to VM measurement issue), use a small base to prevent a period of 0.
        effective_wcet = wcet_lo if wcet_lo > 0 else 1 
        period = int(effective_wcet * random.uniform(*PERIOD_FACTOR_RANGE))
        
        # Ensure period is at least 1
        if period == 0:
            period = 1

        deadline = period  # Assume Deadline = Period for this model.
        
        task = {
            "id": i + 1,
            "name": name.capitalize(),
            "period": period,
            "deadline": deadline,
            "wcet_lo": wcet_lo,
            "criticality": "HI" if is_hi_crit else "LO",
            "wcet_hi": None # Default to None
        }
        
        if is_hi_crit:
            c_hi_factor = random.uniform(*C_HI_FACTOR_RANGE)
            task["wcet_hi"] = int(wcet_lo * c_hi_factor)
        
        tasks.append(task)
        
    # Assign priorities using Deadline Monotonic Priority Ordering (DMPO).
    tasks.sort(key=lambda t: t['deadline'])
    for priority, task in enumerate(tasks, 1):
        task['priority'] = priority
        
    return tasks

def main():
    """Main function to generate and save the task set."""
    try:
        with open(WCET_DATA_FILE, "r") as f:
            wcet_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{WCET_DATA_FILE}' not found. Run 'make data' first.")
        return

    task_set = generate_task_set(wcet_data)
    
    with open(TASK_SET_FILE, "w") as f:
        json.dump(task_set, f, indent=4)
        
    print(f"✅ Task set generated with {len(task_set)} tasks.")
    print(f"   Saved to '{TASK_SET_FILE}'.")

if __name__ == "__main__":
    main()