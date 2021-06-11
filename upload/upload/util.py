from datetime import datetime
from dateutil.tz import tzlocal


def now():
    return str(datetime.now(tz=tzlocal()).isoformat())
