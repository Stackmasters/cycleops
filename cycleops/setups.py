import asyncio
import time
from typing import Any, Dict, List, Optional

import typer
import websockets
from rich import print

from .client import JobClient, SetupClient, WebSocketClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message, display_success_message

app = typer.Typer()

setup_client: SetupClient = SetupClient(cycleops_client)
job_client: JobClient = JobClient(cycleops_client)


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
    setup_identifier: str = typer.Argument(
        ..., help="The ID or name of the setup. Names take precedence."
    ),
) -> None:
    """
    Retrieve the setup specified by the given ID or name.
    """

    try:
        setup = get_setup(setup_identifier)

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
    setup_identifier: str = typer.Argument(
        ..., help="The ID or name of the setup. Names take precedence."
    ),
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
        setup = get_setup(setup_identifier)

        setup_client.update(
            setup_id=setup["id"],
            name=name,
            stack=stack_id,
            environment=environment_id,
            hosts=hosts,
            hostgroups=hostgroups,
            services=services,
        )

        display_success_message(f"Setup {setup_identifier} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    setup_identifier: str = typer.Argument(
        ..., help="The ID or name of the setup. Names take precedence."
    ),
) -> None:
    """
    Delete the setup specified by the given ID or name.
    """

    try:
        setup = get_setup(setup_identifier)

        setup_client.delete(setup["id"])
        display_success_message(f"Setup {setup_identifier} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def deploy(
    setup_identifier: str = typer.Argument(
        ..., help="The ID or name of the setup. Names take precedence."
    ),
    wait: Optional[bool] = typer.Option(
        default=False, help="Wait for the deployment job to complete"
    ),
) -> None:
    """
    Deploy the setup with the specified given ID or name.
    """

    try:
        setup = get_setup(setup_identifier)
        job = setup_client.deploy(setup["id"])
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()

    deployment_scheduled_message = (
        f"Setup {setup_identifier} has been queued for deployment"
    )

    if not wait:
        display_success_message(deployment_scheduled_message)
        return

    print(f"{deployment_scheduled_message}\n")

    try:
        display_job_logs(job["id"])
    except websockets.exceptions.ConnectionClosed:
        job = job_client.retrieve(job["id"])

        match job["status"]:
            case "Deployed":
                display_success_message(
                    f"Setup {setup_identifier} has been deployed successfully"
                )
            case "Failed":
                display_error_message(f"Setup {setup_identifier} could not be deployed")
            case _:
                print(f"Setup {setup_identifier} is in status {job['status']}")
        return


@app.command()
def destroy(
    setup_identifier: str = typer.Argument(
        ..., help="The ID or name of the setup. Names take precedence."
    ),
    wait: Optional[bool] = typer.Option(
        default=False, help="Wait for the destroy job to complete"
    ),
) -> None:
    """
    Destroy the setup with the specified given ID or name.
    """

    try:
        setup = get_setup(setup_identifier)
        job = setup_client.destroy(setup["id"])

        display_success_message(f"Setup {setup['id']} has been queued for destruction")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()

    destruction_scheduled_message = (
        f"Setup {setup_identifier} has been queued for destruction"
    )

    if not wait:
        display_success_message(destruction_scheduled_message)
        return

    print(f"{destruction_scheduled_message}\n")

    try:
        display_job_logs(job["id"])
    except websockets.exceptions.ConnectionClosed:
        job = job_client.retrieve(job["id"])

        match job["status"]:
            case "Initialized":
                display_success_message(
                    f"Setup {setup_identifier} has been destroyed successfully"
                )
            case "Failed":
                display_error_message(
                    f"Setup {setup_identifier} could not be destroyed"
                )
            case _:
                print(f"Setup {setup_identifier} is in status {job['status']}")
        return


def get_setup(setup_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a Setup with either a name or ID. Names take precedence.
    """

    setup = setup_client.retrieve(params={"name": setup_identifier})

    if len(setup) == 1:
        return setup[0]

    setup = setup_client.retrieve(setup_identifier)

    return setup


def display_job_logs(job_id: str) -> None:
    """
    Displays the deployements logs of the specified job
    """

    websocket_client = WebSocketClient(job_id)

    asyncio.get_event_loop().run_until_complete(websocket_client.run())
