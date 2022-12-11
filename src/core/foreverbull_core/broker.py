from foreverbull_core.http import HTTPClient
from foreverbull_core.models.socket import SocketConfig


class Broker:
    def __init__(self, broker_host: str, local_host: str) -> None:
        """Initializes a specific broker connected to Foreverbull

        Args:
            broker_host (str): Address of the server we are trying to connect
            local_host (str): Address of this localhost who is using this library
        """
        self._broker_host = broker_host
        self._local_host = local_host
        self.http = HTTPClient(self._broker_host)
        self.socket_config = SocketConfig(host=self._local_host, port=5555)
