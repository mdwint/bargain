from datetime import timedelta

from bargain.currency import Currency
from bargain.exchange import Order
from bargain.strategy.marketmaker import MarketMaker


def test_marketmaker(exchange, now):
    pair = (Currency.ETH, Currency.USD)
    trade_amount = 0.1
    profit_margin = 0.10
    buydown_margin = 0.05

    pft = 1 + profit_margin
    bdn = 1 - buydown_margin

    exchange._balance[pair[1]] = 100
    exchange.set_price(pair, 50)
    exchange.set_price(pair, 50)

    strategy = MarketMaker(exchange, now, interval=timedelta(minutes=1))

    def trade():
        strategy.trade(pair, trade_amount, profit_margin, buydown_margin)

    buy1 = Order(pair, trade_amount, 50)
    sell1 = Order(pair, -trade_amount, 50 * pft)
    buydown1 = Order(pair, trade_amount, 50 * bdn)
    trade()

    # Executed buy
    assert exchange.get_trades(pair) == (buy1,)
    assert exchange.get_orders(pair) == (sell1, buydown1)

    trade()

    # No changes
    assert exchange.get_trades(pair) == (buy1,)
    assert exchange.get_orders(pair) == (sell1, buydown1)

    # Price went up
    exchange.set_price(pair, 50 * 1.11)
    buy2 = Order(pair, trade_amount, 50 * 1.11)
    sell2 = Order(pair, -trade_amount, 50 * 1.11 * pft)
    buydown2 = Order(pair, trade_amount, 50 * 1.11 * bdn)
    trade()

    # Executed sell
    assert exchange.get_trades(pair) == (buy1, sell1, buy2)
    assert exchange.get_orders(pair) == (sell2, buydown2)

    # Price went down
    exchange.set_price(pair, 50 * 1.10 * bdn)
    sell3 = Order(pair, -trade_amount, 50 * 1.11 * bdn * pft)
    buydown3 = Order(pair, trade_amount, 50 * 1.11 * bdn * bdn)
    trade()

    # Executed buydown
    assert exchange.get_trades(pair) == (buy1, sell1, buy2, buydown2)
    assert exchange.get_orders(pair) == (sell2, sell3, buydown3)
