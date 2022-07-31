import argparse
import unittest

from foreverbull_core.cli import WorkerInput
from foreverbull_core.http.worker import Worker
from foreverbull_core.models import worker as worker_models

sample_parameters = [
    worker_models.Parameter(key="test_key", default=11),
    worker_models.Parameter(key="test_key2", default=22),
]


def test_workers_list(mocker: unittest.mock):
    workers = [
        worker_models.Config(id="worker_id", service_id="service_id", name="test_worker", parameters=sample_parameters)
    ]
    mocked = mocker.patch.object(Worker, "list", return_value=workers)

    parser = argparse.ArgumentParser()
    input_parser = WorkerInput()
    input_parser.add_arguments(parser)

    arguments = ["list"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_once()


def test_worker_create(mocker: unittest.mock):
    created = worker_models.Config(
        id="worker_id", service_id="service_id", name="test_worker", parameters=sample_parameters
    )
    to_create = worker_models.Config(service_id="service_id", name="test_worker", parameters=sample_parameters)

    mocked = mocker.patch.object(Worker, "create", return_value=created)

    parser = argparse.ArgumentParser()
    input_parser = WorkerInput()
    input_parser.add_arguments(parser)

    arguments = [
        "create",
        "--service-id",
        "service_id",
        "--name",
        "test_worker",
        "--parameters",
        "test_key=11",
        "test_key2=22",
    ]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_with(to_create)


def test_worker_delete(mocker: unittest.mock):
    mocked = mocker.patch.object(Worker, "delete", return_value=None)

    parser = argparse.ArgumentParser()
    input_parser = WorkerInput()
    input_parser.add_arguments(parser)

    arguments = ["delete", "--id", "worker_id"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_with("worker_id")
