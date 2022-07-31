import os
import time
from threading import Event

import pytest
from foreverbull_core.models.finance import Asset, Order
from zipline.data import bundles

from app.backtest import Backtest
from app.broker import Broker
from app.feed import Feed
from app.models import Database, EngineConfig, IngestConfig
from tests.factories import populate_sql


@pytest.fixture()
def backtest_config():
    config = EngineConfig(
        bundle="yahoo",
        calendar="NYSE",
        start_date="2020-01-07",
        end_date="2020-02-01",
        benchmark="AAPL",
        isins=["AAPL", "TSLA"],
    )
    return config


@pytest.fixture()
def asset():
    asset = Asset(symbol="TSLA", exchange="QUANDL")
    return asset


@pytest.fixture()
def order(asset):
    order = Order(
        asset=asset,
        amount=10,
    )
    return order


@pytest.fixture()
def backtest():
    return Backtest()


@pytest.fixture()
def configured_backtest(backtest, yahoo_bundle, backtest_config):
    backtest.configure(backtest_config)
    yield backtest
    backtest.stop()
    if backtest.is_alive():
        backtest.join()


@pytest.fixture()
def feed(backtest):
    feed = Feed(backtest)
    yield feed


@pytest.fixture()
def broker(backtest):
    broker = Broker(backtest, bardata)
    yield broker


bardata = None
new_day_event = Event()


def handle_data(context, data):
    global bardata
    bardata = data
    if not new_day_event.is_set():
        new_day_event.wait()


def backtest_completed(*args, **kwargs):
    pass


@pytest.fixture()
def running_backtest(configured_backtest):
    new_day_event.clear()
    configured_backtest.set_callbacks(handle_data, backtest_completed)

    def new_day():
        new_day_event.set()
        new_day_event.clear()
        time.sleep(0.2)

    def finish():
        new_day_event.set()
        return

    def start_backtest():
        configured_backtest.start()
        time.sleep(0.5)
        return new_day, finish

    yield start_backtest


@pytest.fixture
def ingest_config():
    return IngestConfig(
        name="yahoo",
        calendar_name="NYSE",
        from_date="2020-01-01",
        to_date="2020-12-31",
        isins=["US0378331005", "US88160R1014", "US5949181045"],
    )


@pytest.fixture
def database_config():
    netloc = os.environ.get("POSTGRES_NETLOC", "127.0.0.1")
    return Database(user="postgres", password="foreverbull", netloc=netloc, port=5433, dbname="postgres")


@pytest.fixture()
def yahoo_bundle(backtest, ingest_config):
    try:
        bundles.load(ingest_config.name)
    except bundles.core.UnknownBundle:
        ingest_config.isins = ["AAPL", "TSLA", "MSFT"]  # Replace due to yahoo working with symbols only

        backtest.ingest(ingest_config)


@pytest.fixture()
def foreverbull_bundle(backtest, ingest_config, database_config):
    populate_sql(ingest_config, database_config)
    ingest_config.name = "foreverbull"
    ingest_config.database = database_config
    try:
        bundles.load(ingest_config.name)
    except bundles.core.UnknownBundle:
        backtest.ingest(ingest_config)
