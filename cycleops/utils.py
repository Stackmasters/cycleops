import json

from requests.models import Response
from rich import print


def extract_error_message(response: Response) -> str:
    """
    Extracts the error message from a requests Response object.
    """
    content_type: str = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        try:
            response_data = response.json()
            if "message" in response_data:
                return response_data["message"]
            if "msg" in response_data:
                return response_data["msg"]
            if "detail" in response_data:
                return response_data["detail"]
            return ""
        except json.JSONDecodeError:
            pass

    if "text/plain" in content_type:
        return response.text.strip()

    return ""


def display_error_message(error):
    print(f"[bold red]{error}[/bold red]")


def display_success_message(message):
    print(f"[bold green]{message}[/bold green]")
