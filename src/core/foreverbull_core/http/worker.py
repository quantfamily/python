from typing import List

import requests

from foreverbull_core.http import RequestError
from foreverbull_core.models import worker


class Worker:
    def __init__(self, host, session=None) -> None:
        """Initializes Worker endpoint client ID

        Args:
            host (str): Host address to the Foreverbull backend server. IP:PORT Format
            session (requests.Session, optional): Use pre defined session instead of creating new. Defaults to None.
        """
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list(self) -> List[worker.Config]:
        """List stored workers from the Server

        Raises:
            RequestError: In case response code is not OK

        Returns:
            List[worker.Config]: List of workers from the Server
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/workers")
        if not rsp.ok:
            raise RequestError(
                f"""get call /workers gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return [worker.Config(**w) for w in rsp.json()]

    def create(self, worker: worker.Config) -> worker.Config:
        """Creates and stores a new Worker on the Server

        Args:
            worker (worker.Config): Configuration for the new Worker

        Raises:
            RequestError: In case response code is not OK

        Returns:
            worker.Config: Stored worker from the server
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/workers", json=worker.json())
        if not rsp.ok:
            raise RequestError(
                f"""post call /workers gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return worker.update_fields(rsp.json())

    def get(self, worker_id: int) -> worker.Config:
        """Get a specific worker from the Server

        Args:
            worker_id (int): Identifier of the worker

        Raises:
            RequestError: In case response code is not OK

        Returns:
            worker.Config: Stored worker from the Server
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/workers/{worker_id}")
        if not rsp.ok:
            raise RequestError(
                f"""get call /workers/{worker_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return worker.Config(**rsp.json())

    def update(self, worker_id: int, worker: worker.Config) -> worker.Config:
        """Update a specifc worker on the Server

        Args:
            worker_id (int): Identifier of the worker to update
            worker (worker.Config): Updated configuration for the Worker

        Raises:
            RequestError: In case response code is not OK

        Returns:
            worker.Config: Updated worker from the Server
        """
        rsp = self.session.put(f"http://{self.host}/api/v1/workers/{worker_id}", json=worker.json())
        if not rsp.ok:
            raise RequestError(
                f"""put call /workers/{worker_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return worker.update_fields(rsp.json())

    def delete(self, worker_id: int) -> None:
        """Deletes a worker from the Server

        Args:
            worker_id (int): Identifier of the Worker

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.delete(f"http://{self.host}/api/v1/workers/{worker_id}")
        if not rsp.ok:
            raise RequestError(
                f"""delete call /workers/{worker_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return None
