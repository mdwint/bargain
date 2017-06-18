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
        self._length_fast = length_fast
        self._length_slow = length_slow

    @staticmethod
    def ema(prices, length):
        """Calculates the exponential moving average of given length over prices.

        Args:
            prices (iterable): Prices to calculate EMA for
            length (int): Length of EMA

        Returns:
            :obj:`tuple` of :obj:`float`: The last two EMA values, to be used for crossover check

        """
        assert len(prices) >= length
        head, *tail = prices

        k = 2 / (length + 1)
        ema = deque([head], length)

        for price in tail:
            ema.append(price * k + ema[-1] * (1 - k))

        return list(ema)[-2:]

    def emit_signal(self, get_candles):
        prices = [candle.close for candle in get_candles(limit=self._length_slow * 2)]

        a, b = self.ema(prices, self._length_fast)
        c, d = self.ema(prices, self._length_slow)

        log.debug('fast(%d): %.2f -> %.2f' % (self._length_fast, a, b))
        log.debug('slow(%d): %.2f -> %.2f' % (self._length_slow, c, d))

        if a < c and b > d:
            return Signal.BUY
        elif a > c and b < d:
            return Signal.SELL
