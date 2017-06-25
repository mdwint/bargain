from bargain.charts import Candle
from bargain.indicator.trend import ALMA, EMA


def test_alma():
    alma = ALMA(5)

    candles = [Candle(time=i, open=p, close=p, high=p, low=p, volume=1)
               for i, p in enumerate(range(10))]

    for candle in candles:
        alma.advance(candle)

    assert alma.values[-1] == 7.94246134977645


def test_ema():
    ema = EMA(5)

    candles = [Candle(time=i, open=p, close=p, high=p, low=p, volume=1)
               for i, p in enumerate(range(10))]

    for candle in candles:
        ema.advance(candle)

    assert ema.values[-1] == 7.052024589747499
