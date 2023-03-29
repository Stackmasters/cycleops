from requests.models import Response


class Error(Exception):
    """
    Base class for all API errors.
    """

    def __init__(self, message: str, response: Response):
        self.message = message
        self.response = response

    def __str__(self) -> str:
        if not self.message:
            if self.response.status_code >= 500:
                self.mesasge = "Service unavailable, please try again later"
            if self.response.status_code == 400:
                self.message = "Please check your inputs and try again"

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


class NotFound(Exception):
    """
    Raised when the requested resource is falsy.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"Error: {self.message}"
