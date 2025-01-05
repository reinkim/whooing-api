# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4
"""app_test tests against FastAPI app that wraps whooing API."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import pytest

import whooing_api
import whooing_api.api
from whooing_api.category_table import CategoryTable, ItemMapping


table = CategoryTable([
    ItemMapping(name='이케아코리아', spend_type='주거', display_name='이케아'),
    ItemMapping(name='신한카드', spend_type='신한카드', display_name='카드대금(신한)'),
    ItemMapping(name='네이버페이충전', spend_type='네이버페이', display_name='네이버페이 충전'),
    ItemMapping(name='KB카드출금', spend_type='국민카드', display_name='카드대금(국민)'),
])


def test_spend_shcard():
    app = whooing_api.api.app
    app.lookup_table = table
    app.client.spend = AsyncMock(return_value='done')

    client = TestClient(app)

    msg = '[Web발신]신한(1234)승인 최*희 40,000원(일시불)12/25 12:34 이케아코리아'
    res = client.post('/whooing/shcard/', json={'message': msg})
    assert res.json() == {'status': 'done'}

    expected = whooing_api.whooing.WhooingEntry(
        entry_date='20241225',
        item='이케아',
        left='주거',
        right='신한카드',
        money=40000,
        memo='')
    app.client.spend.assert_called_once_with(expected)


def test_spend_shbank():
    app = whooing_api.api.app
    app.lookup_table = table

    client = TestClient(app)

    app.client.spend = AsyncMock(return_value='done')
    msg = '''[Web발신]
신한12/26 18:01
123-123-123456
출금   100,000
잔액 500
 신한카드'''
    res = client.post('/whooing/shbank/', json={'message': msg})
    assert res.json() == {'status': 'done'}

    expected = whooing_api.whooing.WhooingEntry(
        entry_date='20241226',
        item='카드대금(신한)',
        left='신한카드',
        right='신한은행',
        money=100000,
        memo='')
    app.client.spend.assert_called_once_with(expected)

    app.client.spend = AsyncMock(return_value='done')
    msg = '''[Web발신]
신한12/26 18:01
123-123-123456
출금   100,000
잔액 500
 네이버페이충전'''
    res = client.post('/whooing/shbank/', json={'message': msg})
    assert res.json() == {'status': 'done'}

    expected = whooing_api.whooing.WhooingEntry(
        entry_date='20241226',
        item='네이버페이 충전',
        left='네이버페이',
        right='신한은행',
        money=100000,
        memo='')
    app.client.spend.assert_called_once_with(expected)

    app.client.spend = AsyncMock(return_value='done')
    msg = '''[Web발신]
신한01/04 15:10
123-456-789012
입금     100,166
잔액 12,345,678
 화수분'''
    res = client.post('/whooing/shbank/', json={'message': msg})
    assert res.json() == {'status': 'done'}

    expected = whooing_api.whooing.WhooingEntry(
        entry_date='20250104',
        item='입금(미분류,화수분)',
        left='신한은행',
        right='기타수익',
        money=100166,
        memo='TBD: 입금 화수분')
    app.client.spend.assert_called_once_with(expected)


def test_spend_kbbank():
    app = whooing_api.api.app
    app.lookup_table = table

    client = TestClient(app)

    app.client.spend = AsyncMock(return_value='done')
    msg = '''[Web발신]
[KB]12/19 09:45
112233**455
KB카드출금
카드출금(
123,400
잔액10,000,000'''
    res = client.post('/whooing/kbbank/', json={'message': msg})

    expected = whooing_api.whooing.WhooingEntry(
        entry_date='20241219',
        item='카드대금(국민)',
        left='국민카드',
        right='국민은행',
        money=123400,
        memo='')
    app.client.spend.assert_called_once_with(expected)
