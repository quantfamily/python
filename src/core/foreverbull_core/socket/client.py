from foreverbull_core.models.socket import Request, Response, SocketConfig
from foreverbull_core.socket.nanomsg import NanomsgContextSocket, NanomsgSocket


class ContextClient:
    def __init__(self, context_socket: NanomsgContextSocket):
        """Context client is sub socket of SocketClient that will keep track of who sends the request
        to make sure respone will go to the same peer.

        Args:
            context_socket (NanomsgContextSocket): The context_socket to be used for communication,
            uses same Port/int as socket itself.
        """
        self._context_socket = context_socket

    def send(self, message: Response) -> None:
        """Sends a response back to the requester

        Args:
            message (Response): Response will be serialized to bytes before transmitting
        """
        self._context_socket.send(message.dump())

    def recv(self) -> Request:
        """Waits until incoming bytes has been received and load it into a Request Model

        Returns:
            Request: Request that has been received
        """
        data = self._context_socket.recv()
        return Request.load(data)

    def close(self) -> None:
        """Close the socket"""
        self._context_socket.close()


class SocketClient:
    def __init__(self, config: SocketConfig) -> None:
        """SocketClient provides a higher level connection for a socket intended to listen to incoming requests

        Args:
            config (SocketConfig): Configuration for how to socket should work, timeouts etc.
        """
        self.config = config
        self._socket = NanomsgSocket(config)

    def url(self) -> str:
        """Receive the connection information

        Returns:
            str: URL to the local connection
        """
        return self._socket.url()

    def send(self, message: Response) -> None:
        """Sends a response back to the requester

        Args:
            message (Response): Response will be serialized to bytes before transmitting
        """
        self._socket.send(message.dump())

    def recv(self) -> Request:
        """Waits until incoming bytes has been received and load it into a Request Model

        Returns:
            Request: Request that has been received
        """
        data = self._socket.recv()
        return Request.load(data)

    def close(self) -> None:
        """Close the socket"""
        self._socket.close()

    def new_context(self) -> ContextClient:
        """Returns a new context client for this socket that is intended when you might have several
        incoming connections at same time.
        Each context will know where the request came from and reply to the proper peer.

        Returns:
            ContextClient: A new conext client based in this Socket and its address.
        """
        return ContextClient(NanomsgContextSocket(self._socket.new_context()))
