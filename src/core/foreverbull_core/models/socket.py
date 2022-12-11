import enum
import socket
from typing import Optional, Union

import pydantic
import pynng
from foreverbull_core.models.base import Base


class SocketType(enum.Enum):
    REQUESTER = pynng.Req0
    REPLIER = pynng.Rep0
    PUBLISHER = pynng.Pub0
    SUBSCRIBER = pynng.Sub0


class SocketConfig(Base):
    """_summary_

    Args:
        socket_type (SocketType): Union[SocketType, str] = SocketType.REPLIER
        host (str): str = socket.gethostbyname(socket.gethostname())
        port (int): int = 0
        listen (bool): bool = True
        recv_timeout (int): int = 5000
        send_timeout (int): int = 5000

    Returns:
        SocketConfig: _description_
    """

    socket_type: Union[SocketType, str] = SocketType.REPLIER
    host: str = socket.gethostbyname(socket.gethostname())
    port: int = 0
    listen: bool = True
    recv_timeout: int = 5000
    send_timeout: int = 5000

    @pydantic.validator("socket_type")
    def validate_socket_type(cls, v):
        if type(v) is str:
            return getattr(SocketType, v.upper())
        return v

    def dict(self, *args, **kwargs):
        return {
            "socket_type": self.socket_type.name,
            "host": self.host,
            "port": self.port,
            "listen": self.listen,
            "recv_timeout": self.recv_timeout,
            "send_timeout": self.send_timeout,
        }

    def dump(self):
        return self.dict()


class Request(Base):
    """_summary_

    Args:
        task (str): str
        data (dict, optional): Optional[dict] = None

    Returns:
        Request: request
    """

    task: str
    data: Optional[dict] = None


class Response(Base):
    """_summary_

    Args:
        task (str): str
        error (str, optional): Optional[str] = None
        data (dict, optional): Optional[dict] = None

    Returns:
        Response: response
    """

    task: str
    error: Optional[str] = None
    data: Optional[dict] = None
