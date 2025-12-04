from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(int, Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3
