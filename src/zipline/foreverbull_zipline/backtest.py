import json
import os
import threading
from collections import namedtuple

import pandas as pd
import pytz
import six
from foreverbull_zipline.data_bundles.foreverbull import DatabaseEngine, SQLIngester
from foreverbull_zipline.models import EngineConfig, IngestConfig

from zipline import TradingAlgorithm
from zipline.data import bundles
from zipline.data.data_portal import DataPortal
from zipline.errors import SymbolNotFound
from zipline.extensions import load
from zipline.finance import metrics
from zipline.finance.blotter import Blotter
from zipline.finance.trading import SimulationParameters
from zipline.utils.calendar_utils import get_calendar
from zipline.utils.run_algo import BenchmarkSpec, _RunAlgoError

from .exceptions import ConfigError

Config = namedtuple(
    "config", "data_portal, trading_calendar, sim_params, metrics_set, blotter, benchmark_returns, benchmark_sid"
)
Assets = namedtuple("assets", "isins, benchmark")


class Backtest(threading.Thread):
    def __init__(self):
        self.assets = None
        self.handle_data = None
        self.trading_algorithm = None
        self._config = None
        self.backtest_completed = None
        super(Backtest, self).__init__()

    def ingest(self, config: IngestConfig) -> None:
        engine = DatabaseEngine(config.database)
        ingester = SQLIngester(**config.dict(), engine=engine)
        bundles.register(
            config.name,
            ingester,
            calendar_name=config.calendar_name,
        )
        bundles.ingest(config.name, os.environ, pd.Timestamp.utcnow(), [], True)

    def set_callbacks(self, handle_data, backtest_completed) -> None:
        self.handle_data = handle_data
        self.backtest_completed = backtest_completed

    @property
    def configured(self) -> bool:
        return True if self.trading_algorithm else False

    def configure(self, config: EngineConfig) -> None:
        self._config = config
        try:
            start_date = pd.Timestamp(config.start_date, tz=config.timezone)
            end_date = pd.Timestamp(config.end_date, tz=config.timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise ConfigError(repr(e))

        bundles.register(
            config.bundle,
            None,
            calendar_name=config.calendar,
        )

        bundle_data = bundles.load(
            config.bundle,
            os.environ,
            None,
        )
        try:
            benchmark_spec = BenchmarkSpec(None, None, None, benchmark_symbol=config.benchmark, no_benchmark=True)
            benchmark_returns, benchmark_sid = benchmark_spec.resolve(
                asset_finder=bundle_data.asset_finder,
                start_date=start_date,
                end_date=end_date,
            )
        except _RunAlgoError as e:
            raise ConfigError(repr(e))
        trading_calendar = get_calendar("NYSE")
        data_portal = DataPortal(
            bundle_data.asset_finder,
            trading_calendar=trading_calendar,
            first_trading_day=bundle_data.equity_minute_bar_reader.first_trading_day,
            equity_minute_reader=bundle_data.equity_minute_bar_reader,
            equity_daily_reader=bundle_data.equity_daily_bar_reader,
            adjustment_reader=bundle_data.adjustment_reader,
        )
        sim_params = SimulationParameters(
            start_session=start_date,
            end_session=end_date,
            trading_calendar=trading_calendar,
            capital_base=100000,
            data_frequency="daily",
        )
        metrics_set = "default"
        blotter = "default"
        if isinstance(metrics_set, six.string_types):
            try:
                metrics_set = metrics.load(metrics_set)
            except ValueError as e:
                raise ConfigError(repr(e))

        if isinstance(blotter, six.string_types):
            try:
                blotter = load(Blotter, blotter)
            except ValueError as e:
                raise ConfigError(repr(e))
        trading_config = Config(
            data_portal, trading_calendar, sim_params, metrics_set, blotter, benchmark_returns, benchmark_sid
        )
        self.assets = Assets(config.isins, config.benchmark)
        self.trading_algorithm = TradingAlgorithm(
            namespace={},
            data_portal=trading_config.data_portal,
            trading_calendar=trading_config.trading_calendar,
            sim_params=trading_config.sim_params,
            metrics_set=trading_config.metrics_set,
            blotter=trading_config.blotter,
            benchmark_returns=trading_config.benchmark_returns,
            benchmark_sid=trading_config.benchmark_sid,
            handle_data=self.handle_data,
            analyze=self.analyze,
        )
        self.trading_algorithm.assets = []
        try:
            for isin in self.assets.isins:
                self.trading_algorithm.assets.append(self.trading_algorithm.symbol(isin))
        except SymbolNotFound as e:
            raise ConfigError(repr(e))
        self.trading_algorithm.set_benchmark(self.trading_algorithm.symbol(self.assets.benchmark))
        return self.trading_algorithm

    def run(self) -> None:
        # Need to reconfigure to get the trading engine as local thread object
        self.configure(self._config)
        self.trading_algorithm.run()

    def stop(self) -> None:
        return None

    def analyze(self, _, result: pd.DataFrame) -> None:
        result.drop("positions", axis=1, inplace=True)
        result.drop("orders", axis=1, inplace=True)
        result.drop("transactions", axis=1, inplace=True)
        result_in_json = result.to_json(orient="records")
        self.result = json.loads(result_in_json)
        if self.backtest_completed:
            self.backtest_completed()
