from enum import Enum

class JobType(str, Enum):
    Remote = "Remote"
    Hybrid = "Hybrid"
    InPerson = "InPerson"