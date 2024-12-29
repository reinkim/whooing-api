# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
from zoneinfo import ZoneInfo

import whooing_api
import whooing_api.parser
from whooing_api.parser.utils import nearest_date


# 신한은행
def test_shbank():
    parser = whooing_api.parser.ShbankParser()

    # 카드대금
    example0 = '''[Web발신]
신한12/26 18:52
123-456-789012
출금     650,000
잔액 12,345,678
 현대카드(주)'''

    v = parser.parse(example0)
    expected = {
        'date': datetime.date(2024, 12, 26),
        'amount': 650000,
        'left': '기타',
        'right': '신한은행',
        'item': '현대카드(주)',
        'memo': '',
    }
    assert expected == v


# 신한카드
def test_shcard_krw():
    parser = whooing_api.parser.ShcardParser()

    # 본인 카드
    krwExample0 = '''[Web발신]
신한카드(3456)승인 김*수 13,500원(일시불)11/28 13:24 Apple 누적1,234,456원'''
    v = parser.parse(krwExample0)
    expected = {
        'date': datetime.date(2024, 11, 28),
        'amount': 13500,
        'right': '신한카드',
        'item': 'Apple',
        'memo': '',
    }
    assert expected == v

    # 가족 카드
    krwExample1 = '''[Web발신]
신한카드(1234)승인 최*희 47,450원(일시불)11/27 12:36 네이버페이'''
    v = parser.parse(krwExample1)
    expected = {
        'date': datetime.date(2024, 11, 27),
        'amount': 47450,
        'right': '신한카드',
        'item': '네이버페이',
        'memo': '',
    }
    assert expected == v

def test_shcard_usd():
    parser = whooing_api.parser.ShcardParser()

    # USD, NL
    usdExample0 = '''[Web발신]
신한(7890)해외승인 홍*동 9.66 달러        (NL)12/01 15:42 DIGITALOCE 누적1,234,456원'''
    v = parser.parse(usdExample0)
    expected = {
        'date': datetime.date(2024, 12, 1),
        'amount': int(1400 * 9.66),
        'right': '신한카드',
        'item': 'DIGITALOCE',
        'memo': 'TBD, USD 9.66',
    }
    assert expected == v

    # USD, US
    usdExample1 = '''[Web발신]
신한(2345)해외승인 김철* 70.64 달러       (US)11/21 12:39 SEA CREATU 누적1,234,567원'''
    v = parser.parse(usdExample1)
    expected = {
        'date': datetime.date(2024, 11, 21),
        'amount': int(1400 * 70.64),
        'right': '신한카드',
        'item': 'SEA CREATU',
        'memo': 'TBD, USD 70.64',
    }
    assert expected == v

def test_nearest_date():
    today = datetime.date(2024, 1, 2)

    assert nearest_date(12, 29, today) == datetime.date(2023, 12, 29)
    assert nearest_date(1, 2, today) == datetime.date(2024, 1, 2)

    # 2024-02-29 is valid, but 2023-02-29 is not.
    assert nearest_date(2, 29, today) == datetime.date(2024, 2, 29)

    today = datetime.date(2025, 3, 1)
    assert nearest_date(2, 29, today) == datetime.date(2024, 2, 29)

# TODO: 취소, 해외승인?, 체크카드, 아파트 관리비 승인


def test_kbbank():
    parser = whooing_api.parser.KbbankParser()

    example0 = '''[Web발신]
[KB]12/19 09:45
112233**455
KB카드출금
카드출금(
123,400
잔액10,000,000'''
    v = parser.parse(example0)
    assert v == {
        'date': datetime.date(2024, 12, 19),
        'amount': 123400,
        'left': '기타',
        'right': '국민은행',
        'item': 'KB카드출금',
        'memo': '',
    }
