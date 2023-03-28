import typer
from rich import print
from rich.table import Table

from .client import UnitClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message

app = typer.Typer()

unit_client: UnitClient = UnitClient(cycleops_client)


@app.command()
def list() -> None:
    """
    List all of the available units.
    """

    try:
        if all:
            units = unit_client.list()

            if not units:
                raise NotFound("No units available")

            table = Table(show_header=True, leading=True)
            table.add_column("ID", width=5)
            table.add_column("Name", width=30)

            for unit in units:
                table.add_row(str(unit["id"]), unit["name"])

            print(table)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)
