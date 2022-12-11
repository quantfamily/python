from foreverbull_core.models.socket import SocketConfig
from pynng import exceptions, nng

from .exceptions import SocketClosed, SocketTimeout


class NanomsgContextSocket:
    def __init__(self, context_socket: nng.Context):
        """Provides a low level class for managing context sockets

        Args:
            context_socket (nng.Context): Context socket coming from a "normal" socket
        """
        self._context_socket = context_socket

    def send(self, data: bytes) -> None:
        """Send byte data over the socket to a peer

        Args:
            data (bytes): Bytes to send over the socket

        Raises:
            SocketClosed: In case the we are trying to send over a closed socket

        Returns:
            None:
        """
        try:
            return self._context_socket.send(data)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def recv(self) -> bytes:
        """Wait and receive byte data from a peer

        Raises:
            SocketTimeout: _description_
            SocketClosed: _description_

        Returns:
            bytes: Incoming byte data
        """
        try:
            return self._context_socket.recv()
        except exceptions.Timeout as exc:
            raise SocketTimeout(exc)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def close(self) -> None:
        """Close the socket"""
        return self._context_socket.close()


class NanomsgSocket:
    def __init__(self, config: SocketConfig):
        """Initializes a low level Nanomsg socket for transmitting data between peers

        Args:
            config (SocketConfig): Configuration about how the socket should work.
                                    In case Port is not set and we are a listener we will get a random port.
        """
        self._socket = None
        self._config = config
        self._socket = self._config.socket_type.value
        if self._config.listen:
            self._socket = self._config.socket_type.value(listen=f"tcp://{self._config.host}:{self._config.port}")
        else:
            self._socket = self._config.socket_type.value(dial=f"tcp://{self._config.host}:{self._config.port}")
        self._socket.recv_timeout = self._config.recv_timeout
        self._socket.send_timeout = self._config.send_timeout
        if self._config.listen and self._config.port == 0:
            # Pretty hacky way to find the port that OS randomly assigns when it's orginally set as 0
            self._config.port = int(self._socket.listeners[0].url.split(":")[-1])

    def url(self) -> str:
        """Returns the local address of the socket

        Returns:
            str: Local address in host:port format
        """
        if self._config.listen:
            return self._socket.listeners[0].url
        return self._socket.dialers[0].url

    def send(self, data: bytes) -> None:
        """Send byte data over the socket to a peer

        Args:
            data (bytes): Bytes to send over the socket

        Raises:
            SocketClosed: In case the we are trying to send over a closed socket

        Returns:
            None:
        """
        try:
            return self._socket.send(data)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def recv(self) -> bytes:
        """Wait and receive byte data from a peer

        Raises:
            SocketTimeout: _description_
            SocketClosed: _description_

        Returns:
            bytes: Incoming byte data
        """
        try:
            return self._socket.recv()
        except exceptions.Timeout as exc:
            raise SocketTimeout(exc)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def close(self) -> None:
        """Closes the socket"""
        return self._socket.close()

    def new_context(self) -> NanomsgContextSocket:
        """Returns a context socket used when we have multiple concurrent connections coming to us

        Returns:
            NanomsgContextSocket: Context socket based on this socket
        """
        return NanomsgContextSocket(self._socket.new_context())
