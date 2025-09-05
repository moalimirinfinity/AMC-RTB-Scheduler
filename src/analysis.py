import math
from typing import List, Dict, Tuple
from .system import Task

def solve_response_time_equation(wcet: int, interferences: List[Tuple[int, int]], deadline: int) -> int:
    """
    Solves the response time recurrence relation using fixed-point iteration.

    This function calculates the worst-case response time for a task. It terminates
    and returns a value greater than the deadline if the task is unschedulable.

    Args:
        wcet: The worst-case execution time of the task being analyzed.
        interferences: A list of tuples, where each tuple contains the
                       (period, wcet) of a higher-priority task.
        deadline: The deadline of the task.

    Returns:
        The calculated worst-case response time.
    """
    response_time = wcet + sum(hp_wcet for _, hp_wcet in interferences)
    if response_time > deadline:
        return response_time

    while True:
        interference_sum = sum(math.ceil(response_time / period) * hp_wcet for period, hp_wcet in interferences)
        new_response_time = wcet + interference_sum
        
        if new_response_time == response_time or new_response_time > deadline:
            return new_response_time
        response_time = new_response_time

def analyze_lo_mode_schedulability(task_set: List[Task]) -> Dict[int, int]:
    """
    Calculates R_LO for all tasks to check LO-mode schedulability (Eq. 4 from the paper).

    Args:
        task_set: The list of tasks in the system.

    Returns:
        A dictionary mapping task_id to its R_LO if schedulable, otherwise an empty dict.
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
    """
    Calculates R_HI for HI-criticality tasks in stable HI-mode (Eq. 5 from the paper).

    Args:
        task_set: The list of tasks in the system.

    Returns:
        True if all HI-crit tasks are schedulable in HI-mode, False otherwise.
    """
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
    """
    Performs AMC-rtb analysis for the mode transition (Eq. 7 from the paper).

    Args:
        task_set: The list of tasks in the system.
        r_lo_values: A dictionary of pre-calculated R_LO values for all tasks.

    Returns:
        True if all HI-crit tasks are schedulable during the transition, False otherwise.
    """
    print("\n--- Analyzing Transition Schedulability (AMC-rtb) ---")
    hi_crit_tasks = [t for t in task_set if t.criticality == 'HI']
    
    for task in sorted(hi_crit_tasks, key=lambda t: t.priority):
        hp_tasks = [hp for hp in task_set if hp.priority < task.priority]
        
        # Interference from higher-priority HI-criticality tasks (dynamic part)
        hp_hi_interferences = [(hp.period, hp.wcet_hi) for hp in hp_tasks if hp.criticality == 'HI']
        
        # Interference from higher-priority LO-criticality tasks (fixed part, capped by R_LO)
        r_i_lo = r_lo_values[task.id]
        fixed_lo_interference = sum(
            math.ceil(r_i_lo / hp.period) * hp.wcet_lo
            for hp in hp_tasks if hp.criticality == 'LO'
        )
        
        # The base execution time for the response time equation includes the task's own WCET(HI)
        # and the capped interference from LO-criticality tasks.
        base_wcet = task.wcet_hi + fixed_lo_interference
        
        r_star = solve_response_time_equation(base_wcet, hp_hi_interferences, task.deadline)
        
        if r_star > task.deadline:
            print(f"❌ UNSCHEDULABLE: Task {task.name} misses deadline during transition. R*={r_star} > D={task.deadline}")
            return False
        print(f"✅ Task {task.name}: R* = {r_star}, Deadline = {task.deadline}")
    return True