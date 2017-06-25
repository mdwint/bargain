from enum import Enum


class Signal(Enum):
    BUY = 1
    SELL = -1


class Indicator:

    def __init__(self, length=0, backtrack_ratio=10):
        self.backtrack = length * backtrack_ratio
        self.values = []

    def advance(self, candle):
        raise NotImplementedError()

    def emit_signal(self):
        raise NotImplementedError


class Price(Indicator):

    def advance(self, candle):
        self.values.append(candle.close)


class Crossover(Indicator):
    """Crossover indicator

    Emits a buy signal when the buy indicator crosses over the sell value,
    and a sell signal when the sell indicator crosses over the buy value.

    Args:
        buy_indicator: Buy indicator
        sell_indicator: Sell indicator

    """
    def __init__(self, buy_indicator, sell_indicator):
        self._buy = buy_indicator
        self._sell = sell_indicator

    @property
    def backtrack(self):
        return max(self._buy.backtrack, self._sell.backtrack)

    def advance(self, candle):
        self._buy.advance(candle)
        self._sell.advance(candle)

    def emit_signal(self):
        def get_tail(indicator):
            tail = indicator.values[-2:]
            return tail if len(tail) > 1 else tail * 2

        a, b = get_tail(self._buy)
        x, y = get_tail(self._sell)

        if a < x and y < b:
            return Signal.BUY
        elif x < a and b < y:
            return Signal.SELL


class Inverse(Indicator):
    """Inverse of an indicator; emits inverse buy/sell signals.

    Args:
        indicator: Indicator to invert

    """
    def __init__(self, indicator):
        self._original = indicator

    def advance(self, candle):
        signal = self._original.advance(candle)
        if signal: return Signal(-signal.value)
