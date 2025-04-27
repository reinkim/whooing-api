# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import re

from .utils import nearest_date, today_kr


fromWeb = '[Web발신]'
pattern = re.compile(r'^\[신한체크승인\]\s+(\S+?)\([0-9]{4}\) '
                    r'([0-9]{2})/([0-9]{2}) [0-9]{2}:[0-9]{2} '
                    r'(\(금액\))?([0-9,]+)원 '
                    r'(.*?)(\s+잔액[0-9,]+원)?$')


class ShdebitParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        # remove a `[Web발신]` prefix, if exists.
        if msg.startswith(fromWeb):
            msg = msg[len(fromWeb):].strip()

        m = pattern.match(msg)
        if not m:
            raise ValueError('invalid message format for 신한체크')

        month = int(m.group(2))
        day = int(m.group(3))
        amount = int(m.group(5).replace(',', ''))
        item = m.group(6).strip()

        return {
            'date': nearest_date(month, day, today_kr()),
            'amount': amount,
            'right': '신한체크',
            'item': item,
            'memo': '',
        }
