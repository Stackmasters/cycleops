from typing import Any, Dict, Optional

import requests
import sec
import typer
import websockets
from requests.models import Response
from websockets.legacy.client import WebSocketClientProtocol

from .auth import CycleopsAuthentication
from .exceptions import APIError, AuthenticationError
from .utils import display_error_message, extract_error_message


class Client:
    """
    A client for the Cycleops API.
    """

    def __init__(
        self,
        base_url: Optional[str] = "https://cloud.cycleops.io/stack-manager",
        api_key: Optional[str] = None,
    ):
        self.base_url: str = sec.load("CYCLEOPS_BASE_URL", base_url)
        self.api_key: str = sec.load("CYCLEOPS_API_KEY", api_key)

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        url: str = f"{self.base_url}/{endpoint}"
        headers: Dict[str] = {"Accept": "application/json; version=v2"}
        response: Response = requests.request(
            method,
            url,
            json=payload,
            auth=CycleopsAuthentication(self.api_key),
            params=params,
            headers=headers,
        )
        return self._handle_response(response)

    def _handle_response(self, response: Response) -> Optional[Dict[str, Any]]:
        try:
            if response.status_code == 401:
                error_message: str = extract_error_message(response)
                raise AuthenticationError(error_message, response)

            if response.status_code == 204:
                return None

            try:
                response.raise_for_status()

                return response.json()
            except:
                error_message: str = extract_error_message(response)
                raise APIError(error_message, response)
        except Exception as error:
            display_error_message(error)
            raise typer.Abort()


class SubClient:
    """
    A base class for sub-clients that use the Cycleops API.
    """

    client: Client

    def __init__(self, client: Client):
        self.client: Client = client


class ServiceClient(SubClient):
    """
    Client for managing Cycleops services.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"services")

    def retrieve(
        self, service_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if service_id:
            return self.client._request("GET", f"services/{service_id}")

        return self.client._request("GET", f"services", params=params)

    def create(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("POST", f"services", payload)

    def update(self, service_id: int, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("PATCH", f"services/{service_id}", payload)

    def delete(self, service_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("DELETE", f"services/{service_id}")


class JobClient(SubClient):
    """
    Client for managing Cycleops jobs.
    """

    def create(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("POST", "jobs", payload)

    def retrieve(self, job_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"jobs/{job_id}")


class SetupClient(SubClient):
    """
    Client for managing Cycleops setups.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"setups")

    def retrieve(
        self, setup_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if setup_id:
            return self.client._request("GET", f"setups/{setup_id}")

        return self.client._request("GET", f"setups", params=params)

    def create(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("POST", "setups", payload)

    def update(self, setup_id: int, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("PATCH", f"setups/{setup_id}", payload)

    def delete(self, setup_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("DELETE", f"setups/{setup_id}")

    def deploy(self, setup_id: int) -> Optional[Dict[str, Any]]:
        description: str = f"Deploying setup: {setup_id}"
        type: str = "Deployment"

        jobs_client: JobClient = JobClient(cycleops_client)
        return jobs_client.create(description=description, type=type, setup=setup_id)

    def destroy(self, setup_id: int) -> Optional[Dict[str, Any]]:
        description: str = f"Destroying setup: {setup_id}"
        type: str = "Destruction"

        jobs_client = JobClient(cycleops_client)
        return jobs_client.create(description=description, type=type, setup=setup_id)


class UnitClient(SubClient):
    """
    Client for listing all of the available units.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"units")


class StackClient(SubClient):
    """
    Client for managing Cycleops stacks.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"stacks")

    def retrieve(
        self, stack_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if stack_id:
            return self.client._request("GET", f"stacks/{stack_id}")

        return self.client._request("GET", f"stacks", params=params)

    def create(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("POST", "stacks", payload)

    def update(self, stack_id: int, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("PATCH", f"stacks/{stack_id}", payload)

    def delete(self, stack_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("DELETE", f"stacks/{stack_id}")


class EnvironmentClient(SubClient):
    """
    Client for managing Cycleops environments.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"environments")


class HostClient(SubClient):
    """
    Client for managing Cycleops hosts.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"hosts")

    def retrieve(
        self, host_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if host_id:
            return self.client._request("GET", f"hosts/{host_id}")

        return self.client._request("GET", f"hosts", params=params)

    def create(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("POST", "hosts", payload)

    def update(self, host_id: int, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("PATCH", f"hosts/{host_id}", payload)

    def delete(self, host_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("DELETE", f"hosts/{host_id}")


class HostgroupClient(SubClient):
    """
    Client for managing Cycleops hostgroups.
    """

    def list(self) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"hostgroups")

    def retrieve(
        self,
        hostgroup_id: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if hostgroup_id:
            return self.client._request("GET", f"hostgroups/{hostgroup_id}")

        return self.client._request("GET", f"hostgroups", params=params)

    def create(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("POST", "hostgroups", payload)

    def update(self, hostgroup_id: int, **kwargs: Any) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {k: v for (k, v) in kwargs.items() if v}

        return self.client._request("PATCH", f"hostgroups/{hostgroup_id}", payload)

    def delete(self, hostgroup_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("DELETE", f"hostgroups/{hostgroup_id}")


cycleops_client: Client = Client()


class WebSocketClient:
    """
    A client for interacting with Cycleops websockets to request and listen for job logs.
    """

    def __init__(self, job_id: str):
        self.url: str = "wss://cloud.cycleops.io/ansible-worker-ws/ws/ansible-output"
        self.job_id: str = job_id
        self._jwt: Optional[str] = None
        self._job: Optional[Dict[str, Any]] = None

    @property
    def jwt(self):
        if not self._jwt:
            self._jwt = self.authenticate()
        return self._jwt

    @property
    def job(self):
        if not self._job:
            self._job = self.get_job()
        return self._job

    def authenticate(self) -> Optional[str]:
        token: str = cycleops_client._request("POST", f"identity/token")
        return token["access_token"]

    def get_job(self) -> Optional[Dict[str, Any]]:
        job_client: JobClient = JobClient(cycleops_client)
        job: Optional[Dict[str, Any]] = job_client.retrieve(self.job_id)

        return job

    async def get_job_logs(self, websocket: WebSocketClientProtocol) -> None:
        message: str = f"id={self.job_id}|jwt={self.jwt}|account={self.job['account']}"
        await websocket.send(message)

    async def listen(self, websocket: WebSocketClientProtocol) -> None:
        while message := await websocket.recv():
            print(f"{message}\n")

    async def run(self) -> None:
        async with websockets.connect(self.url) as websocket:
            await self.get_job_logs(websocket)
            await self.listen(websocket)
