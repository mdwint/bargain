import logging

from bargain.charts import emac_chart


log = logging.getLogger(__name__)


class Bot:

    def __init__(self, dryrun, exchange, now, interval):
        self._dryrun = dryrun
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, strategy, pair, ratio):
        backtrack = self._dryrun + strategy.backtrack
        candles = self._exchange.get_candles(pair, self._interval, self._now, backtrack)

        for candle in candles:
            for signal in strategy.advance(candle):
                log.info('{1} {0} {1}'.format(signal.name, '#' * 18))

                # TODO: Refactor
                if not self._dryrun and candle == candles[-1]:
                    order = self._order(pair, signal, ratio)
                    log.info(order)

        if self._dryrun:
            emac_chart(candles, strategy._plot_ema_fast, strategy._plot_ema_slow)

    def _order(self, pair, signal, ratio):
        balances = self._exchange.get_wallet_balances()
        currency = pair[0]
        amount = balances.get(currency, 0) * ratio

        log.info('%s %.5g %s', signal.name, amount, currency.name)
        return self._exchange.place_order(pair, signal, amount)
