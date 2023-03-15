import typer

from .client import app as client_app
from .services import app as services_app
from .setups import app as setups_app

cycleops = typer.Typer(pretty_exceptions_show_locals=False)

cycleops.add_typer(client_app, name="client")
cycleops.add_typer(services_app, name="services")
cycleops.add_typer(setups_app, name="setups")


if __name__ == "__main__":
    cycleops()
