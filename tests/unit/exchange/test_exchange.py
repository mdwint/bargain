from bargain.currency import Currency


def test_orders(exchange):
    pair = (Currency.ETH, Currency.USD)
    exchange._balance[pair[1]] = 100
    exchange.set_price(pair, 50)
    exchange.set_price(pair, 50)
    trade_amount = 0.1

    exchange.place_order(pair, trade_amount)
    sell = exchange.place_order(pair, -trade_amount, price=60)
    buydown = exchange.place_order(pair, trade_amount, price=45)

    def assert_balance(a, b):
        balance = exchange.get_wallet_balances()
        assert balance[pair[0]] == a
        assert balance[pair[1]] == b

    # executed buy
    assert_balance(0.1, 95)
    assert exchange.get_orders(pair) == (sell, buydown)

    exchange.set_price(pair, 61)

    # executed sell
    assert_balance(0, 101)
    assert exchange.get_orders(pair) == (buydown,)

    exchange.set_price(pair, 43)

    # executed buydown
    assert_balance(0.1, 96.5)
    assert not exchange.get_orders(pair)
