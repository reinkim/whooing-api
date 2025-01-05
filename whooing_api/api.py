# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from typing import Optional

from pydantic import BaseModel
from fastapi import FastAPI

from .parser import new_parser
from .category_table import CategoryTable
from .whooing import Client, WhooingEntry
from .utils import init_sentry, get_settings, get_rules, get_webhook_url


init_sentry()

app = FastAPI()
app.client = Client(get_settings().whooing_token.get_secret_value())
app.lookup_table = CategoryTable(get_rules(get_settings().rules))


class SMSMessage(BaseModel):
    message: str


def to_whooing_entry(parsed):
    dt = parsed['date'].strftime('%Y%m%d') if parsed['date'] else ''

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
    parser = new_parser(method)
    if not parser:
        return {'status': 'invalid method'}

    parsed = parser.parse(msg.message)
    if not parsed:
        # NOTE: fallback to send a message to the webhook on whooing.
        resp = await app.client.whooing_fallback(msg.message)
        return {'status': resp}

    # try to apply predefined rules
    cat, name = app.lookup_table.lookup(parsed['item'])
    if cat != '' and name != '':
        parsed['left'] = cat
        parsed['item'] = name
        if '미분류' in name and parsed['memo'] == '':
            parsed['memo'] = 'TBD: 재분류'
    else:
        if not parsed['left']:
            parsed['left'] = '기타'
        if not parsed['memo']:
            parsed['memo'] = 'TBD: 재분류'

    we = to_whooing_entry(parsed)
    resp = await app.client.spend(we)
    return {'status': resp}
