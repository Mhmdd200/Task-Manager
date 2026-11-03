from enum import StrEnum

class Role(StrEnum):
    OWNER = "owner"
    MEMBER = "member"
    
class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"