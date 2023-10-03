from typing import Any, Dict, List, Optional, Tuple, Union

import typer
from rich import print

from .client import ServiceClient, cycleops_client
from .exceptions import NotFound
from .utils import display_error_message, display_success_message

app = typer.Typer()

service_client: ServiceClient = ServiceClient(cycleops_client)


@app.command()
def list() -> None:
    """
    List all of the available services.
    """

    try:
        services = service_client.list()

        if not services:
            raise NotFound("No services available")

        print(services)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def retrieve(
    service_identifier: str = typer.Argument(
        ..., help="The ID or name of the service. Names take precedence."
    ),
) -> None:
    """
    Retrieve the service specified by the given ID.
    """

    try:
        service = get_service(service_identifier)

        print(service)
    except Exception as error:
        display_error_message(error)
        raise typer.Exit(code=1)


@app.command()
def create(
    name: str = typer.Option(..., help="The name of the service."),
    unit_id: int = typer.Option(..., help="The ID of the unit."),
    description: Optional[str] = typer.Option(
        None,
        help="The description of the service.",
    ),
    variables: Optional[List[str]] = typer.Option(
        None,
        "--variable",
        help="Variable key-value pairs (e.g. containers.0.image=nginx:1.23).",
    ),
) -> None:
    """
    Create a service with the specified option values.
    """

    try:
        if variables:
            variables = dict_from_variables(variables)

        service_client.create(
            name=name,
            unit=unit_id,
            description=description,
            variables=variables,
        )

        display_success_message(f"Service {name} has been created")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def update(
    service_identifier: str = typer.Argument(
        ..., help="The ID or name of the service. Names take precedence."
    ),
    name: Optional[str] = typer.Option(
        None,
        help="The name of the service.",
    ),
    description: Optional[str] = typer.Option(
        None,
        help="The description of the service.",
    ),
    unit_id: Optional[int] = typer.Option(
        None,
        help="The ID of the unit.",
    ),
    variables: Optional[List[str]] = typer.Option(
        None,
        "--variable",
        help="Variable key-value pairs (e.g. containers.0.image=nginx:1.23).",
    ),
) -> None:
    """
    Update the service specified by the given ID with the given option values.
    """

    try:
        service = get_service(service_identifier)

        if variables:
            variables = dict_from_variables(variables, service["variables"])

        service_client.update(
            service["id"],
            name=name,
            description=description,
            unit=unit_id,
            variables=variables,
        )

        display_success_message(f"Service {service_identifier} has been updated")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def delete(
    service_identifier: str = typer.Argument(
        ..., help="The ID or name of the service. Names take precedence."
    ),
) -> None:
    """
    Delete the service specified by the given ID.
    """

    try:
        service = get_service(service_identifier)

        service_client.delete(service["id"])
        display_success_message(f"Service {service_identifier} has been deleted")
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


def validate_variable_format(variable: str) -> Tuple[str, str]:
    """
    Validates the format of a variable, splits on the first "=" and returns the key-value pair.

    container.image=nginx1.23 | valid
    container.image           | invalid
    =container.image=nginx    | invalid
    """

    if "=" not in variable:
        raise ValueError("Invalid variable format. Must be in the form of 'key=value'.")

    key, value = variable.split("=", maxsplit=1)

    if not key or not value:
        raise ValueError("Invalid variable format. Key and value cannot be empty.")

    return key.strip(), value.strip()


def dict_from_variables(
    variables: List[str], top_level_dict: Dict[str, Any] = {}
) -> Dict[str, Any]:
    """
    Creates or updates a dict, given a list of strings in the following format:

    ["container.image=nginx:1.23", "container.ports=80:80"] -> {'container': {'image': 'nginx:1.23', 'ports': '80:80'}}

    ["containers.0.image=nginx:1.23", "containers.0.ports.0=80:80", "containers.1.image=redis:latest"] -> {'containers': [{'image': 'nginx:1.23', 'ports': [80:80]}, {'image': 'redis:latest'}]}

    Implementation:

        We use current_node to keep track of the current nested dictionary (inside top_level_dict) that we are updating.
        As such, we can update the top_level_dict with the correct nested keys and values without losing track of our current position in the nested structure.

        If we only used top_level_dict, we would break the reference to the initial object.
    """

    for variable in variables:
        keys, value = validate_variable_format(variable)
        keys = keys.split(".")
        keys = [int(x) if x.isdigit() else x for x in keys]
        current_node = top_level_dict

        for i, key in enumerate(keys[:-1]):
            next_key = keys[i + 1]

            if type(key) is str:
                if key not in current_node:
                    current_node[key] = [] if type(next_key) is int else {}
            elif should_create_new_node(key, current_node):
                current_node.append({})

            current_node = current_node[key]

        last_key = keys[-1]
        if should_create_new_node(last_key, current_node):
            current_node.append(value)

        current_node[last_key] = parse_if_bool(value)

    return top_level_dict


def should_create_new_node(
    key: Union[str, int], current_node: Union[Dict[str, Any], List[Any]]
) -> bool:
    """
    Determines if a new node should be created.
    """

    if type(key) is int:
        return key >= len(current_node)
    else:
        return False


def parse_if_bool(value: str) -> Union[str, bool]:
    """
    Parses a string and returns a boolean value.
    """

    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


@app.command()
def create_container(
    service_identifier: str = typer.Argument(
        ..., help="The ID or name of the service. Names take precedence."
    ),
    container_name: str = typer.Option(
        ..., help="The name of the container to be created."
    ),
    image: Optional[str] = typer.Option(
        None,
        help="The image of the container in the following format: <image_name>:<image_tag>",
    ),
    ports: Optional[str] = typer.Option(
        None,
        help="The ports of the container seperated by comma (e.g. 80:80,3000:3000).",
    ),
    volumes: Optional[str] = typer.Option(
        None,
        help="The volumes of the container.",
    ),
    env_file: Optional[str] = typer.Option(
        None,
        help="A file that contains environment variables.",
    ),
    command: Optional[str] = typer.Option(
        None,
        help="A command that is run on container startup.",
    ),
) -> None:
    """
    Create a container in a service with the specified option values.
    """

    try:
        service = get_service(service_identifier)

        image_name = None
        image_tag = None
        if image:
            if ":" not in image or image.count(":") != 1:
                raise ValueError(
                    "Please specify a valid image in the format: <image_name>:<image_tag>"
                )

            image_split = image.split(":")
            image_name = image_split[0]
            image_tag = image_split[1]

        env_vars = []
        if env_file:
            with open(env_file, "r") as env_file_fd:
                for line in env_file_fd:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        env_vars.append(line)

        ports_list = []
        if ports:
            ports_list = [port.strip() for port in ports.split(",")]

        volumes_list = []
        if volumes:
            volumes_list = [volume.strip() for volume in volumes.split(",")]

        service["variables"]["containers"].append(
            {
                "name": container_name,
                "image": image_name,
                "tag": image_tag,
                "ports": ports_list,
                "volumes": volumes_list,
                "env_vars": env_vars,
                "command": command,
            }
        )

        service_client.update(
            service["id"],
            variables=service["variables"],
        )

        display_success_message(
            f"Container {container_name} in Service {service_identifier} has been created"
        )
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


@app.command()
def update_container(
    service_identifier: str = typer.Argument(
        ..., help="The ID or name of the service. Names take precedence."
    ),
    container_name: str = typer.Argument(
        ..., help="The name of the container to be updated."
    ),
    name: Optional[str] = typer.Option(
        None,
        help="A new name for the container.",
    ),
    image: Optional[str] = typer.Option(
        None,
        help="The image of the container in the following format: <image_name>:<image_tag>",
    ),
    ports: Optional[str] = typer.Option(
        None,
        help="The ports of the container seperated by comma (e.g. 80:80,3000:3000).",
    ),
    volumes: Optional[str] = typer.Option(
        None,
        help="The volumes of the container.",
    ),
    env_file: Optional[str] = typer.Option(
        None,
        help="A file that contains environment variables.",
    ),
    command: Optional[str] = typer.Option(
        None,
        help="A command that is run on container startup.",
    ),
) -> None:
    """
    Updates a container in a service with the specified option values.
    """

    try:
        service = get_service(service_identifier)

        container_index = None
        for index, container in enumerate(service["variables"]["containers"]):
            if container["name"] == container_name:
                container_index = index
                break

        if container_index is None:
            raise ValueError(f"Container {container_name} not found")

        image_name = None
        image_tag = None
        if image:
            if ":" not in image or image.count(":") != 1:
                raise ValueError(
                    "Please specify a valid image in the format: <image_name>:<image_tag>"
                )

            image_split = image.split(":")
            image_name = image_split[0]
            image_tag = image_split[1]

        env_vars = []
        if env_file:
            with open(env_file, "r") as env_file_fd:
                for line in env_file_fd:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        env_vars.append(line)

        ports_list = []
        if ports:
            ports_list = [port.strip() for port in ports.split(",")]

        volumes_list = []
        if volumes:
            volumes_list = [volume.strip() for volume in volumes.split(",")]

        container_name = name if name else container_name

        variables = {
            "name": container_name,
            "image": image_name,
            "tag": image_tag,
            "ports": ports_list,
            "volumes": volumes_list,
            "env_vars": env_vars,
            "command": command,
        }

        for key, value in variables.items():
            if value:
                service["variables"]["containers"][container_index][key] = value

        service_client.update(
            service["id"],
            variables=service["variables"],
        )

        display_success_message(
            f"Container {container_name} in Service {service_identifier} has been updated"
        )
    except Exception as error:
        display_error_message(error)
        raise typer.Abort()


def get_service(service_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a Service with either a name or ID. Names take precedence.
    """

    service = service_client.retrieve(params={"name": service_identifier})

    if len(service) == 1:
        return service[0]

    service = service_client.retrieve(service_identifier)

    return service
