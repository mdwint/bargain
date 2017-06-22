from datetime import datetime, timezone

import pytest

from bargain.exchange.bitfinex import Bitfinex


@pytest.fixture(scope='session')
def now():
    return datetime.now(timezone.utc)


@pytest.fixture(scope='session')
def bitfinex():
    return Bitfinex()
