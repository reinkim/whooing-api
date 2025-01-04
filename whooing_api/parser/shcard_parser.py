# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
import decimal
import re
from zoneinfo import ZoneInfo

from .utils import nearest_date, today_kr


fromWeb = '[Web발신]'

# for Shinhan Card
patternShcard = re.compile(r'신한(카드)?\([0-9]{4}\)(해외)?승인 \S+')
patternAmountKRW = re.compile(r'([1-9][0-9,]*)원\(일시불\)')
patternAmountUSD = re.compile(r'([1-9][0-9,]*\.[0-9]{1,2}) 달러\s+\([A-Z]{2}\)')
patternDate = re.compile(r'([0-9]{2})/([0-9]{2}) ([0-9]{2}):([0-9]{2})')
patternItem = re.compile(r'(.*?)(\s누적[0-9,]+원)?$')

# 2025년부터 보이는 새 패턴
patternShcardAlt = re.compile(r'신한해외승인 \w+\([0-9]{4}\)')
patternDateAlt = re.compile(r'([0-9]{2})/([0-9]{2}) ([0-9]{2}):([0-9]{2})')
patternAmountUSDAlt = re.compile(r'\S+ ([1-9][0-9,]*\.[0-9]{1,2}) 달러\s+\([A-Z]{2}\)')

# default currency exchange rates
rateUSD2KRW = 1400


class ShcardParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        # remove a `[Web발신]` prefix, if exists.
        if msg.startswith(fromWeb):
            msg = msg[len(fromWeb):]

        memo = ''
        msg = msg.strip()
        m = patternShcard.match(msg)
        if m:
            currencyHint = m.group(2)
        else:
            m = patternShcardAlt.match(msg)
            if not m:
                return None
            return self._parse_alt(msg[len(m.group(0)):].strip())

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
        d = self._get_date(int(m.group(1)), int(m.group(2)))
        msg = msg[len(m.group(0)):].strip()

        m = patternItem.match(msg)
        if not m:
            return None
        item = m.group(1).strip()

        rv = {
            'right': '신한카드',
            'amount': amount,
            'date': d,
            'item': item,
            'memo': memo,
        }
        return rv

    def _parse_alt(self, msg: str):
        m = patternDateAlt.match(msg)
        if not m:
            raise ValueError('invalid date format for 신한카드')
        d = self._get_date(int(m.group(1)), int(m.group(2)))
        msg = msg[len(m.group(0)):].strip()

        m = patternAmountUSD.match(msg)
        if not m:
            raise ValueError('invalid amount format for 신한카드')
        # no strict validation for thousand separtors
        value = decimal.Decimal(value=m.group(1))
        amount = int(value * rateUSD2KRW)
        memo = f'TBD, USD {value}'
        msg = msg[len(m.group(0)):].strip()

        m = patternItem.match(msg)
        if not m:
            return None
        item = m.group(1).strip()

        return {
            'right': '신한카드',
            'amount': amount,
            'date': d,
            'item': item,
            'memo': memo,
        }

    def _get_date(self, month, day):
        # NOTE(jinuk): it's error prone to use the snippet, but we don't have a
        # precise method to get a year, as it's not available from received
        # messages.
        today = today_kr()
        d = nearest_date(month, day, today)
        return d
