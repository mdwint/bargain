import logging

from bargain.charts import emac_chart


log = logging.getLogger(__name__)


class Bot:

    def __init__(self, exchange, now, interval, backtrack):
        self._exchange = exchange
        self._now = now
        self._interval = interval
        self._backtrack = backtrack

    def trade(self, strategy, pair, chart=False):
        backtrack = self._backtrack + strategy.backtrack
        candles = self._exchange.get_candles(pair, self._interval, self._now, backtrack)

        for candle in candles:
            for signal in strategy.advance(candle):
                log.info('{1} {0} {1}'.format(signal.name, '#' * 18))

        if chart:
            emac_chart(candles, strategy._plot_ema_fast, strategy._plot_ema_slow)
