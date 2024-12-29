# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import pytest

import whooing_api
import whooing_api.api
from whooing_api.category_table import CategoryTable, ItemMapping


table = CategoryTable([
    ItemMapping(name='이케아코리아', spend_type='주거', display_name='이케아'),
])


def test_spend_shcard():
    app = whooing_api.api.app
    app.category_table = table
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
