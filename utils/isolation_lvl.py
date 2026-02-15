from enum import StrEnum

class IsolationLvl(StrEnum):
    serializable = "serializable"
    repeatable_read = "repeatable_read"
    read_uncommitted = "read_uncommitted"
    read_committed = "read_committed"