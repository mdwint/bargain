from bargain.signal import Signal


class Strategy:
    pass


class MovingAverage(Strategy):

    def emit_signal(self, candles):
        return Signal.HOLD
