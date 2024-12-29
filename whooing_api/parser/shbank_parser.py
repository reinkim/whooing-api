# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4
import datetime
import re

from .utils import nearest_date, today_kr


fromWeb = '[Web발신]'

# 신한은행 형식
patternDate = re.compile(r'신한([0-9]{2})/([0-9]{2}) [0-9]{2}:[0-9]{2}')
patternAmount = re.compile(r'출금\s+([0-9,]+)')


class ShbankParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        msg = msg.strip()
        if msg.startswith(fromWeb):
            msg = msg[len(fromWeb):].strip()

        segments = msg.split('\n')
        if len(segments) != 5:
            raise ValueError('invalid message format for 신한은행')

        m = patternDate.match(segments[0])
        if not m:
            raise ValueError('invalid date format for 신한은행')
        month = int(m.group(1))
        day = int(m.group(2))
        d = nearest_date(month, day, today_kr())

        m = patternAmount.match(segments[2])
        if not m:
            raise ValueError('invalid amount format for 신한은행')
        amount = int(m.group(1).replace(',', ''))

        item = segments[4].strip()
        if not item:
            raise ValueError('invalid item format for 신한은행')

        return {
            'date': d,
            'left': '기타',
            'right': '신한은행',
            'item': item,
            'amount': amount,
            'memo': '',
        }