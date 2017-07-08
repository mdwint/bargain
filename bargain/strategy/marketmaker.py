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

    def trade(self, pair, trade_amount, profit_margin, buydown_margin):
        price = self._exchange.get_ticker(pair).ask
        orders = self._exchange.get_active_orders(pair)

        sell_orders = [o for o in orders if o.is_sell]
        buy_orders = [o for o in orders if o.is_buy]

        cancel_orders = []
        new_orders = []

        def place_order(*args, **kwargs):
            order = Order(*args, **kwargs)
            new_orders.append(order)
            return order

        def place_market_buy():
            return place_order(pair, trade_amount, price)

        if not sell_orders:
            buy = place_market_buy()
        elif not buy_orders:
            buy = self._get_last_buy(pair) or place_market_buy()
        else:
            buy = None

        if buy:
            # Place limit sell with profit
            place_order(pair, -trade_amount, buy.price * (1 + profit_margin))
            price = buy.price

        # (Re)place limit buydown to maintain straddle
        if buy_orders:
            cancel_orders.extend(buy_orders)
        place_order(pair, trade_amount, price * (1 - buydown_margin))

        log.info('Cancel orders: %s', cancel_orders)
        log.info('Place orders: %s', new_orders)

        if self._dryrun:
            log.info('Skipping orders (dry run)')
            return

        if cancel_orders:
            self._exchange.cancel_orders(cancel_orders)
        self._exchange.place_orders(new_orders)

    def _get_last_buy(self, pair):
        until = self._now
        since = until - self._interval

        try:
            return [o for o in self._exchange.get_past_trades(pair, since, until) if o.is_buy][-1]
        except IndexError:
            return None
