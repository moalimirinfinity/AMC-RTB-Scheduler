import heapq
from typing import List
from .system import Task, Job
from enum import Enum, auto

class SystemMode(Enum):
    LO = auto()
    HI = auto()

class Scenario(Enum):
    LO_MODE = auto()
    HI_MODE = auto()

class Simulator:
    """Event-driven simulator for an AMC fixed-priority preemptive scheduler."""
    def __init__(self, task_set: List[Task]):
        self.tasks = task_set
        self.time = 0
        self.system_mode = SystemMode.LO
        self.ready_queue: List[Job] = []  # A min-heap of Jobs, ordered by priority
        self.current_job: Job | None = None
        self.log = []
        self.scenario: Scenario | None = None

    def _add_log(self, message: str):
        self.log.append(f"[{self.time:06d}] {message}")

    def _release_jobs(self):
        """Check for new job releases at the current time and add them to the ready queue."""
        for task in self.tasks:
            if self.time % task.period == 0:
                exec_time = task.wcet_lo
                if self.scenario == Scenario.HI_MODE and task.criticality == 'HI':
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

    def _handle_mode_switch(self):
        """If in HI mode, drop all LO-criticality jobs."""
        if self.system_mode == SystemMode.HI and any(j.criticality == 'LO' for j in self.ready_queue):
            self.ready_queue = [j for j in self.ready_queue if j.criticality == 'HI']
            heapq.heapify(self.ready_queue)
            self._add_log("System switched to HI mode. Dropped all LO-criticality jobs.")

    def _scheduler_tick(self):
        """Handles the core scheduling logic for a single time unit."""
        self._handle_mode_switch()

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

    def run(self, max_time: int, scenario: Scenario):
        """Runs the simulation for a given duration and scenario."""
        self.scenario = scenario
        self._add_log(f"--- Simulation Started: Scenario={scenario.name}, Duration={max_time} ---")

        while self.time < max_time:
            self._release_jobs()
            self._scheduler_tick()

            if self.current_job:
                self.current_job.remaining_wcet -= 1
                self.current_job.wcet_lo_budget -= 1
                
                # Check for criticality switch
                if self.system_mode == SystemMode.LO and self.current_job.wcet_lo_budget < 0:
                    self._add_log(f"‼️ CRITICALITY SWITCH: {self.current_job.name} exceeded its C(LO) budget!")
                    self.system_mode = SystemMode.HI
                    self._scheduler_tick()  # Re-evaluate scheduler immediately

                # Check for job completion
                if self.current_job.remaining_wcet == 0:
                    response_time = (self.time + 1) - self.current_job.arrival_time
                    self._add_log(f"Job Finished: {self.current_job.name}, Response Time: {response_time}")
                    if (self.time + 1) > self.current_job.deadline:
                        self._add_log(f"🔥 DEADLINE MISS: {self.current_job.name} missed its deadline!")
                    
                    heapq.heappop(self.ready_queue)
                    self.current_job = None
            
            self.time += 1
            
        print("\n--- Simulation Log ---")
        for entry in self.log:
            print(entry)