from datetime import timedelta
from operator import attrgetter

from bargain.currency import Currency


def test_get_candles(now, bitfinex):
    pair = (Currency.ETH, Currency.USD)
    interval = timedelta(minutes=15)
    limit = 10

    candles = bitfinex.get_candles(pair, interval, now, limit)

    assert len(candles) == limit
    assert sorted(candles, key=attrgetter('time')) == candles
