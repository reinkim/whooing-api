# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from .kbbank_parser import KbbankParser
from .naverpay_parser import NaverpayParser
from .shcard_parser import ShcardParser
from .shbank_parser import ShbankParser
from .shdebit_parser import ShdebitParser


_parsers= {
    "kbbank": KbbankParser(),
    "naverpay": NaverpayParser(),
    "shcard": ShcardParser(),
    "shbank": ShbankParser(),
    "shdebit": ShdebitParser(),
}


def new_parser(method: str):
    if method not in _parsers:
        raise KeyError(f'Invalid method: {method}')

    return _parsers[method]


def get_parser_names():
    return list(sorted(_parsers.keys()))
