from datetime import datetime

from foreverbull_core.models.finance import Asset, Order
from foreverbull_core.models.socket import Request, Response

from foreverbull import Foreverbull
from foreverbull.models import OHLC, Configuration, Parameter


def configured_worker(data, dataframe, ma_high, ma_low):
    assert ma_high == 64
    assert ma_low == 16
    asset = Asset(symbol="TSLA", exchange="QUANDL")
    return Order(asset=asset, amount=10)


def test_configure(mocker):
    fb = Foreverbull()
    # configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    configuration = Configuration(
        execution_id="123",
        execution_start_date=datetime.now(),
        execution_end_date=datetime.now(),
        parameters=[param1, param2],
    )

    request = Request(task="configure", data=configuration)
    response = Response(task="configure")
    assert fb._routes(request) == response
    fb.stop()


def test_stock_data_configured():
    fb = Foreverbull()

    Foreverbull._worker_routes["stock_data"] = configured_worker

    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    configuration = Configuration(
        execution_id="123",
        execution_start_date=datetime.now(),
        execution_end_date=datetime.now(),
        parameters=[param1, param2],
    )
    req = Request(task="configure", data=configuration)
    rsp = fb._routes(req)

    assert rsp.error is None
    assert len(fb._workers) == 1
    assert len(fb._worker_routes) == 1

    # stock_data
    ohlc = OHLC(
        isin="ISIN11223344",
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
        time=datetime.now(),
    )
    req = Request(task="stock_data", data=ohlc)
    rsp = fb._routes(req)
    assert rsp.error is None
    fb.stop()


def test_stock_data_not_configured():
    fb = Foreverbull()
    # stock_data
    ohlc = OHLC(
        isin="ISIN11223344",
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
        time=datetime.now(),
    )
    req = Request(task="stock_data", data=ohlc)
    rsp = fb._routes(req)
    assert rsp.error == "Exception('workers are not initialized')"
    assert rsp.data is None


def test_backtest_completed():
    fb = Foreverbull()
    req = Request(task="backtest_completed")
    rsp = fb._routes(req)
    assert rsp.error is None
