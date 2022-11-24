import pytest
from typing import Iterator

from foreverbull_zipline.models import IngestConfig, EngineConfig
from foreverbull_core.models.socket import Request

class Backtest:
    def __init__(self):
        pass

    def ingest(self, config: IngestConfig) -> None:
        pass

    def configure(self, config: EngineConfig) -> None:
        pass

    def run(self) -> Iterator[Request]:
        pass

class Client:
    def __init__(self):
        pass

    def configure(self) -> None:
        pass

    def process(self, request: Request) -> None:
        pass

@pytest.fixture
def backtest():
    yield Backtest()

@pytest.fixture
def client():
    yield Client()


def test_backtest_client_connection(backtest: Backtest, client: Client):
    backtest.configure()
    client.configure()

    for message in backtest.run():
        client.process(message)
