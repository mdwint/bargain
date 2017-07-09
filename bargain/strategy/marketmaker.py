import logging

from bargain.exchange import Order
from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class MarketMaker(Strategy):

    def __init__(self, dryrun, exchange, now, interval):
        self._dryrun = dryrun
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, pair, trade_amount, profit_pct, buydown_pct):
        orders = self._exchange.get_active_orders(pair)
        sell_orders = [o for o in orders if o.is_sell]
        buy_orders = [o for o in orders if o.is_buy]

        profit_scl = (100 + profit_pct) / 100
        buydown_scl = (100 - buydown_pct) / 100

        def place_order(order):
            if self._dryrun:
                log.info('Skipping order (dry run): %s', order)
                return order
            log.info('Placing order: %s', order)
            return self._exchange.place_order(order)

        def cancel_orders(orders):
            if not orders:
                return
            if self._dryrun:
                log.info('Skipping cancel (dry run): %s', orders)
                return
            log.info('Cancel orders: %s', orders)
            self._exchange.cancel_orders(orders)

        def place_market_buy():
            ticker = self._exchange.get_ticker(pair)
            buy = Order(pair, trade_amount, price=ticker.ask)
            return place_order(buy)

        def place_profit_sell(buy):
            sell = Order(pair, -trade_amount, buy.price * profit_scl)
            sell_orders.append(sell)
            return place_order(sell)

        if not sell_orders:
            buy = place_market_buy()
            place_profit_sell(buy)
        elif not buy_orders:
            buy = self._get_last_buy(pair) or place_market_buy()
            place_profit_sell(buy)

        min_sell_price = min(o.price for o in sell_orders)
        buydown = Order(pair, trade_amount, min_sell_price / profit_scl * buydown_scl)

        if buydown not in buy_orders:
            cancel_orders(buy_orders)
            place_order(buydown)

    def _get_last_buy(self, pair):
        until = self._now
        since = until - self._interval * 2
        past_trades = self._exchange.get_past_trades(pair, since, until)
        log.debug('Past trades: %s', past_trades)

        try:
            return [t for t in past_trades if t.is_buy][-1]
        except IndexError:
            return None
