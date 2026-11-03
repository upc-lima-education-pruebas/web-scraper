from enum import Enum

class CompensationType(str, Enum):
    Fixed = "Fixed"
    Commission = "Commission"
    Mixed = "Mixed"