import pytest
from foreverbull_zipline.backtest import Backtest
from foreverbull_zipline.exceptions import ConfigError
from tests.factories import populate_sql


def test_configure(engine_config):
    Backtest._config = None
    backtest = Backtest()
    assert backtest.configured is False
    backtest.configure(engine_config)
    assert backtest.configured is True


def test_configure_bad_timezone(engine_config):
    backtest = Backtest()
    engine_config.timezone = "qwerty"
    with pytest.raises(ConfigError, match="UnknownTimeZoneError.*"):
        backtest.configure(engine_config)


def test_configure_bad_symbol(engine_config):
    backtest = Backtest()
    engine_config.benchmark = "Elon Musk"
    with pytest.raises(ConfigError, match=".*Symbol 'Elon Musk' as a benchmark not found in this bundle."):
        backtest.configure(engine_config)


def test_configure_bad_asset(engine_config):
    backtest = Backtest()
    engine_config.isins = ["Corndogs"]
    with pytest.raises(ConfigError, match=".*Symbol 'CORNDOGS' was not found."):
        backtest.configure(engine_config)


def test_ingest(ingest_config, database_config):
    populate_sql(ingest_config, database_config)
    ingest_config.name = "foreverbull"
    ingest_config.database = database_config

    backtest = Backtest()
    backtest.ingest(ingest_config)


def test_run_backtest(engine_config):
    backtest = Backtest()
    backtest.configure(engine_config)
    backtest.run()
