from foreverbull_core.http import backtest, service, worker


class HTTPClient:
    def __init__(self, host: str) -> None:
        """Initializes a HTTPClient which has the underlying http endpoints

        Args:
            host (str): Host address to the Foreverbull backend server. IP:PORT Format
        """
        self.backtest = backtest.Backtest(host)
        self.service = service.Service(host)
        self.worker = worker.Worker(host)
