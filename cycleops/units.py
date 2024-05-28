import typer
from rich import print

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
        raw_units = unit_client.list()

        if not raw_units:
            raise NotFound("No units available")

        units = [
            {
                "id": raw_unit.get("id"),
                "name": raw_unit.get("name"),
                "type_slug": raw_unit.get("type_slug"),
                "service_groups_slugs": raw_unit.get("service_groups_slugs"),
            }
            for raw_unit in raw_units
            if raw_unit.get("type_slug") != "system"
        ]

        print(units)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)
