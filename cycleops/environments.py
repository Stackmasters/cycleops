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

        environments_result = []
        for environment in environments:
            environment_result = {
                "id": environment["id"],
                "hosts": environment["hosts"],
                "hostgroups": environment["hostgroups"],
                "account": environment["account"],
                "name": environment["name"],
                "description": environment["description"],
            }

            environments_result.append(environment_result)

        print(environments_result)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)
