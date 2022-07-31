Socket
======

-------
Nanomsg
-------

.. autoclass:: foreverbull_core.socket.nanomsg.NanomsgSocket
    :members: __init__, url, send, recv, new_context, close

.. autoclass:: foreverbull_core.socket.nanomsg.NanomsgContextSocket
    :members: __init__, send, recv, close


------
Client
------

.. autoclass:: foreverbull_core.socket.client.SocketClient
    :members: __init__, url, send, recv, new_context, close

.. autoclass:: foreverbull_core.socket.client.ContextClient
    :members: __init__, send, recv, close
