#!/usr/bin/env python3
# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
from zoneinfo import ZoneInfo

import whooing_api
import whooing_api.parser


def test_shcard_krw():
    parser = whooing_api.ShcardParser()

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
    parser = whooing_api.ShcardParser()

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
    d = datetime.date(2024, 12, 29)
    d2 = datetime.date(2023, 12, 29)

    assert d2 == whooing_api.parser.nearest_date(d, today)

    d = datetime.date(2024, 1, 1)
    assert d == whooing_api.parser.nearest_date(d, today)

    # 2024-02-29 is valid, but 2023-02-29 is not.
    d = datetime.date(2024, 2, 29)
    assert d == whooing_api.parser.nearest_date(d, today)

# TODO: 취소, 해외승인?, 체크카드, 아파트 관리비 승인
