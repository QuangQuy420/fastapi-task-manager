from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(int, Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


# Project
class UserRole(str, Enum):
    OWNER = "owner"
    MAINTAINER = "maintainer"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectHistoryAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    ADJUST_MEMBER = "adjust_member"