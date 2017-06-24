from enum import Enum


class Signal(Enum):
    BUY = 1
    SELL = -1


class Indicator:

    backtrack = 0

    def advance(self, candle):
        raise NotImplementedError()


class inverse(Indicator):

    def __init__(self, indicator):
        self._original = indicator

    def advance(self, candle):
        signal = self._original.advance(candle)
        if signal: return Signal(-signal.value)
