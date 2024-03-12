from typing import Any, Dict, List, Optional

import typer
from rich import print

from .client import HostgroupClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message, display_success_message

app = typer.Typer()

hostgroup_client: HostgroupClient = HostgroupClient(cycleops_client)


@app.command()
def list() -> None:
    """
    List all of the available hostgroups.
    """

    try:
        hostgroups = hostgroup_client.list()

        if not hostgroups:
            raise NotFound("No hostgroups available")

        print(hostgroups)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def retrieve(
    hostgroup_identifier: str = typer.Argument(
        ..., help="The ID or name of the hostgroup. Names take precedence."
    ),
) -> None:
    """
    Retrieve the hostgroup specified by the given ID.
    """

    try:
        hostgroup = get_hostgroup(hostgroup_identifier)

        print(hostgroup)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def create(
    name: str = typer.Option(
        ...,
        help="The name of the hostgroup.",
    ),
    environment_id: int = typer.Option(None, help="The ID of the environment."),
    hosts: Optional[List[int]] = typer.Option(
        None,
        "--host-id",
        help="The ID of the host.",
    ),
) -> None:
    """
    Create a hostgroup with the specified option values.
    """

    try:
        hostgroup_client.create(
            name=name,
            environment=environment_id,
            hosts=hosts,
        )

        display_success_message(f"Hostgroup {name} has been created")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def update(
    hostgroup_identifier: str = typer.Argument(
        ..., help="The ID or name of the hostgroup. Names take precedence."
    ),
    name: Optional[str] = typer.Option(
        None,
        help="The name of the hostgroup.",
    ),
    environment_id: Optional[int] = typer.Option(
        None, help="The ID of the environment."
    ),
    hosts: Optional[List[int]] = typer.Option(
        None,
        "--host-id",
        help="The ID of the host.",
    ),
) -> None:
    """
    Update a hostgroup with the specified option values.
    """

    try:
        hostgroup = get_hostgroup(hostgroup_identifier)

        hostgroup_client.update(
            hostgroup["id"],
            name=name,
            environment=environment_id,
            hosts=hosts,
        )

        display_success_message(f"Hostgroup {hostgroup_identifier} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    hostgroup_identifier: str = typer.Argument(
        ..., help="The ID or name of the hostgroup. Names take precedence."
    ),
) -> None:
    """
    Delete the hostgroup specified by the given name.
    """

    try:
        hostgroup = get_hostgroup(hostgroup_identifier)

        hostgroup_client.delete(hostgroup["id"])
        display_success_message(f"Hostgroup {hostgroup_identifier} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


def get_hostgroup(hostgroup_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a hostgroup with either a name or ID. Names take precedence.
    """

    hostgroup = hostgroup_client.retrieve(params={"name": hostgroup_identifier})

    if len(hostgroup) == 1:
        return hostgroup[0]

    hostgroup = hostgroup_client.retrieve(hostgroup_identifier)

    return hostgroup
