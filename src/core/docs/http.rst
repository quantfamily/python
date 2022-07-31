HTTP
======

------
Client
------

.. autoclass:: foreverbull_core.http.http.HTTPClient
    :members: __init__

----------
Exceptions
----------

.. autoclass:: foreverbull_core.http.exceptions.RequestError

-------
Service
-------

.. autoclass:: foreverbull_core.http.service.Service
   :members: __init__, list, create, update, get, delete, list_instances, get_instance, update_instance, delete_instance

--------
Backtest
--------

.. autoclass:: foreverbull_core.http.backtest.Backtest
    :members: __init__, list, create, get, delete, list_sessions, get_session, delete_session, setup_session, configure_session, run_session, stop_session

------
Worker
------

.. autoclass:: foreverbull_core.http.worker.Worker
    :members: __init__, list, create, get, update, delete
