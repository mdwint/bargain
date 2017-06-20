from enum import Enum


class Signal(Enum):
    BUY = 1
    SELL = -1


class Indicator:

    backtrack = 0

    def advance(self, candle):
        raise NotImplementedError()
