from typing import Optional

import typer

from .client import cycleops_client
from .services import app as services_app
from .setups import app as setups_app
from .stacks import app as stacks_app
from .units import app as units_app

cycleops = typer.Typer(pretty_exceptions_show_locals=False)

cycleops.add_typer(services_app, name="services", help="Manage your services.")
cycleops.add_typer(stacks_app, name="stacks", help="Manage your stacks.")
cycleops.add_typer(setups_app, name="setups", help="Manage your setups.")
cycleops.add_typer(units_app, name="units", help="List all of the available units.")


@cycleops.callback()
def configure_cycleops_client(
    base_url: Optional[str] = typer.Option(
        None, help="Configure a base URL for the Cycleops API."
    ),
    api_key: Optional[str] = typer.Option(
        None, help="Set your API key for the Cycleops API."
    ),
) -> None:
    """
    Configures the Cycleops client.
    """

    if base_url:
        cycleops_client.base_url: str = base_url

    if api_key:
        cycleops_client.api_key: str = api_key


if __name__ == "__main__":
    cycleops()
