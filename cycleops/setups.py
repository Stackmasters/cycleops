import time
from typing import Any, Dict, List, Optional

import typer
from rich import print

from .client import JobClient, SetupClient, cycleops_client
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
        report_queued = print if wait else display_success_message
        report_queued(f"Setup {setup['id']} has been queued for deployment")

        while wait:
            match status := job["status"]:
                case "Initialized":
                    print(f"Setup {setup['id']} has been initialized")
                case "Deploying":
                    print(f"Setup {setup['id']} is being deployed")
                case "Deployed":
                    display_success_message(
                        f"Setup {setup['id']} has been deployed successfully"
                    )
                    break
                case "Failed":
                    display_error_message(job)
                    raise Exception(f"Setup {setup['id']} could not be deployed")
                case _:
                    print(f"Setup {setup['id']} is in status {status}")
            time.sleep(3)
            job = job_client.retrieve(job["id"])
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


def get_setup(setup_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a Setup with either a name or ID. Names take precedence.
    """

    setup = setup_client.retrieve(params={"name": setup_identifier})

    if len(setup) == 1:
        return setup[0]

    setup = setup_client.retrieve(setup_identifier)

    return setup
