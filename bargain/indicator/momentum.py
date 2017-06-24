import logging
from collections import deque

from bargain.indicator import Indicator, Signal


log = logging.getLogger(__name__)


class RSI(Indicator):

    def __init__(self, length, low=30, high=70):
        self._gain = deque(maxlen=length)
        self._loss = deque(maxlen=length)
        self._prev_price = 0

        self._low = low
        self._high = high

        # TODO: Refactor
        self._plot_rsi = []

    @property
    def backtrack(self):
        return self._gain.maxlen * 20

    def advance(self, candle):
        price = candle.close
        change = price - self._prev_price
        self._prev_price = price

        self._gain.append(max(0, change))
        self._loss.append(-min(0, change))

        def ema(values):
            avg = sum(values) / len(values)
            k = 1 / values.maxlen

            for value in values:
                avg = value * k + avg * (1 - k)

            return avg

        avg_gain = ema(self._gain)
        avg_loss = ema(self._loss)

        if avg_loss > 0:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 100

        self._report(candle, rsi)

        if len(self._gain) < self._gain.maxlen:
            # Need more data before emitting signals
            return

        if rsi < self._low:
            yield Signal.BUY
        elif rsi > self._high:
            yield Signal.SELL

    def _report(self, candle, rsi):
        log.debug('{1} {0} {1}'.format(candle.time, '=' * 5))
        log.debug('rsi(%d): %.5g' % (self._gain.maxlen, rsi))

        # TODO: Refactor
        self._plot_rsi.append(rsi)
