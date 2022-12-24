import os
import time
from threading import Event

import pytest
from foreverbull_core.models.finance import Instrument, Order
from foreverbull_core.models.socket import SocketConfig
from foreverbull_zipline.app import Application
from foreverbull_zipline.backtest import Backtest
from foreverbull_zipline.broker import Broker
from foreverbull_zipline.feed import Feed
from foreverbull_zipline.models import Database, EngineConfig, IngestConfig
from tests.factories import populate_sql

from zipline.data import bundles


@pytest.fixture(scope="function")
def application():
    socket_config = SocketConfig(host="127.0.0.1", port=6565)
    application = Application(socket_config)
    application.start()
    for _ in range(10):
        if application.running:
            break
        time.sleep(0.1)
    else:
        raise Exception("Application not running")
    yield application
    application.stop()
    application.join()


@pytest.fixture()
def engine_config(foreverbull_bundle):
    return EngineConfig(
        bundle="foreverbull",
        calendar="NYSE",
        start_date="2020-01-07",
        end_date="2020-02-01",
        benchmark="US0378331005",
        isins=["US0378331005", "US88160R1014"],
    )


@pytest.fixture()
def instrument():
    instrument = Instrument(symbol="US88160R1014", exchange="NYSE")
    return instrument


@pytest.fixture()
def order(instrument):
    order = Order(
        isin=instrument.symbol,
        amount=10,
    )
    return order


@pytest.fixture()
def backtest():
    return Backtest()


@pytest.fixture()
def configured_backtest(backtest, foreverbull_bundle, engine_config):
    backtest.configure(engine_config)
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
def ingest_config(database_config):
    return IngestConfig(
        database=database_config,
        name="foreverbull",
        calendar_name="NYSE",
        from_date="2019-12-24",
        to_date="2020-12-31",
        isins=["US0378331005", "US88160R1014", "US5949181045"],
    )


@pytest.fixture
def database_config():
    netloc = os.environ.get("POSTGRES_NETLOC", "127.0.0.1")
    return Database(user="postgres", password="foreverbull", netloc=netloc, port=5433, dbname="postgres")


@pytest.fixture()
def foreverbull_bundle(ingest_config, database_config):
    populate_sql(ingest_config, database_config)

    try:
        bundles.load(ingest_config.name)
    except ValueError:
        Backtest().ingest(ingest_config)
