# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
import itertools
import re

from bs4 import BeautifulSoup


subTablePattern = re.compile(r'\s*주문상품\s*')
amountPattern = re.compile(r'\s*최종결제금액\s*')


class NaverpayParser:
    def __init__(self):
        pass

    def parse(self, msg: str):
        soup = BeautifulSoup(msg, 'html.parser')
        try:
            return self._parse_naver_pay(soup)
        except:
            pass

        try:
            return self._parse_naver_shopping(soup)
        except:
            pass

        return ValueError('invalid message format for 네이버페이')

    def _parse_naver_pay(self, soup: BeautifulSoup):
        # read the text of the next `td` element.
        def readNextTd(td):
            parent = td.parent
            nextTd = parent.find_all('td')[1]
            return nextTd.text.strip()

        item = ''
        memo = ''

        # `td` elements with width=70 or width=50% have most of the information.
        for td in itertools.chain(soup.find_all('td', width='70'),
                                  soup.find_all('td', width='50%')):
            field = td.text.strip()

            match field:
                case '결제일자':
                    try:
                        dstr = readNextTd(td).split(' ')[0]
                        d = datetime.datetime.strptime(dstr, '%Y.%m.%d').date()
                    except:
                        raise ValueError('invalid date format for 네이버페이')
                case '결제처' | '가맹점명':
                    item = readNextTd(td)
                case '상품정보':
                    memo = readNextTd(td)

        if item == '':
            raise ValueError('invalid item format for 네이버페이')

        amount = 0
        td = soup.find(string=amountPattern).parent
        if td:
            p = td.parent.find_all('td')[1].find('span')
            amount = int(p.text.strip().replace(',', ''))

        if amount == 0:
            raise ValueError('invalid amount for 네이버페이')

        return {
            'date': d,
            'left': '기타',
            'right': '네이버페이',
            'item': item,
            'amount': amount,
            'memo': memo,
        }

    def _parse_naver_shopping(self, soup: BeautifulSoup):
        # read the text of the next `td` element.
        def readNextTd(td):
            parent = td.parent
            nextTd = parent.find_all('td')[1]
            return nextTd.text.strip()

        memo = ''

        amount = 0
        p = soup.find('td', {'width': '45%'})
        amountStr = readNextTd(p)
        if amountStr.endswith('원'):
            amountStr = amountStr[:-1]
        amount = int(amountStr.replace(',', ''))
        if amount == 0:
            raise ValueError('invalid amount for 네이버페이')

        # item name
        item = ''
        p = soup.find_all(string=subTablePattern)[-1]
        subTbl = p.parent.parent.parent.find('table')
        try:
            item = subTbl.find('table').find('tr').find('td').text.strip()
        except:
            item = ''
        if item == '':
            raise ValueError('invalid item format for 네이버페이')

        for td in soup.find_all('td', width='70'):
            if td.text.strip() == '주문일자':
                try:
                    dstr = readNextTd(td)
                    d = datetime.datetime.strptime(dstr, '%Y.%m.%d').date()
                except:
                    raise ValueError('invalid date format for 네이버페이')
                break

        return {
            'date': d,
            'left': '기타',
            'right': '네이버페이',
            'item': item,
            'amount': amount,
            'memo': memo,
        }
