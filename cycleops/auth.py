from requests.auth import AuthBase
from requests.models import PreparedRequest


class CycleopsAuthentication(AuthBase):
    """
    Authentication handler for Cycleops API.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = f"api-key {self.api_key}"
        return request
