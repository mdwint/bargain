import logging
from collections import deque

from bargain.signal import Signal
from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class EMAC(Strategy):
    """Exponential moving average crossover strategy.

    Calculates the crossover between a short-term and a long-term exponential moving average.

    Emits a *BUY* signal when the short-term EMA crosses *over* the long-term EMA, indicating the start of an upward trend.
    Emits a *SELL* signal when the short-term EMA crosses *under* the long-term EMA, indicating the start of a downward trend.

    """
    def __init__(self, length_fast, length_slow):
        self._ema_fast = deque(maxlen=length_fast)
        self._ema_slow = deque(maxlen=length_slow)

        # TODO: Refactor
        self._plot_ema_fast = []
        self._plot_ema_slow = []

    @property
    def backtrack(self):
        return self._ema_slow.maxlen * 2

    def advance(self, candle):
        price = candle.close

        def update(ema):
            k = 2 / (ema.maxlen + 1)
            ema.append(price * k + ema[-1] * (1 - k) if ema else price)

            tail = list(ema)[-2:]
            return tail if len(tail) > 1 else tail * 2

        a, b = update(self._ema_fast)
        c, d = update(self._ema_slow)

        self._report(candle, a, b, c, d)

        if len(self._ema_slow) < self._ema_slow.maxlen:
            # Need more data before emitting signals
            return

        if a < c and b > d:
            yield Signal.BUY
        elif a > c and b < d:
            yield Signal.SELL

    def _report(self, candle, a, b, c, d):
        log.debug('{1} {0} {1}'.format(candle.time, '=' * 5))
        log.debug('fast(%d): %.5g -> %.5g' % (self._ema_fast.maxlen, a, b))
        log.debug('slow(%d): %.5g -> %.5g' % (self._ema_slow.maxlen, c, d))

        # TODO: Refactor
        self._plot_ema_fast.append(b)
        self._plot_ema_slow.append(d)
