from typing import List

import requests

from foreverbull_core.models import service
from foreverbull_core.models.socket import SocketConfig

from .exceptions import RequestError


class Service:
    def __init__(self, host: str, session: requests.session = None) -> None:
        """Initializes Service- endpoint client api

        Args:
            host (str): Host address to the Foreverbull backend server. IP:PORT Format
            session (requests.Session, optional): Use pre defined session instead of creating new. Defaults to None.
        """
        self.host = host
        if session is None:
            session = requests.Session()
        self.session: requests.Session = session

    def list(self) -> List[service.Service]:
        """List stored Services from the Server

        Raises:
            RequestError: In case response code is not OK

        Returns:
            List[service.Service]: List of Services stored on backend
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/services")
        if not rsp.ok:
            raise RequestError(
                f"""get call /services gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return [service.Service(**s) for s in rsp.json()]

    def create(self, service: service.Service) -> service.Service:
        """Create and Store a new Service on the Server

        Args:
            service (service.Service): Service to be created

        Raises:
            RequestError: In case response code is not OK

        Returns:
            service.Service: Created service with Identifier set
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/services", json=service.dict())
        if not rsp.ok:
            raise RequestError(
                f"""post call /services gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return service.update_fields(rsp.json())

    def get(self, service_id: str) -> service.Service:
        """Get a specific Service based on a Identifier

        Args:
            service_id (str): Identifier of the Service

        Raises:
            RequestError: In case response code is not OK

        Returns:
            service.Service: Stored service
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/services/{service_id}")
        if not rsp.ok:
            raise RequestError(
                f"""get call /services/{service_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return service.Service(**rsp.json())

    def update(self, service_id: str, service: service.Service) -> service.Service:
        """Update a stored Service with new Values

        Args:
            service_id (str): Identifier of the service to Update
            service (service.Service): Updated Service that we shall store

        Raises:
            RequestError: In case response code is not OK

        Returns:
            service.Service: Updated stored Service
        """
        rsp = self.session.put(f"http://{self.host}/api/v1/services/{service_id}", json=service.dict())
        if not rsp.ok:
            raise RequestError(
                f"""put call /services/{service_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return service.update_fields(rsp.json())

    def delete(self, service_id: str) -> None:
        """Deletes a stored service from the Server

        Args:
            service_id (str): Identifier of the Service to Delete

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.delete(f"http://{self.host}/api/v1/services/{service_id}")
        if not rsp.ok:
            raise RequestError(
                f"""delete call /services/{service_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return None

    def list_instances(self, service_id: str) -> List[service.Instance]:
        """List stored Instances based on a Service Identifier

        Args:
            service_id (str): Identifier of the Service where we should list Instances from

        Raises:
            RequestError: In case response code is not OK

        Returns:
            List[service.Instance]: List of stored service instances
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/services/{service_id}/instances")
        if not rsp.ok:
            raise RequestError(
                f"""get call /services/{service_id}/instances gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return [service.Instance(**i) for i in rsp.json()]

    def get_instance(self, service_id: str, instance_id: str) -> service.Instance:
        """Get a specific stored instance from server

        Args:
            service_id (str): Service Identifier to the Instance
            instance_id (str): Instance Identifier

        Raises:
            RequestError: In case response code is not OK

        Returns:
            service.Instance: Stored Service Instance from the Server
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/services/{service_id}/instances/{instance_id}")
        if not rsp.ok:
            raise RequestError(
                f"""get call /services/{service_id}/instances/{instance_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return service.Instance(**rsp.json())

    def update_instance(self, service_id: str, container_id: str, socket: SocketConfig, online: bool) -> bool:
        """Update a stored Service Instance

        Args:
            ins (service.Instance): New updated service Instance. Must have same Service ID and Instance ID as before

        Raises:
            RequestError: In case response code is not OK

        Returns:
            service.Instance: Updated Service Instance
        """
        rsp = self.session.put(
            f"http://{self.host}/api/v1/services/{service_id}/instances/{container_id}",
            json={**socket.dict(), "online": online},
        )
        if not rsp.ok:
            code = rsp.status_code  # to mitigate next line too long
            raise RequestError(
                f"""get call /services/{service_id}/instances/{container_id} gave bad return code: {code}
            Text: {rsp.text}"""
            )
        return True

    def delete_instance(self, service_id: str, instance_id: str) -> None:
        """Delete a stored Service Instance

        Args:
            service_id (str): Service Identifier to the Instance
            instance_id (str): Instance Identifier

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.delete(f"http://{self.host}/api/v1/services/{service_id}/instances/{instance_id}")
        if not rsp.ok:
            raise RequestError(
                f"""delete call /services/{service_id}/instances/{instance_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return None
