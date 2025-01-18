import re

from .utils import nearest_date, today_kr


fromWeb = '[Web발신]'

# for Shinhan Card
patternAmount = re.compile(r'([1-9][0-9,]*)원 일시불')
patternDate = re.compile(r'([0-9]{2})/([0-9]{2}) ([0-9]{2}):([0-9]{2})')


class HdcardParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        if msg.startswith(fromWeb):
            msg = msg[len(fromWeb):].strip()

        segments = [s.strip() for s in msg.split('\n')]

        m = patternAmount.match(segments[2])
        if not m:
            raise ValueError('invalid amount format for 현대카드 ')
        amount = int(m.group(1).strip().replace(',', ''))

        m = patternDate.match(segments[3])
        if not m:
            raise ValueError('invalid date format for 현대카드 ')
        month = int(m.group(1))
        day = int(m.group(2))
        d = nearest_date(month, day, today_kr())

        item = segments[4]

        return {
            'date': d,
            'left': '기타',
            'right': '현대카드',
            'amount': amount,
            'item': item,
            'memo': '',
        }
