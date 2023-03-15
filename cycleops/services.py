from typing import List, Optional, Tuple

import typer

from .client import ServiceClient, cycleops_client

app = typer.Typer()

service_client: ServiceClient = ServiceClient(cycleops_client)


@app.command()
def update(
    service_id: int,
    variables: Optional[List[str]] = typer.Option(
        None,
        "--variable",
        "-v",
        help="Variable key-value pairs (e.g. container.image=nginx:1.23)",
    ),
) -> None:
    """
    Update the service specified by the given ID with the specified option values.
    """

    try:
        service = service_client.get(service_id)

        if not service:
            raise ValueError("Invalid resource: Service")

        if variables:
            # split each variable into keys and value, and traverse the dictionary using keys to update the value
            for variable in variables:
                keys, value = validate_variable_format(variable)
                keys = keys.split(".")
                current_dict = service["variables"]

                for key in keys[:-1]:
                    if key not in current_dict:
                        current_dict[key] = {}
                    current_dict = current_dict[key]

                current_dict[keys[-1]] = value

            service_client.update(service_id, service["variables"])
    except Exception as error:
        typer.echo(error)
        raise typer.Abort()


def validate_variable_format(variable: str) -> Tuple[str, str]:
    """
    Validate the format of a variable and return the key-value pair.
    """

    if "=" not in variable:
        raise ValueError("Invalid variable format. Must be in the form of 'key=value'.")

    key, value = variable.split("=", maxsplit=1)

    if not key or not value:
        raise ValueError("Invalid variable format. Key and value cannot be empty.")

    return key.strip(), value.strip()
