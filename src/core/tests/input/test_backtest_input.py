import argparse
import json
import unittest

from foreverbull_core.cli import BacktestInput
from foreverbull_core.http.backtest import Backtest
from foreverbull_core.models import backtest as backtest_models

sample_config = backtest_models.EngineConfig(
    start_date="2017-01-01", end_date="2018-01-01", timezone="utc", benchmark="AAPL", assets=["TSLA", "AAPL"]
)


def test_backtest_list(mocker: unittest.mock):
    backtests = [
        backtest_models.Config(id="backtest_id", service_id="service_id", name="test_backtes", config=sample_config)
    ]
    mocked = mocker.patch.object(Backtest, "list", return_value=backtests)

    parser = argparse.ArgumentParser()
    input_parser = BacktestInput()
    input_parser.add_arguments(parser)

    arguments = ["list"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_once()


def test_backtest_create(mocker: unittest.mock):
    with open("for_test.json", "w") as fw:
        fw.write(json.dumps(sample_config.dict()))

    created = backtest_models.Config(
        id="backtest_id", service_id="service_id", name="test_backtest", config=sample_config
    )
    to_create = backtest_models.Config(service_id="service_id", name="test_backtest", config=sample_config)

    mocked = mocker.patch.object(Backtest, "create", return_value=created)

    parser = argparse.ArgumentParser()
    input_parser = BacktestInput()
    input_parser.add_arguments(parser)

    arguments = ["create", "--service-id", "service_id", "--name", "test_backtest", "--config", "for_test.json"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_with(to_create)


def test_backtest_delete(mocker: unittest.mock):
    mocked = mocker.patch.object(Backtest, "delete", return_value=None)

    parser = argparse.ArgumentParser()
    input_parser = BacktestInput()
    input_parser.add_arguments(parser)

    arguments = ["delete", "--id", "backtest_id"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_with("backtest_id")
