from requests.models import Response


class Error(Exception):
    """
    Base class for all API errors.
    """

    def __init__(self, message: str, response: Response):
        self.message = message
        self.response = response

    def __str__(self) -> str:
        return f"Status code {self.response.status_code}. Error message: {self.message}"


class AuthenticationError(Error):
    """
    Raised when an API request fails due to an authentication error.
    """

    pass


class APIError(Error):
    """
    Raised when an API request fails due to an unknown error.
    """

    pass
