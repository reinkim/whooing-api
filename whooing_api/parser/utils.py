# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
from zoneinfo import ZoneInfo


# default timezone
tzSeoul = ZoneInfo('Asia/Seoul')


def today_kr():
    return datetime.datetime.now(tz=tzSeoul).date()


# choose nearest datetime from [(prev year, month, day), (this year, ...)]
def nearest_date(mon: int, day_of_month: int, today: datetime.date) -> datetime.date:
    try:
        d = datetime.date(today.year, mon, day_of_month)
    except ValueError:
        return datetime.date(today.year-1, mon, day_of_month)

    try:
        prev = d.replace(year=d.year-1)
    except ValueError: # leap year
        return d

    distPrev= abs((prev - today).days)
    distCurr = abs((today - d).days)
    return prev if distPrev < distCurr else d
