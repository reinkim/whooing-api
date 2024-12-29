# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from .kbbank_parser import KbbankParser
from .shcard_parser import ShcardParser
from .shbank_parser import ShbankParser

kbbank_parser = KbbankParser()
shcard_parser = ShcardParser()
shbank_parser = ShbankParser()


def new_parser(method: str):
    match method:
        case "kbbank":
            return kbbank_parser
        case "shcard":
            return shcard_parser
        case "shbank":
            return shbank_parser
        case _:
            return None
