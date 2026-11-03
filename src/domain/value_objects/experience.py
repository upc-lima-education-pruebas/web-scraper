from enum import Enum

class Experience(str, Enum):
    NoExperienceNeeded = "NoExperienceNeeded"
    ThreeMonths = "ThreeMonths"
    SixMonths = "SixMonths"
    OneYear = "OneYear"
    TwoOrMoreYears = "TwoOrMoreYears"