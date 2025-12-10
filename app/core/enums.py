from enum import Enum


# Entity Types
class EntityEnum(str, Enum):
    Entity = "Entity"
    TASK = "Task"
    PROJECT = "Project"
    SPRINT = "Sprint"


# Task
class TaskStatus(str, Enum):
    NEW = "new"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    IN_TESTING = "in_testing"
    DONE = "done"
    ACHIEVED = "achieved"


class TaskPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


# User Roles - for Project Members
class UserRole(str, Enum):
    OWNER = "owner"
    MAINTAINER = "maintainer"
    MEMBER = "member"
    VIEWER = "viewer"


# Project
class ProjectStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


# History Actions
class HistoryAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ADJUST_MEMBER = "adjust_member"


# Sprint
class SprintStatus(str, Enum):
    NEW = "new"
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


# Sort - Filter - Pagination
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ProjectSortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"
    STATUS = "status"
