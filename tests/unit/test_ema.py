from bargain.strategy.ema import EMAC


def test_ema_calculation():
    a, b = EMAC.ema(prices=list(range(10)), length=5)

    assert a == 6.078036884621247
    assert b == 7.052024589747499
