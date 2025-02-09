# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
from zoneinfo import ZoneInfo

import pytest

import whooing_api
import whooing_api.parser
from whooing_api.parser.utils import nearest_date, today_kr

from whooing_api.parser.shcard import *


@pytest.mark.parametrize(
    'test_input,expected', [
        pytest.param(
            '[Web발신]\n신한카드(3456)승인 김*수 13,500원(일시불)11/28 13:24 Apple 누적1,234,456원',
            {
                'date': datetime.date(2024, 11, 28),
                'amount': 13500,
                'right': '신한카드',
                'item': 'Apple',
                'memo': '',
            },
            id='base case'
        ),
        pytest.param(
            '[Web발신]\n신한카드(1234)승인 최*희 47,450원(일시불)11/27 12:36 네이버페이',
            {
                'date': datetime.date(2024, 11, 27),
                'amount': 47450,
                'right': '신한카드',
                'item': '네이버페이',
                'memo': '',
            },
            id='authorized user card'
        ),
        pytest.param(
            '''[Web발신]
신한해외승인 홍길*(1234) 02/04 10:48
86.40 달러 (US)AMZN Mktp US''',
            {
                'date': datetime.date(2025, 2, 4),
                'amount': int(1400 * 86.40),
                'right': '신한카드',
                'item': 'AMZN Mktp US',
                'memo': 'TBD, USD 86.40',
            },
            id='USD, US'
        ),
        pytest.param(
            '''[Web발신]
신한해외승인 김철*(1111) 01/01 18:05
9.66 달러 (NL)DIGITALOCEAN.COM''',
            {
                'date': datetime.date(2025, 1, 1),
                'amount': int(1400 * 9.66),
                'right': '신한카드',
                'item': 'DIGITALOCEAN.COM',
                'memo': 'TBD, USD 9.66',
            },
            id='USD, NL'
        ),
        pytest.param(
            '''[Web발신]
신한해외승인 김*수(4321) 01/28 20:03
KRW 53,800 (US)DNH*GODADDY#35512655''',
            {
                'date': datetime.date(2025, 1, 28),
                'amount': 53800,
                'right': '신한카드',
                'item': 'DNH*GODADDY#35512655',
                'memo': '',
            },
            id='KRW, US',
        ),
        pytest.param(
            '''[Web발신]
신한카드(1224)취소 김*수 39,860원(일시불)01/02 18:15 이마트''',
            {
                'date': datetime.date(2025, 1, 2),
                'amount': -39860,
                'right': '신한카드',
                'item': '이마트',
                'memo': '취소',
            },
            id='cancel'
        ),
        pytest.param(
            '''[Web발신]
신한카드(3333)승인 김*수님 아파트 관리비  400,000원 정상승인 되었습니다.''',
            {
                'date': today_kr(),
                'amount': 400000,
                'right': '신한카드',
                'item': '아파트 관리비',
                'memo': '',
            },
            id='Apt'
        ),
    ])


def test_shcard(test_input, expected):
    parser = ShcardParser()
    actual = parser.parse(test_input)
    assert expected == actual


# 체크카드
def test_shdebit():
    parser = whooing_api.parser.ShdebitParser()

    example0 = '''[Web발신]
[신한체크승인] 홍길*(1231) 10/20 00:23 28,600원 카카오T일반택  잔액12,345,678원'''

    v = parser.parse(example0)

    expected = {
        'date': datetime.date(2024, 10, 20),
        'amount': 28600,
        'right': '신한체크',
        'item': '카카오T일반택',
        'memo': '',
    }
    assert expected == v
