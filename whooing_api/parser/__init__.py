# vim: fileencoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4

from .shcard_parser import ShcardParser
from .shbank_parser import ShbankParser

shcard_parser = ShcardParser()
shbank_parser = ShbankParser()


def new_parser(method: str):
    match method:
        case "shcard":
            return shcard_parser
        case "shbank":
            return shbank_parser
        case _:
            return None
