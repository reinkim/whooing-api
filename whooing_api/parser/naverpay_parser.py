# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime


dtFormat = '%Y.%m.%d'


def _sanitize(s: str) -> str:
    return s.replace('\uFFFC', '').strip()

class NaverpayParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        rows = [_sanitize(l) for l in msg.split('\n')]
        rows = [l for l in rows if l]

        item = ''
        memo = ''
        d = None
        amount = 0
        i = 0

        while i < len(rows) - 1:
            match rows[i]:
                case '결제처' | '가맹점명' | '주문상품':
                    if not item:
                        item = rows[i+1]
                    i += 1
                case '결제일자' | '주문일자':
                    d = datetime.datetime.strptime(rows[i+1].split(' ')[0], dtFormat).date()
                    i += 1
                case '상품정보':
                    memo = rows[i+1]
                    i += 1
                case '최종결제금액' | '주문금액':
                    amountStr = rows[i+1].replace(',', '')
                    if amountStr.endswith('원'):
                        amountStr = amountStr[:-1]
                    amount = int(amountStr)
                    i += 1
            i += 1

        return {
            'date': d,
            'amount': amount,
            'left': '기타',
            'right': '네이버페이',
            'item': item,
            'memo': memo,
        }
