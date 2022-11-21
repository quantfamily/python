import logging
from collections import namedtuple
from typing import Callable

import pydantic

from foreverbull_core.models.socket import Request, Response

ROUTE = namedtuple("route", "func, route, model")


class TaskNotFoundError(Exception):
    pass


class TaskAlreadyExists(Exception):
    pass


class MessageRouter:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._routes = {}

    def __call__(self, request: Request) -> Response:
        """Call the router with a Request, trying to find the saved route to call

        Args:
            request (Request): Request to send to a routed function

        Returns:
            Response: Response with possible data from the function called
        """
        if request.task not in self._routes:
            return Response(task=request.task, error=str(TaskNotFoundError("task not found")))
        route = self._routes[request.task]
        try:
            if route.model is None:
                data = route.func()
            else:
                model_data = route.model.load(request.data)
                data = route.func(model_data)
            return Response(task=request.task, data=data)
        except Exception as exc:
            self._logger.error(f"Error calling task: {request.task}")
            self._logger.error(exc, exc_info=True)
            return Response(task=request.task, error=repr(exc))

    def add_route(self, function: Callable, route: str, model: pydantic.BaseModel = None):
        """Add a route to the local _routes with a name<->function pair.

        Args:
            function (function): Function call shall be called on a route
            route (str): Name task which should call a specific function
            model (pydantic.BaseModel, optional): In case we shall include some data to the function being called.
            Defaults to None.

        Raises:
            TaskAlreadyExists: The task we are trying to add is already registed
        """
        if route in self._routes:
            raise TaskAlreadyExists(f"{route} already registered")
        new_route = ROUTE(function, route, model)
        self._routes[route] = new_route
