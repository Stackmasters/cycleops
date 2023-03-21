import typer

from .client import SetupClient, cycleops_client

app = typer.Typer()

setup_client: SetupClient = SetupClient(cycleops_client)


@app.command()
def deploy(setup_id: int = typer.Argument(..., help="The id of the setup.")) -> None:
    """
    Deploy the setup with the specified setup_id.
    """

    setup_client.deploy(setup_id)
