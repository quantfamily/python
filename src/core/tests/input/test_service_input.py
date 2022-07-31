import argparse
import unittest

from foreverbull_core.cli import ServiceInput
from foreverbull_core.http.service import Service
from foreverbull_core.models import service as service_models


def test_service_create(mocker: unittest.mock):
    to_create = service_models.Service(name="service1", image="docker", type=service_models.ServiceType.WORKER)
    created_service = service_models.Service(
        id="abc", name="service1", image="docker", type=service_models.ServiceType.WORKER
    )
    mocked = mocker.patch.object(Service, "create", return_value=created_service)

    parser = argparse.ArgumentParser()
    input_parser = ServiceInput()
    input_parser.add_arguments(parser)

    arguments = ["create", "--name", "service1", "--image", "docker", "--type", "worker"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_with(to_create)


def test_service_list(mocker: unittest.mock):
    services = [
        service_models.Service(id="abc", name="service1", image="docker", type=service_models.ServiceType.WORKER)
    ]
    mocked = mocker.patch.object(Service, "list", return_value=services)

    parser = argparse.ArgumentParser()
    input_parser = ServiceInput()
    input_parser.add_arguments(parser)

    arguments = ["list"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_once()


def test_service_delete(mocker: unittest.mock):
    mocked = mocker.patch.object(Service, "delete", return_value=None)

    parser = argparse.ArgumentParser()
    input_parser = ServiceInput()
    input_parser.add_arguments(parser)

    arguments = ["delete", "--id", "service_id"]
    args = parser.parse_args(arguments)
    input_parser.parse(args)

    mocked.assert_called_with("service_id")
