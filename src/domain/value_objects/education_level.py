from enum import Enum

class EducationLevel(str, Enum):
    Unspecified = "Unspecified"
    Primary = "Primary"
    Secondary = "Secondary"
    Technical = "Technical"
    University = "University"
    Master = "Master"
    Doctorate = "Doctorate"