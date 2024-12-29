# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from typing import Optional

import aiohttp
from pydantic import BaseModel


class WhooingEntry(BaseModel):
    # a data model for Whooing API
    # Please note that this should be posted as x-www-form-urlencoded.
    entry_date: str # TODO(jinuk): proper validation for yyyymmdd
    item: str
    left: str
    right: str
    money: int
    memo: Optional[str] = ''


class Client:
    def __init__(self, token):
        self.webhook = f'https://whooing.com/webhook/s/{token}/'

    async def spend(self, entry):
        data = entry.model_dump(exclude_none=True)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook, data=data) as resp:
                resp.raise_for_status()
                return await resp.text()

    async def whooing_fallback(self, msg: str):
        m = {'message': msg}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook, json=m) as resp:
                resp.raise_for_status()
                return await resp.text()
