from typing import List, Optional

import typer
from rich import print

from .client import SetupClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message, display_success_message

app = typer.Typer()

setup_client: SetupClient = SetupClient(cycleops_client)


@app.command()
def list() -> None:
    """
    List all of the available setups.
    """

    try:
        setups = setup_client.list()

        if not setups:
            raise NotFound("No setups available")

        print(setups)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def retrieve(
    setup_id: int = typer.Argument(..., help="The ID of the setup."),
) -> None:
    """
    Retrieve the setup specified by the given ID.
    """

    try:
        setup = setup_client.retrieve(setup_id)

        if not setup:
            raise NotFound("No setup with such ID exists")

        print(setup)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def create(
    name: str = typer.Option(
        ...,
        help="The name of the setup.",
    ),
    stack_id: int = typer.Option(None, help="The ID of the stack."),
    environment_id: int = typer.Option(None, help="The ID of the environment."),
    hosts: Optional[List[int]] = typer.Option(
        None,
        "--host-id",
        help="The ID of the host.",
    ),
    hostgroups: Optional[List[int]] = typer.Option(
        None,
        "--hostgroup-id",
        help="The ID of the hostgroup.",
    ),
    services: Optional[List[int]] = typer.Option(
        None,
        "--service-id",
        help="The ID of the service.",
    ),
) -> None:
    """
    Create a setup with the specified option values.
    """

    try:
        setup_client.create(
            name=name,
            stack=stack_id,
            environment=environment_id,
            hosts=hosts,
            hostgroups=hostgroups,
            services=services,
        )

        display_success_message(f"Setup {name} has been created")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def update(
    setup_id: int = typer.Argument(..., help="The ID of the setup."),
    name: str = typer.Option(
        None,
        help="The name of the setup.",
    ),
    stack_id: int = typer.Option(None, help="The ID of the stack."),
    environment_id: int = typer.Option(None, help="The ID of the environment."),
    hosts: Optional[List[str]] = typer.Option(
        None,
        "--host-id",
        help="The ID of the host.",
    ),
    hostgroups: Optional[List[str]] = typer.Option(
        None,
        "--hostgroup-id",
        help="The ID of the hostgroup.",
    ),
    services: Optional[List[str]] = typer.Option(
        None,
        "--service-id",
        help="The ID of the service.",
    ),
) -> None:
    """
    Update a setup with the specified option values.
    """

    try:
        setup_client.update(
            setup_id=setup_id,
            name=name,
            stack=stack_id,
            environment=environment_id,
            hosts=hosts,
            hostgroups=hostgroups,
            services=services,
        )

        display_success_message(f"Setup {setup_id} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    setup_id: int = typer.Argument(..., help="The ID of the setup."),
) -> None:
    """
    Delete the setup specified by the given ID.
    """

    try:
        setup_client.delete(setup_id)
        display_success_message(f"Setup {setup_id} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def deploy(setup_id: int = typer.Argument(..., help="The ID of the setup.")) -> None:
    """
    Deploy the setup with the specified setup_id.
    """

    try:
        setup_client.deploy(setup_id)
        display_success_message(f"Setup {setup_id} has been queued for deployment")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()
