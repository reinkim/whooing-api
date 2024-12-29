import datetime

from .shcard_parser import ShcardParser


# choose nearest datetime from [(prev year, month, day), (this year, ...)]
def nearest_date(d: datetime.date, today: datetime.date) -> datetime.date:
    try:
        prev = d.replace(year=d.year-1)
    except ValueError: # leap year
        return d

    distPrev= abs((prev - today).days)
    distCurr = abs((today - d).days)
    return prev if distPrev < distCurr else d
