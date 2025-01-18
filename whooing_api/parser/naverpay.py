# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
import re


dtFormat = '%Y.%m.%d'

patternItem = re.compile(r'결제처\s+(.+?)\s상품정보', re.UNICODE)
patternItem2 = re.compile(r'가맹점명\s+(.+?)\s총 결제 금액', re.UNICODE)
patternItem3= re.compile(r'주문상품\s+(.+?)\s+(옵션|주문금액)', re.UNICODE)

patternProduct= re.compile(r'상품정보\s+(.+?)\s결제상세', re.UNICODE)

patternDate = re.compile(r'(결제일자|주문일자)\s+(\d{4}\.\d{2}\.\d{2})', re.UNICODE)

patternAmount = re.compile(r'최종결제금액\s+([\d,]+)원?')
patternAmountAlt = re.compile(r'주문금액\s+([\d,]+)원?')


def _sanitize(s: str) -> str:
    return s.replace('\uFFFC', '').strip()


class NaverpayParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        msg = _sanitize(msg)

        # item
        item = ''
        for p in (patternItem, patternItem2, patternItem3):
            m = re.search(p, msg)
            if not m:
                continue
            item = m.group(1).strip()
            break

        if not item:
            raise ValueError('invalid item for 네이버페이')

        # date
        d = None
        m = re.search(patternDate, msg)
        if not m:
            raise ValueError('invalid date for 네이버페이')
        d = datetime.datetime.strptime(m.group(2), dtFormat).date()

        # amount
        amount = 0
        for p in (patternAmount, patternAmountAlt):
            m = re.search(p, msg)
            if m:
                amount = int(m.group(1).replace(',', ''))
                break
        if not m:
            raise ValueError('invalid amount for 네이버페이')

        # memo
        memo = ''
        m = re.search(patternProduct, msg)
        if m:
            memo = m.group(1).strip()

        return {
            'date': d,
            'amount': amount,
            'left': '기타',
            'right': '네이버페이',
            'item': item,
            'memo': memo,
        }
