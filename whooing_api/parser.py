#!/usr/bin/env python3
# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
import decimal
import re
from zoneinfo import ZoneInfo

fromWeb = '[Web발신]'

# for Shinhan Card
patternShcard = re.compile(r'신한(카드)?\([0-9]{4}\)(해외)?승인')
patternAmountKRW = re.compile(r'\S+ ([1-9][0-9,]*)원\(일시불\)')
patternAmountUSD = re.compile(r'\S+ ([1-9][0-9,]*\.[0-9]{1,2}) 달러\s+\([A-Z]{2}\)')
patternDate = re.compile(r'([0-9]{2})/([0-9]{2}) ([0-9]{2}):([0-9]{2})')
patternItem = re.compile(r'(.*?)(\s누적[0-9,]+원)?$')

# default currency exchange rates
rateUSD2KRW = 1400

# default timezone
tzSeoul = ZoneInfo('Asia/Seoul')


class Parser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        # remove a `[Web발신]` prefix, if exists.
        if msg.startswith(fromWeb):
            msg = msg[len(fromWeb):]

        memo = ''
        msg = msg.strip()
        m = patternShcard.match(msg)
        if not m:
            return None

        right = '신한카드'
        currencyHint = m.group(2)
        msg = msg[len(m.group(0)):].strip()

        if currencyHint == '해외':
            m = patternAmountUSD.match(msg)
            if not m:
                return None
            # no strict validation for thousand separtors
            value = decimal.Decimal(value=m.group(1))
            amount = int(value * rateUSD2KRW)
            memo = f'TBD, USD {value}'
        else: # KRW
            m = patternAmountKRW.match(msg)
            if not m:
                return None
            # no strict validation for thousand separtors
            amount = int(m.group(1).replace(',', ''))

        msg = msg[len(m.group(0)):].strip()
        m = patternDate.match(msg)
        if not m:
            return None

        # NOTE(jinuk): it's error prone to use the snippet, but we don't have a
        # precise method to get a year, as it's not available from received
        # messages.
        today = datetime.datetime.now(tz=tzSeoul).date()
        d = datetime.date(year=today.year, month=int(m.group(1)), day=int(m.group(2)))
        d = nearest_date(d, today)

        msg = msg[len(m.group(0)):].strip()
        m = patternItem.match(msg)
        if not m:
            return None
        item = m.group(1).strip()

        rv = {
            'right': right,
            'amount': amount,
            'date': d,
            'item': item,
            'memo': memo,
        }
        return rv

# choose nearest datetime from [(prev year, month, day), (this year, ...)]
def nearest_date(d: datetime.date, today: datetime.date) -> datetime.date:
    try:
        prev = d.replace(year=d.year-1)
    except ValueError: # leap year
        return d

    distPrev= abs((prev - today).days)
    distCurr = abs((today - d).days)
    return prev if distPrev < distCurr else d
