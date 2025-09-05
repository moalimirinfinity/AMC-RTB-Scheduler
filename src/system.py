from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Task:
    """Represents a mixed-criticality sporadic task."""
    id: int
    name: str
    period: int
    deadline: int
    wcet_lo: int
    wcet_hi: Optional[int]
    criticality: str
    priority: int

@dataclass(order=True)
class Job:
    """Represents a single instance (arrival) of a task."""
    priority: int = field(init=False)
    arrival_time: int
    deadline: int
    remaining_wcet: int
    wcet_lo_budget: int
    parent_task: Task = field(compare=False)
    
    def __post_init__(self):
        self.priority = self.parent_task.priority

    @property
    def name(self):
        return f"{self.parent_task.name}_Job@{self.arrival_time}"

    @property
    def criticality(self):
        return self.parent_task.criticality

