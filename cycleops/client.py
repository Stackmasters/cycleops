from typing import Any, Dict, Optional

import requests
import sec
import typer
from requests.models import Response

from .auth import CycleopsAuthentication
from .exceptions import APIError, AuthenticationError
from .utils import extract_error_message


class Client:
    """
    A client for the Cycleops API.
    """

    def __init__(
        self,
        base_url: Optional[str] = "https://cloud.cycleops.io/manager",
        api_key: Optional[str] = None,
    ):
        self.base_url: str = sec.load("CYCLEOPS_BASE_URL", base_url)
        self.api_key: str = sec.load("CYCLEOPS_API_KEY", api_key)

    def _request(
        self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        url: str = f"{self.base_url}/{endpoint}"
        response: Response = requests.request(
            method,
            url,
            json=payload,
            auth=CycleopsAuthentication(self.api_key),
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
            typer.echo(error)
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

    def get(self, service_id: int) -> Optional[Dict[str, Any]]:
        return self.client._request("GET", f"services/{service_id}")

    def update(
        self, service_id: int, variables: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {"variables": variables}

        return self.client._request("PATCH", f"services/{service_id}", payload)


class JobClient(SubClient):
    """
    Client for managing Cycleops jobs.
    """

    def create(
        self, description: str, type: str, setup_id: int
    ) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "description": description,
            "type": type,
            "setup": setup_id,
        }

        return self.client._request("POST", "jobs", payload)


class SetupClient(SubClient):
    """
    Client for managing Cycleops setups.
    """

    def deploy(self, setup_id: int) -> Optional[Dict[str, Any]]:
        description: str = f"Deploying setup: {setup_id}"
        type: str = "Deployment"

        jobs_client = JobClient(cycleops_client)
        return jobs_client.create(description, type, setup_id)


cycleops_client: Client = Client()
