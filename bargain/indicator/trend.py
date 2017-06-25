import logging
import math
from collections import deque

from bargain.indicator import Indicator


log = logging.getLogger(__name__)


class ALMA(Indicator):
    """Arnaud Legoux Moving Average

    http://www.arnaudlegoux.com/img/ALMA-Arnaud-Legoux-Moving-Average.pdf

    Args:
        length: Window length
        offset: Trade-off between smoothness and responsiveness
        sigma: Filter width

    """
    def __init__(self, length, offset=0.85, sigma=6):
        super().__init__(length)
        self._prices = deque(maxlen=length)
        self._offset = offset
        self._sigma = sigma

    def advance(self, candle):
        price = candle.close
        self._prices.append(price)
        length = self._prices.maxlen

        m = math.floor(self._offset * (length - 1))
        s = length / self._sigma
        total, norm = 0, 0

        for i, price in enumerate(self._prices):
            coeff = math.exp(-((i - m)**2) / (2 * s**2))
            total += price * coeff
            norm += coeff

        self.values.append(total / norm if norm else price)


class EMA(Indicator):
    """Exponential Moving Average

    Args:
        length: Window length

    """
    def __init__(self, length):
        super().__init__(length)
        self._prices = deque(maxlen=length)
        self._k = 2 / (length + 1)

    def advance(self, candle):
        price = candle.close
        self._prices.append(price)

        ema = price * self._k + self.values[-1] * (1 - self._k) if self.values else price
        self.values.append(ema)
