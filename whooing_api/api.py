# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from typing import Optional

import aiohttp
from pydantic import BaseModel
from fastapi import FastAPI

from .parser import Parser
from .category_table import CategoryTable
from .utils import init_sentry, get_settings, get_rules, get_webhook_url


init_sentry()
app = FastAPI()

lookup_table = CategoryTable(get_rules(get_settings().rules))


class SMSMessage(BaseModel):
    message: str


class WhooingEntry(BaseModel):
    # a data model for Whooing API
    # Please note that this should be posted as x-www-form-urlencoded.
    entry_date: str # TODO(jinuk): proper validation for yyyymmdd
    item: str
    left: str
    right: str
    money: int
    memo: Optional[str] = ''


def to_whooing_entry(parsed):
    dt = parsed['date'].strftime('%Y%m%d')

    return WhooingEntry(entry_date=dt,
                        item=parsed['item'],
                        left=parsed['left'],
                        right=parsed['right'],
                        money=parsed['amount'],
                        memo=parsed['memo'])


@app.get('/')
async def index():
    return {'status': 'ok'}


@app.post('/whooing/{method}/')
async def payment(method: str, msg: SMSMessage):
    parser = Parser()
    parsed = parser.parse(msg.message)

    if not parsed:
        # TODO: fallback to send a message to the webhook on whooing.
        resp = await whooing_fallback(msg.message)
        return {'status': resp}

    # try to apply predefined rules
    cat, name = lookup_table.lookup(parsed['item'])
    if cat != '' and name != '':
        parsed['left'] = cat
        parsed['item'] = name
        if '미분류' in name:
            parsed['memo'] = 'TBD: 재분류'
    else:
        parsed['left'] = '기타'
        parsed['memo'] = 'TBD: 재분류'

    we = to_whooing_entry(parsed)
    resp = await whooing_spend(we)
    return {'status': resp}


async def whooing_spend(entry: WhooingEntry):
    webhook = get_webhook_url()
    data = entry.model_dump(exclude_none=True)

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook, data=data) as resp:
            resp.raise_for_status()
            return await resp.text()


async def whooing_fallback(msg: str):
    webhook = get_webhook_url()

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook, json={'message': msg}) as resp:
            resp.raise_for_status()
            return await resp.text()
