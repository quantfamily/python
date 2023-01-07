import logging
from random import choice

import foreverbull
from foreverbull.data.data import Database
from foreverbull.models import OHLC
from foreverbull_core.models.finance import Order

bull = foreverbull.Foreverbull()

logger = logging.getLogger(__name__)


@bull.on("ohlc")
def random(ohlc: OHLC, database: Database):
    return choice([Order(isin=ohlc.isin, amount=10), Order(isin=ohlc.isin, amount=-10), None])
