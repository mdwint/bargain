import logging

from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class MarketMaker(Strategy):

    def __init__(self, exchange, now, interval):
        self._exchange = exchange

    def trade(self, now, trade_amount):
        orders = self._exchange.get_orders(None)

        buy_orders = (o for o in orders if o['side'] == 'buy')
        sell_orders = (o for o in orders if o['side'] == 'sell')

        if not sell_orders:
            # TODO: Buy now + place sell
            pass
        elif not buy_orders:
            # TODO: Place sell
            pass
        else:
            # TODO: (Re)place buydown order(s) to maintain straddle
            pass

        log.info(orders)
