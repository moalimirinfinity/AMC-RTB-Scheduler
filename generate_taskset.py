import json
import random

WCET_DATA_FILE = "wcet_data.json"
TASK_SET_FILE = "task_set.json"

# Factors for generating task parameters
CRITICALITY_HI_PROB = 0.4  # Probability of a task being HI-criticality
PERIOD_FACTOR_RANGE = (8, 15)  # How many times larger the period is than the WCET
C_HI_FACTOR_RANGE = (1.5, 2.0) # How many times larger C(HI) is than C(LO)

def generate_task_set(wcet_data: dict):
    """
    Generates a mixed-criticality task set based on WCET data.
    """
    tasks = []
    
    # Sort by WCET to aid in assigning better priorities later
    sorted_benchmarks = sorted(wcet_data.items(), key=lambda item: item[1])

    for i, (name, wcet_lo) in enumerate(sorted_benchmarks):
        # Assign criticality level
        is_hi_crit = random.random() < CRITICALITY_HI_PROB
        
        # Generate period and deadline
        period = int(wcet_lo * random.uniform(*PERIOD_FACTOR_RANGE))
        deadline = period  # Assume D=T for simplicity
        
        task = {
            "id": i + 1,
            "name": name.capitalize(),
            "period": period,
            "deadline": deadline,
            "wcet_lo": wcet_lo,
            "criticality": "HI" if is_hi_crit else "LO",
        }
        
        if is_hi_crit:
            c_hi_factor = random.uniform(*C_HI_FACTOR_RANGE)
            task["wcet_hi"] = int(wcet_lo * c_hi_factor)
        else:
            task["wcet_hi"] = None
        
        tasks.append(task)
        
    # Assign priorities using Deadline Monotonic Priority Ordering (DMPO)
    tasks.sort(key=lambda t: t['deadline'])
    for priority, task in enumerate(tasks, 1):
        task['priority'] = priority
        
    return tasks

def main():
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

import json
import random

WCET_DATA_FILE = "wcet_data.json"
TASK_SET_FILE = "task_set.json"
CRITICALITY_HI_PROB = 0.4
PERIOD_FACTOR_RANGE = (10, 20)
C_HI_FACTOR_RANGE = (1.5, 2.0)

def generate_task_set(wcet_data: dict):
    tasks = []
    total_lo_utilization = 0.0
    
    sorted_benchmarks = sorted(wcet_data.items(), key=lambda item: item[1])

    for i, (name, wcet_lo) in enumerate(sorted_benchmarks):
        if wcet_lo == 0:
            print(f"  ⚠️ Skipping task {name} due to zero WCET.")
            continue
            
        is_hi_crit = random.random() < CRITICALITY_HI_PROB
        period = int(wcet_lo * random.uniform(*PERIOD_FACTOR_RANGE))
        deadline = period
        
        task = {
            "id": i + 1, "name": name.capitalize(), "period": period,
            "deadline": deadline, "wcet_lo": wcet_lo,
            "criticality": "HI" if is_hi_crit else "LO",
        }
        
        if is_hi_crit:
            task["wcet_hi"] = int(wcet_lo * random.uniform(*C_HI_FACTOR_RANGE))
        else:
            task["wcet_hi"] = None
        
        tasks.append(task)
        total_lo_utilization += wcet_lo / period
        
    tasks.sort(key=lambda t: t['deadline'])
    for priority, task in enumerate(tasks, 1):
        task['priority'] = priority
        
    print(f"  📈 Total LO-mode utilization: {total_lo_utilization:.2%}")
    if total_lo_utilization > 1.0:
        print("  ⚠️ Warning: Total LO-mode utilization exceeds 100%. The task set is likely unschedulable.")
        
    return tasks

def main():
    try:
        with open(WCET_DATA_FILE, "r") as f:
            wcet_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{WCET_DATA_FILE}' not found. Run 'make data' first.")
        return

    task_set = generate_task_set(wcet_data)
    
    with open(TASK_SET_FILE, "w") as f:
        json.dump(task_set, f, indent=4)
        
    print(f"✅ Task set generated with {len(task_set)} tasks and saved to '{TASK_SET_FILE}'.")

if __name__ == "__main__":
    main()

