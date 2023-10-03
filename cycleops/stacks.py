from typing import List, Optional, Dict, Any

import typer
from rich import print

from .client import StackClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message, display_success_message

app = typer.Typer()

stack_client: StackClient = StackClient(cycleops_client)


@app.command()
def list() -> None:
    """
    List all of the available stacks.
    """

    try:
        if all:
            stacks = stack_client.list()

        if not stacks:
            raise NotFound("No stacks available")

        print(stacks)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def retrieve(
    stack_identifier: str = typer.Argument(
        ..., help="The ID or name of the stack. Names take precedence."
    ),
) -> None:
    """
    Retrieve the stack specified by the given ID or name.
    """

    try:
        stack = get_stack(stack_identifier)

        print(stack)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def create(
    name: str = typer.Option(
        ...,
        help="The name of the stack.",
    ),
    description: Optional[str] = typer.Option(
        None,
        help="The description of the job.",
    ),
    units: Optional[List[int]] = typer.Option(
        None,
        "--unit-id",
        help="The ID of the setup.",
    ),
) -> None:
    """
    Create a stack with the specified option values.
    """

    try:
        stack_client.create(
            name=name,
            description=description,
            units=units,
        )

        display_success_message(f"Stack {name} has been created")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def update(
    stack_identifier: str = typer.Argument(
        ..., help="The ID or name of the stack. Names take precedence."
    ),
    name: str = typer.Option(
        None,
        help="The name of the stack.",
    ),
    description: Optional[str] = typer.Option(
        None,
        help="The description of the job.",
    ),
    units: Optional[List[int]] = typer.Option(
        None,
        "--unit-id",
        help="The ID of the setup.",
    ),
) -> None:
    """
    Update a stack with the specified option values.
    """

    try:
        stack = get_stack(stack_identifier)

        stack_client.update(
            stack["id"],
            name=name,
            description=description,
            units=units,
        )

        display_success_message(f"Stack {stack_identifier} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    stack_identifier: str = typer.Argument(
        ..., help="The ID or name of the stack. Names take precedence."
    ),
) -> None:
    """
    Delete the stack specified by the given name.
    """

    try:
        stack = get_stack(stack_identifier)

        stack_client.delete(stack["id"])
        display_success_message(f"Stack {stack_identifier} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


def get_stack(stack_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a Stack with either a name or ID. Names take precedence.
    """

    stack = stack_client.retrieve(params={"name": stack_identifier})

    if len(stack) == 1:
        return stack[0]

    stack = stack_client.retrieve(stack_id=stack_identifier)

    return stack
