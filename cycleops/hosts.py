from typing import Any, Dict, List, Optional

import typer
from rich import print

from .client import HostClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message, display_success_message

app = typer.Typer()

host_client: HostClient = HostClient(cycleops_client)

REGISTRATION_STATUS_CHOICES = {
    11: "Registering",
    6: "Registered",
    5: "Unregistered",
}


@app.command()
def list() -> None:
    """
    List all of the available hosts.
    """

    try:
        hosts = host_client.list()

        if not hosts:
            raise NotFound("No hosts available")

        for host in hosts:
            host["register_status"] = REGISTRATION_STATUS_CHOICES.get(
                host["register_status"]
            )

        print(hosts)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def retrieve(
    host_identifier: str = typer.Argument(
        ..., help="The ID or name of the host. Names take precedence."
    ),
) -> None:
    """
    Retrieve the host specified by the given ID.
    """

    try:
        host = get_host(host_identifier)

        print(host)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def create(
    name: str = typer.Option(
        ...,
        help="The name of the host.",
    ),
    ip: str = typer.Option(..., help="The IP of the host."),
    environment_id: int = typer.Option(..., help="The ID of the environment."),
    jump_host: Optional[str] = typer.Option(
        "false", help="Whether the host is a jump host (true, false)."
    ),
    hostgroups: Optional[List[int]] = typer.Option(
        None,
        "--hostgroup-id",
        help="The ID of the hostgroup.",
    ),
) -> None:
    """
    Create a host with the specified option values.
    """

    try:
        host_client.create(
            name=name,
            IP=ip,
            environment=environment_id,
            jump_host=jump_host.lower(),
            hostgroups=hostgroups,
        )

        display_success_message(f"Host {name} has been created")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def update(
    host_identifier: str = typer.Argument(
        ..., help="The ID or name of the host. Names take precedence."
    ),
    name: Optional[str] = typer.Option(
        None,
        help="The name of the host.",
    ),
    ip: Optional[str] = typer.Option(None, help="The IP of the host."),
    environment_id: Optional[int] = typer.Option(
        None, help="The ID of the environment."
    ),
    jump_host: Optional[str] = typer.Option(
        None, help="Whether the host is a jump host (true, false)."
    ),
    hostgroups: Optional[List[int]] = typer.Option(
        None,
        "--hostgroup-id",
        help="The ID of the hostgroup.",
    ),
) -> None:
    """
    Update a host with the specified option values.
    """

    try:
        if jump_host:
            jump_host = jump_host.lower()

        host = get_host(host_identifier)

        host_client.update(
            host["id"],
            name=name,
            IP=ip,
            environment=environment_id,
            jump_host=jump_host,
            hostgroups=hostgroups,
        )

        display_success_message(f"Host {host_identifier} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    host_identifier: str = typer.Argument(
        ..., help="The ID or name of the host. Names take precedence."
    ),
) -> None:
    """
    Delete the host specified by the given name.
    """

    try:
        host = get_host(host_identifier)

        host_client.delete(host["id"])
        display_success_message(f"Host {host_identifier} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


def get_host(host_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a host with either a name or ID. Names take precedence.
    """

    host = host_client.retrieve(params={"name": host_identifier})

    if len(host) == 1:
        return host[0]

    host = host_client.retrieve(host_identifier)

    return host
