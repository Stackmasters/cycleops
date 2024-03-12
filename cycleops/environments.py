import typer
from rich import print
from rich.table import Table

from .client import EnvironmentClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message

app = typer.Typer()

environment_client: EnvironmentClient = EnvironmentClient(cycleops_client)


@app.command()
def list() -> None:
    """
    List all of the available environments.
    """

    try:
        environments = environment_client.list()

        if not environments:
            raise NotFound("No environments available")

        table = Table(show_header=True, leading=True)
        table.add_column("ID", width=5)
        table.add_column("Name", width=30)

        for environment in environments:
            table.add_row(str(environment["id"]), environment["name"])

        print(table)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)
