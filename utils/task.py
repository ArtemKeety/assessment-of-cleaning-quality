from enum import Enum


class TaskCondition(str, Enum):
    success = "SUCCESS"
    failure = "FAILURE"