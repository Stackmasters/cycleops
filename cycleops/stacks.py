from typing import List, Optional

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
    stack_id: int = typer.Argument(..., help="The ID of the stack."),
) -> None:
    """
    Retrieve the stack specified by the given ID.
    """

    try:
        stack = stack_client.retrieve(stack_id)

        if not stack:
            raise NotFound("No stack with such ID exists")

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
    stack_id: int = typer.Argument(..., help="The ID of the stack."),
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
        stack_client.update(
            stack_id,
            name=name,
            description=description,
            units=units,
        )

        display_success_message(f"Stack {stack_id} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    stack_id: int = typer.Argument(..., help="The ID of the stack."),
) -> None:
    """
    Delete the stack specified by the given ID.
    """

    try:
        stack_client.delete(stack_id)
        display_success_message(f"Stack {stack_id} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()
