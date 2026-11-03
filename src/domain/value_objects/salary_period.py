from enum import Enum

class SalaryPeriod(str, Enum):
    Daily = "Daily"
    Weekly = "Weekly"
    Fortnightly = "Fortnightly"
    Monthly = "Monthly"
    ForFees = "ForFees"