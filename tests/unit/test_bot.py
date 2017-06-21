from bargain.bot import Bot
from bargain.currency import Currency
from bargain.exchange import Ticker
from bargain.indicator import Signal


def test_buy_amount_and_price():
    pair = (Currency.ETH, Currency.USD)
    ticker = Ticker(bid=5, ask=4)
    balances = {Currency.ETH: 0, Currency.USD: 10}
    ratio = 0.8

    amount, price = Bot._calc_trade_amount_and_price(pair, Signal.BUY, ticker, balances, ratio)

    assert amount == 2
    assert price == 4


def test_sell_amount_and_price():
    pair = (Currency.ETH, Currency.USD)
    ticker = Ticker(bid=5, ask=4)
    balances = {Currency.ETH: 10, Currency.USD: 0}
    ratio = 0.8

    amount, price = Bot._calc_trade_amount_and_price(pair, Signal.SELL, ticker, balances, ratio)

    assert amount == 8
    assert price == 5
