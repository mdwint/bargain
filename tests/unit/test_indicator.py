from bargain.indicator import Indicator, Signal, inverse


def test_inverse_indicator(monkeypatch):
    normal_indicator = Indicator()
    inverse_indicator = inverse(normal_indicator)

    for normal_signal, inverse_signal in [(Signal.BUY, Signal.SELL),
                                          (Signal.SELL, Signal.BUY), (None, None)]:
        monkeypatch.setattr(normal_indicator, 'advance', lambda c: normal_signal)
        signal = inverse_indicator.advance(candle=None)
        assert signal == inverse_signal
