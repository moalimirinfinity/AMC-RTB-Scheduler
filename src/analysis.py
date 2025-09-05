import math
from typing import List, Dict
from .system import Task

def solve_response_time_equation(c_val: int, interferences: List[tuple], deadline: int) -> int:
    """
    Solves the recurrence relation for response time using fixed-point iteration.
    This function terminates and returns a value > deadline if the task is unschedulable.
    """
    r = c_val + sum(wcet for _, wcet in interferences)
    if r > deadline:
        return r

    while True:
        interference_sum = sum(math.ceil(r / period) * wcet for period, wcet in interferences)
        r_new = c_val + interference_sum
        
        if r_new == r or r_new > deadline:
            return r_new
        r = r_new

def analyze_lo_mode_schedulability(task_set: List[Task]) -> Dict[int, int]:
    """
    Calculates R_LO for all tasks. Corresponds to Eq. (4) in the paper.
    Returns a dictionary of {task_id: r_lo} or an empty dict if unschedulable.
    """
    r_lo_values = {}
    print("--- Analyzing LO-Mode Schedulability ---")
    
    for task in sorted(task_set, key=lambda t: t.priority):
        hp_tasks = [t for t in task_set if t.priority < task.priority]
        interferences = [(hp.period, hp.wcet_lo) for hp in hp_tasks]
        r_lo = solve_response_time_equation(task.wcet_lo, interferences, task.deadline)
        
        if r_lo > task.deadline:
            print(f"❌ UNSCHEDULABLE: Task {task.name} misses deadline in LO-mode. R(LO)={r_lo} > D={task.deadline}")
            return {}
            
        print(f"✅ Task {task.name}: R(LO) = {r_lo}, Deadline = {task.deadline}")
        r_lo_values[task.id] = r_lo
    return r_lo_values

def analyze_hi_mode_schedulability(task_set: List[Task]) -> bool:
    """Calculates R_HI for HI-crit tasks in stable HI-mode. Corresponds to Eq. (5)."""
    print("\n--- Analyzing HI-Mode Schedulability (Stable) ---")
    hi_crit_tasks = [t for t in task_set if t.criticality == 'HI']
    
    for task in sorted(hi_crit_tasks, key=lambda t: t.priority):
        hp_hi_tasks = [hp for hp in hi_crit_tasks if hp.priority < task.priority]
        interferences = [(hp.period, hp.wcet_hi) for hp in hp_hi_tasks]
        r_hi = solve_response_time_equation(task.wcet_hi, interferences, task.deadline)
        
        if r_hi > task.deadline:
            print(f"❌ UNSCHEDULABLE: Task {task.name} misses deadline in HI-mode. R(HI)={r_hi} > D={task.deadline}")
            return False
        print(f"✅ Task {task.name}: R(HI) = {r_hi}, Deadline = {task.deadline}")
    return True

def analyze_transition_schedulability_rtb(task_set: List[Task], r_lo_values: Dict[int, int]) -> bool:
    """Performs AMC-rtb analysis for the mode transition. Corresponds to Eq. (7)."""
    print("\n--- Analyzing Transition Schedulability (AMC-rtb) ---")
    hi_crit_tasks = [t for t in task_set if t.criticality == 'HI']
    
    for task in sorted(hi_crit_tasks, key=lambda t: t.priority):
        hp_tasks = [hp for hp in task_set if hp.priority < task.priority]
        
        # Dynamic interference from higher-priority HI-crit tasks
        hp_hi_interferences = [(hp.period, hp.wcet_hi) for hp in hp_tasks if hp.criticality == 'HI']
        
        # Fixed interference from higher-priority LO-crit tasks, capped by R_LO
        r_i_lo = r_lo_values[task.id]
        fixed_lo_interference = sum(
            math.ceil(r_i_lo / hp.period) * hp.wcet_lo
            for hp in hp_tasks if hp.criticality == 'LO'
        )
        base_c = task.wcet_hi + fixed_lo_interference
        
        r_star = solve_response_time_equation(base_c, hp_hi_interferences, task.deadline)
        
        if r_star > task.deadline:
            print(f"❌ UNSCHEDULABLE: Task {task.name} misses deadline during transition. R*={r_star} > D={task.deadline}")
            return False
        print(f"✅ Task {task.name}: R* = {r_star}, Deadline = {task.deadline}")
    return True

