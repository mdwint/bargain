import logging

from bargain.charts import emac_chart
from bargain.indicator import Signal


log = logging.getLogger(__name__)


class Bot:

    def __init__(self, dryrun, exchange, now, interval):
        self._dryrun = dryrun
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, indicator, pair, ratio):
        backtrack = self._dryrun + indicator.backtrack
        candles = self._exchange.get_candles(pair, self._interval, self._now, backtrack)

        for candle in candles:
            for signal in indicator.advance(candle):
                log.debug('{1} {0} {1}'.format(signal.name, '#' * 18))

                # TODO: Refactor; add safeties
                if not self._dryrun and candle == candles[-1]:
                    order = self._order(pair, signal, ratio)
                    log.info(order)

        if self._dryrun:
            # TODO: Refactor
            emac_chart(candles, indicator._plot_ema_fast, indicator._plot_ema_slow)

    def _order(self, pair, signal, ratio):
        ticker = self._exchange.get_ticker(pair)
        balances = self._exchange.get_wallet_balances()

        if signal == Signal.BUY:
            price = ticker.ask
            max_amount = balances.get(pair[1], 0) * price
        elif signal == Signal.SELL:
            price = ticker.bid
            max_amount = balances.get(pair[0], 0)

        amount = max_amount * ratio

        log.info('%s %.5g %s', signal.name, amount, pair[0].name)
        return self._exchange.place_order(pair, signal, amount, price)
