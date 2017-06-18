from datetime import datetime

import pytest

from bargain.exchange.bitfinex import Bitfinex


@pytest.fixture(scope='session')
def now():
    return datetime.utcnow()


@pytest.fixture(scope='session')
def bitfinex():
    return Bitfinex()
