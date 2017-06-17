import requests

from bargain.charts import Candle
from bargain.exchange import Exchange
from bargain.utils import dt, ms


class Bitfinex(Exchange):

    _base = 'https://api.bitfinex.com/v2'

    @staticmethod
    def _period(interval):
        return {
            60: '1m',
            300: '5m',
            900: '15m',
            1800: '30m',
            3600: '1h',
        }.get(interval.total_seconds())

    def _get(self, path, **kwargs):
        params = kwargs.pop('params', {})
        r = requests.get(self._base + path.format(**kwargs), params=params)
        r.raise_for_status()
        return r.json()

    def get_candles(self, pair, interval, now, history):
        limit = history.total_seconds() / interval.total_seconds()

        raw = self._get('/candles/trade:{interval}:t{symbol_from}{symbol_to}/hist',
                        interval=self._period(interval), symbol_from=pair[0].name, symbol_to=pair[1].name,
                        params={'start': ms(now - history), 'end': ms(now), 'limit': limit, 'sort': 1})

        return [Candle(dt(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in raw]
