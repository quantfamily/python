import pytest
from foreverbull_zipline.backtest import Backtest
from foreverbull_zipline.exceptions import ConfigError
from tests.factories import populate_sql


def test_configure(backtest_config):
    Backtest._config = None
    backtest = Backtest()
    assert backtest.configured is False
    backtest.configure(backtest_config)
    assert backtest.configured is True


def test_configure_bad_timezone(backtest_config):
    backtest = Backtest()
    backtest_config.timezone = "qwerty"
    with pytest.raises(ConfigError, match="UnknownTimeZoneError.*"):
        backtest.configure(backtest_config)


def test_configure_bad_symbol(backtest_config):
    backtest = Backtest()
    backtest_config.benchmark = "Elon Musk"
    with pytest.raises(ConfigError, match=".*Symbol 'Elon Musk' as a benchmark not found in this bundle."):
        backtest.configure(backtest_config)


def test_configure_bad_asset(backtest_config):
    backtest = Backtest()
    backtest_config.isins = ["Corndogs"]
    with pytest.raises(ConfigError, match=".*Symbol 'CORNDOGS' was not found."):
        backtest.configure(backtest_config)


def test_ingest_yahoo(ingest_config):
    backtest = Backtest()
    ingest_config.isins = ["AAPL", "TSLA", "MSFT"]  # Replace due to yahoo working with symbols only

    backtest.ingest(ingest_config)


def test_ingest_foreverbull(ingest_config, database_config):
    populate_sql(ingest_config, database_config)

    ingest_config.name = "foreverbull"
    ingest_config.database = database_config

    backtest = Backtest()
    backtest.ingest(ingest_config)


def test_run_backtest(backtest_config):
    backtest = Backtest()
    backtest.configure(backtest_config)
    backtest.run()
