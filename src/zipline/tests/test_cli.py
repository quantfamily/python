import os
from unittest import mock

import pytest
from foreverbull_core.broker import Broker

import app.__main__ as main


def test_from_arguments():
    service_id = "service123"
    instance_id = "instance123"
    broker = Broker("https://foreverbull.com", "127.0.0.1")
    args = [
        "--service-id",
        service_id,
        "--instance-id",
        instance_id,
        "--broker-url",
        "https://foreverbull.com",
        "--local-host",
        "127.0.0.1",
    ]
    parsed = main.parser.parse_args(args)
    recieved_service_id = main.get_service_id(parsed)
    recieved_instance_id = main.get_instance_id(parsed)
    recieved_broker = main.get_broker(parsed)
    assert service_id == recieved_service_id
    assert instance_id == recieved_instance_id
    assert broker._broker_host == recieved_broker._broker_host
    assert broker._local_host == recieved_broker._local_host


def test_from_environments():
    env = {
        "SERVICE_ID": "service123",
        "INSTANCE_ID": "instance123",
        "LOCAL_HOST": "127.0.0.1",
        "BROKER_URL": "http://foreverbull.com",
    }
    parsed = main.parser.parse_args([])
    with mock.patch.dict(os.environ, env):
        recieved_service_id = main.get_service_id(parsed)
        recieved_instance_id = main.get_instance_id(parsed)
        recieved_broker = main.get_broker(parsed)

    assert env["SERVICE_ID"] == recieved_service_id
    assert env["INSTANCE_ID"] == recieved_instance_id
    assert env["LOCAL_HOST"] == recieved_broker._local_host
    assert env["BROKER_URL"] == recieved_broker._broker_host


def test_broker_from_arguments_missing_service_id():
    parsed = main.parser.parse_args([])
    with pytest.raises(SystemExit, match="missing service-id"):
        main.get_service_id(parsed)


def test_broker_from_arguments_missing_instance_id():
    parsed = main.parser.parse_args([])
    with pytest.raises(SystemExit, match="missing instance-id"):
        main.get_instance_id(parsed)
