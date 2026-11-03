from datetime import datetime, date, time, timezone
from typing import Any, Optional

UTC = timezone.utc

COMMON_DATE_FORMATS = (
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y"
)

def normalize_date(raw_date: Any) -> Optional[str]:
    if not raw_date:
        return None

    parsed: Optional[datetime] = None

    if isinstance(raw_date, datetime):
        parsed = raw_date
    elif isinstance(raw_date, date):
        parsed = datetime.combine(raw_date, time.min)
    elif isinstance(raw_date, str):
        raw = raw_date.strip()
        if not raw:
            return None
        
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass

        if parsed is None:
            for fmt in COMMON_DATE_FORMATS:
                try:
                    parsed = datetime.strptime(raw, fmt)
                    break
                except ValueError:
                    continue

    if parsed is None:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    else:
        parsed = parsed.astimezone(UTC)

    return parsed.isoformat().replace("+00:00", "Z")