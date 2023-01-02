import logging

import foreverbull
import numpy
from foreverbull.data.data import Database
from foreverbull.models import OHLC
from foreverbull_core.models.finance import Order
from pandas.core.frame import DataFrame
from talib import EMA

bull = foreverbull.Foreverbull()

logger = logging.getLogger(__name__)

ema_low = 16
ema_high = 32


def should_hold(df: DataFrame, low, high):
    high = EMA(df.close, timeperiod=high).iloc[-1]
    low = EMA(df.close, timeperiod=low).iloc[-1]
    if numpy.isnan(high) or low < high:
        return False
    return True


@bull.on("ohlc")
def ema(ohlc: OHLC, database: Database):
    history = database.stock_data(ohlc.isin)
    position = database.get_position(ohlc.isin)
    hold = should_hold(history, ema_low, ema_high)

    if hold and position is None:
        return Order(isin=ohlc.isin, amount=10)
    elif position and not hold:
        return Order(asset=ohlc.isin, amount=-position.amount)
    return None
