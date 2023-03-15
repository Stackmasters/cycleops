import typer

from .client import SetupClient, cycleops_client

app = typer.Typer()

setup_client: SetupClient = SetupClient(cycleops_client)


@app.command()
def deploy(setup_id: int) -> None:
    """
    Create a deployment job for the specified setup_id.
    """

    setup_client.deploy(setup_id)
