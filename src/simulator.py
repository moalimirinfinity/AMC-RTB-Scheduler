import heapq
from typing import List
from .system import Task, Job

class Simulator:
    """Event-driven simulator for an AMC fixed-priority preemptive scheduler."""
    def __init__(self, task_set: List[Task]):
        self.tasks = task_set
        self.time = 0
        self.system_mode = 'LO'
        self.ready_queue = [] # A min-heap of Jobs, prioritized by priority
        self.current_job: Job | None = None
        self.log = []

    def _add_log(self, message: str):
        self.log.append(f"[{self.time:06d}] {message}")

    def _release_jobs(self):
        """Check for new job releases at the current time."""
        for task in self.tasks:
            if self.time % task.period == 0:
                # In the HI_MODE scenario, HI-crit tasks use their C(HI)
                exec_time = task.wcet_lo
                if self.scenario == 'HI_MODE' and task.criticality == 'HI':
                    exec_time = task.wcet_hi

                job = Job(
                    arrival_time=self.time,
                    deadline=self.time + task.deadline,
                    remaining_wcet=exec_time,
                    wcet_lo_budget=task.wcet_lo,
                    parent_task=task
                )
                heapq.heappush(self.ready_queue, job)
                self._add_log(f"Job Released: {job.name}, Prio: {job.priority}, WCET: {job.remaining_wcet}")

    def _scheduler_tick(self):
        """Handles scheduling logic for a single time unit."""
        if self.system_mode == 'HI':
            # If there are any LO-crit jobs, drop them from the ready queue
            if any(j.criticality == 'LO' for j in self.ready_queue):
                self.ready_queue = [j for j in self.ready_queue if j.criticality == 'HI']
                heapq.heapify(self.ready_queue)
                self._add_log("Dropped all LO-criticality jobs from the ready queue.")

        if not self.ready_queue:
            if self.current_job:
                self._add_log("CPU is now idle.")
                self.current_job = None
            return

        highest_prio_job = self.ready_queue[0]

        if self.current_job is None:
            self.current_job = highest_prio_job
            self._add_log(f"Execution Started: {self.current_job.name}")
        elif highest_prio_job.priority < self.current_job.priority:
            self._add_log(f"PREEMPTION: {highest_prio_job.name} preempts {self.current_job.name}")
            self.current_job = highest_prio_job

    def run(self, max_time: int, scenario: str):
        self.scenario = scenario
        self._add_log(f"--- Simulation Started: Scenario={scenario}, Duration={max_time} ---")

        while self.time < max_time:
            self._release_jobs()
            self._scheduler_tick()

            if self.current_job:
                self.current_job.remaining_wcet -= 1
                self.current_job.wcet_lo_budget -= 1
                
                if self.system_mode == 'LO' and self.current_job.wcet_lo_budget < 0:
                    self._add_log(f"‼️ CRITICALITY SWITCH: {self.current_job.name} exceeded its C(LO) budget!")
                    self.system_mode = 'HI'
                    self._scheduler_tick() # Re-evaluate scheduler immediately after mode switch

                if self.current_job.remaining_wcet == 0:
                    response_time = self.time + 1 - self.current_job.arrival_time
                    self._add_log(f"Job Finished: {self.current_job.name}, Response Time: {response_time}")
                    if self.time + 1 > self.current_job.deadline:
                        self._add_log(f"🔥 DEADLINE MISS: {self.current_job.name} missed its deadline!")
                    
                    heapq.heappop(self.ready_queue) # Remove completed job
                    self.current_job = None
            
            self.time += 1
            
        print("\n--- Simulation Log ---")
        for entry in self.log:
            print(entry)

