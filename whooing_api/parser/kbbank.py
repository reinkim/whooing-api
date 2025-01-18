# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4
import datetime
import re

from .utils import nearest_date, today_kr


fromWeb = '[Web발신]'

patternDate = re.compile(r'\[KB\]([0-9]{2})/([0-9]{2}) [0-9]{2}:[0-9]{2}')


class KbbankParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        msg = msg.strip()
        if msg.startswith(fromWeb):
            msg = msg[len(fromWeb):].strip()

        segments = msg.split('\n')
        if len(segments) < 5: # NOTEI(jinuk): 6번째 줄(잔액) 없을 수 있음.
            raise ValueError('invalid message format for 국민은행')

        m = patternDate.match(segments[0])
        if not m:
            raise ValueError('invalid date format for 국민은행')
        month = int(m.group(1))
        day = int(m.group(2))
        d = nearest_date(month, day, today_kr())

        try:
            amount = int(segments[4].replace(',', '').strip())
        except ValueError:
            raise ValueError('invalid amount format for 국민은행')

        item = segments[2].strip()
        if not item:
            raise ValueError('invalid item format for 국민은행')

        return {
            'date': d,
            'left': '기타',
            'right': '국민은행',
            'item': item,
            'amount': amount,
            'memo': '',
        }
