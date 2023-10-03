from typing import Any, Dict, Optional

import requests
import sec
import typer
from requests.models import Response

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
        response: Response = requests.request(
            method,
            url,
            json=payload,
            auth=CycleopsAuthentication(self.api_key),
            params=params,
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


cycleops_client: Client = Client()
