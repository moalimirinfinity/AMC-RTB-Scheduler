import heapq
import pandas as pd
from typing import List, Dict, Any, Tuple
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
        self.ready_queue: List[Job] = []
        self.current_job: Job | None = None
        self.log: List[Dict[str, Any]] = []
        self.scenario: Scenario | None = None
        # New: Detailed history for Gantt chart
        self.execution_history: List[Tuple[int, str, str]] = []

    def _add_log(self, event: str, details: str = ""):
        self.log.append({
            "Timestamp": self.time, "Event": event, "Details": details,
            "SystemMode": self.system_mode.name,
            "RunningJob": self.current_job.name if self.current_job else "Idle",
        })

    def _release_jobs(self):
        for task in self.tasks:
            if self.time % task.period == 0:
                exec_time = task.wcet_lo
                if self.scenario == Scenario.HI_MODE and task.criticality == 'HI':
                    exec_time = task.wcet_hi
                job = Job(
                    arrival_time=self.time, deadline=self.time + task.deadline,
                    remaining_wcet=exec_time, wcet_lo_budget=task.wcet_lo,
                    parent_task=task
                )
                heapq.heappush(self.ready_queue, job)
                self._add_log("Job Released", f"{job.name} (Prio: {job.priority}, WCET: {job.remaining_wcet})")

    def _handle_mode_switch(self):
        if self.system_mode == SystemMode.HI and any(j.criticality == 'LO' for j in self.ready_queue):
            lo_jobs_dropped = [j.name for j in self.ready_queue if j.criticality == 'LO']
            self.ready_queue = [j for j in self.ready_queue if j.criticality == 'HI']
            heapq.heapify(self.ready_queue)
            if lo_jobs_dropped:
                self._add_log("Mode Switch", f"Dropped LO-jobs: {', '.join(lo_jobs_dropped)}")

    def _scheduler_tick(self):
        self._handle_mode_switch()
        if not self.ready_queue:
            if self.current_job:
                self._add_log("CPU Idle")
                self.current_job = None
            return
        highest_prio_job = self.ready_queue[0]
        if self.current_job is None:
            self.current_job = highest_prio_job
            self._add_log("Execution Started", self.current_job.name)
        elif highest_prio_job.priority < self.current_job.priority:
            self._add_log("Preemption", f"{highest_prio_job.name} preempts {self.current_job.name}")
            self.current_job = highest_prio_job

    def get_log_dataframe(self) -> pd.DataFrame:
        if not self.log: return pd.DataFrame()
        return pd.DataFrame(self.log).set_index("Timestamp")

    def run(self, max_time: int, scenario: Scenario):
        self.scenario = scenario
        self._add_log("Simulation Start", f"Scenario: {scenario.name}, Duration: {max_time}")
        while self.time < max_time:
            self._release_jobs()
            self._scheduler_tick()

            # Record current state for Gantt chart
            job_name = self.current_job.parent_task.name if self.current_job else "Idle"
            job_crit = self.current_job.criticality if self.current_job else "N/A"
            self.execution_history.append((self.time, job_name, job_crit))

            if self.current_job:
                self.current_job.remaining_wcet -= 1
                self.current_job.wcet_lo_budget -= 1
                if self.system_mode == SystemMode.LO and self.current_job.wcet_lo_budget < 0:
                    self.system_mode = SystemMode.HI
                    self._add_log("‼️ CRITICALITY SWITCH ‼️", f"{self.current_job.name} exceeded C(LO) budget!")
                    self._scheduler_tick()
                if self.current_job.remaining_wcet == 0:
                    response_time = (self.time + 1) - self.current_job.arrival_time
                    details = f"{self.current_job.name} (Response Time: {response_time})"
                    if (self.time + 1) > self.current_job.deadline:
                        details += " - 🔥 DEADLINE MISS 🔥"
                    self._add_log("Job Finished", details)
                    heapq.heappop(self.ready_queue)
                    self.current_job = None
            self.time += 1
        self._add_log("Simulation End")