# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from .kbbank import KbbankParser
from .hdcard import HdcardParser
from .naverpay import NaverpayParser
from .shcard import ShcardParser
from .shbank import ShbankParser
from .shdebit import ShdebitParser


_parsers= {
    "kbbank": KbbankParser(),
    "naverpay": NaverpayParser(),
    "shcard": ShcardParser(),
    "shbank": ShbankParser(),
    "shdebit": ShdebitParser(),
    'hdcard': HdcardParser(),
}


def new_parser(method: str):
    if method not in _parsers:
        raise KeyError(f'Invalid method: {method}')

    return _parsers[method]


def get_parser_names():
    return list(sorted(_parsers.keys()))
