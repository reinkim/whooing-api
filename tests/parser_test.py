# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

import datetime
from zoneinfo import ZoneInfo

import whooing_api
import whooing_api.parser
from whooing_api.parser.utils import nearest_date, today_kr


def test_nearest_date():
    today = datetime.date(2024, 1, 2)

    assert nearest_date(12, 29, today) == datetime.date(2023, 12, 29)
    assert nearest_date(1, 2, today) == datetime.date(2024, 1, 2)

    # 2024-02-29 is valid, but 2023-02-29 is not.
    assert nearest_date(2, 29, today) == datetime.date(2024, 2, 29)

    today = datetime.date(2025, 3, 1)
    assert nearest_date(2, 29, today) == datetime.date(2024, 2, 29)


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

    # 입금
    example1 = '''[Web발신]
신한01/04 15:10
123-456-789012
입금     100,166
잔액 12,345,678
 화수분'''
    v = parser.parse(example1)
    expected = {
        'date': datetime.date(2025, 1, 4),
        'amount': 100166,
        'left': '신한은행',
        'right': '기타수익',
        'item': '입금(미분류,화수분)',
        'memo': 'TBD: 입금 화수분',
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

    # USD, NL (2025)
    usdExample2 = '''[Web발신]
신한해외승인 김철수(1111) 01/01 18:05
9.66 달러 (NL)DIGITALOCEAN.COM'''
    v = parser.parse(usdExample2)
    expected = {
        'date': datetime.date(2025, 1, 1),
        'amount': int(1400 * 9.66),
        'right': '신한카드',
        'item': 'DIGITALOCEAN.COM',
        'memo': 'TBD, USD 9.66',
    }
    assert expected == v

# TODO: 처리 안할 단어 목록
# [신한카드] 해외결제 유의사항 안내
# [신한카드]해외원화결제시 추가수수료가 부과되므로 현지통화 거래가 유리합니다.
# [신한카드] 원화결제차단 서비스신청
def test_shcard_cancel():
    parser = whooing_api.parser.ShcardParser()

    example0 = '''[Web발신]
신한카드(1224)취소 김*수 39,860원(일시불)01/02 18:15 이마트'''
    v = parser.parse(example0)

    expected = {
        'date': datetime.date(2025, 1, 2),
        'amount': -39860,
        'right': '신한카드',
        'item': '이마트',
        'memo': '취소',
    }
    assert expected == v


def test_shcard_apt():
    parser = whooing_api.parser.ShcardParser()

    example = '''[Web발신]
신한카드(3333)승인 김*수님 아파트 관리비  400,000원 정상승인 되었습니다.'''
    v = parser.parse(example)

    expected = {
        'date': today_kr(),
        'amount': 400000,
        'right': '신한카드',
        'item': '아파트 관리비',
        'memo': '',
    }
    assert expected == v


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


def read_utf16_file(filepath):
    with open(filepath, 'rb') as f:
        return f.read().decode('utf-16le').replace('\n', ' ')


def test_naverpay():
    # 네이버페이 일반결제
    parser = whooing_api.parser.NaverpayParser()

    msg = read_utf16_file('tests/fixtures/naverpay-aladin.txt')
    v = parser.parse(msg)

    assert v == {
        'date': datetime.date(2024, 12, 27),
        'amount': 55030,
        'left': '기타',
        'right': '네이버페이',
        'item': '알라딘 커뮤니케이션',
        'memo': '괴도 세인트 테일 : 천사소녀 네티 1~4 애장판 박스 세트 - 전4권 외 1건',
    }

    # 네이버페이 일반결제 (카드)
    msg = read_utf16_file('tests/fixtures/naverpay-bus.txt')
    v = parser.parse(msg)

    assert v == {
        'date': datetime.date(2024, 11, 24),
        'amount': 11900,
        'left': '기타',
        'right': '네이버페이',
        'item': '버스타고',
        'memo': '[11/24(일), 시외우등] 인천공항T2(12:34) - 서현역',
    }

    # 네이버페이 일반결제 (지방세, 카드)
    msg = read_utf16_file('tests/fixtures/naverpay-wetax.txt')
    v = parser.parse(msg)

    assert v == {
        'date': datetime.date(2024, 9, 15),
        'amount': 200000,
        'left': '기타',
        'right': '네이버페이',
        'item': '금융결제원 인터넷지로',
        'memo': '위택스',
    }


def test_naverpay_shopping():
    # 네이버쇼핑
    parser = whooing_api.parser.NaverpayParser()

    msg = read_utf16_file('tests/fixtures/naverpay-shopping.txt')
    v = parser.parse(msg)

    assert v == {
        'date': datetime.date(2024, 12, 20),
        'amount': 13400,
        'left': '기타',
        'right': '네이버페이',
        'item': 'Foo Bar',
        'memo': '',
    }


def test_naverpay_offline():
    # 오프라인 결제
    parser = whooing_api.parser.NaverpayParser()

    msg = read_utf16_file('tests/fixtures/naverpay-gs25.txt')
    v = parser.parse(msg)

    assert v == {
        'date': datetime.date(2024, 12, 18),
        'amount': 1400,
        'left': '기타',
        'right': '네이버페이',
        'item': 'GS25 대통령실점',
        'memo': '',
    }


def test_hdcard():
    parser = whooing_api.parser.HdcardParser()
    msg = '''[Web발신]
현대카드 ZERO 승인
홍*동
300,123원 일시불
01/14 12:08
코스트코코리아'''
    v = parser.parse(msg)

    assert v == {
        'date': datetime.date(2025, 1, 14),
        'amount': 300123,
        'left': '기타',
        'right': '현대카드',
        'item': '코스트코코리아',
        'memo': '',
    }
