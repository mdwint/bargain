import logging

from bargain.charts import show_chart
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
        signal = None

        for candle in candles:
            indicator.advance(candle)
            tmp_signal = indicator.emit_signal()
            if tmp_signal:
                signal = tmp_signal
                signal_time = candle.time + self._interval
                signal_price = candle.close
                log.debug('%s: %-4s @ %.5g' % (signal_time, signal.name, signal_price))

        if signal:
            self._handle_signal(pair, signal, signal_time, signal_price, ratio)

        if self._dryrun:
            # TODO: Refactor
            show_chart(candles, indicator._sell, indicator._buy)

    def _handle_signal(self, pair, signal, signal_time, signal_price, ratio):
        past_trades = self._exchange.get_past_trades(pair, since=signal_time, until=self._now, limit=1)

        if past_trades:  # and past_trades[-1].signal == signal:
            log.debug('Already traded since %s: %s', signal_time, past_trades[-1])
        else:
            order = self._order(pair, signal, signal_price, ratio)
            if order: log.info(order)

    def _order(self, pair, signal, signal_price, ratio):
        ticker = self._exchange.get_ticker(pair)
        balances = self._exchange.get_wallet_balances()
        amount, price = self._calc_trade_amount_and_price(pair, signal, ticker, balances, ratio)

        # TODO: Check price change against signal_price

        log.info('%s %.8f %s @ %.5g %s', signal.name, amount, pair[0].name, price, pair[1].name)
        if self._dryrun:
            log.info('Skipping order (dry run)')
            return

        return self._exchange.place_order(pair, signal, amount, price)

    @staticmethod
    def _calc_trade_amount_and_price(pair, signal, ticker, balances, ratio):
        if signal == Signal.BUY:
            price = ticker.ask
            max_amount = balances.get(pair[1], 0) / price
        elif signal == Signal.SELL:
            price = ticker.bid
            max_amount = balances.get(pair[0], 0)

        return max_amount * ratio, price
