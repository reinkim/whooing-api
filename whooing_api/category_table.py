from typing import List

from pydantic import BaseModel

import pygtrie


class ItemMapping(BaseModel):
    # 카드 명세서의 이름
    name: str
    # 후잉에 표시할 이름
    display_name: str
    # 비용 항목
    spend_type: str


class Item:
    def __init__(self, spend_type, name):
        self.spend_type = spend_type
        self.name = name


class CategoryTable:
    def __init__(self, rules: List[ItemMapping]):
        self.trie = pygtrie.CharTrie()
        self.trie.enable_sorting(True)

        for rule in rules:
            key = rule.name.replace(' ', '').lower()
            self.trie[key] = Item(rule.spend_type, rule.display_name)

    # lookups predefined rules, and returns (spend (or debt) category, item name)
    def lookup(self, item_name: str):
        item_name = item_name.replace(' ', '').lower()
        try:
            v = self.trie.items(item_name)
            return v[0][1].spend_type, v[0][1].name
        except KeyError:
            v = self.trie.longest_prefix(item_name)
            if not v or not v.value:
                return '', ''

            return v.value.spend_type, v.value.name

