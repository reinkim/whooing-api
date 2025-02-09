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
