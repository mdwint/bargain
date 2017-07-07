from datetime import timedelta

from bargain.currency import Currency
from bargain.exchange import Order
from bargain.strategy.marketmaker import MarketMaker


def test_marketmaker(exchange, now):
    pair = (Currency.ETH, Currency.USD)
    trade_amount = 0.1
    profit_margin = 0.05
    buydown_margin = 0.03

    exchange._balance[pair[1]] = 100
    exchange.set_price(pair, 50)
    exchange.set_price(pair, 50)

    strategy = MarketMaker(exchange, now, interval=timedelta(minutes=1))

    def trade():
        strategy.trade(pair, trade_amount, profit_margin, buydown_margin)

    trade()

    assert exchange.get_trades(pair) == (Order(pair, trade_amount, 50))
    assert exchange.get_orders(pair) == (Order(pair, -trade_amount, 50 * 1.05),
                                         Order(pair, trade_amount, 50 * 0.97))
