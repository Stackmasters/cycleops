# Cycleops CLI

This is the official command line interface for the Cycleops API.

## Requirements

* Python 3.11 or later

## Installation

The Cycleops CLI is available on PyPI and you can install it through your favorite package manager:

```console
pip install cycleops
```

## Usage

### Authentication

To authenticate with the Cycleops CLI, you need to provide an API key.

You can find your API keys in the Cycleops UI, under the `Team` category. Alternatively you can create a new API key by visiting `Team > Users > Add New > API key`.

#### Environment variable

Set the `CYCLEOPS_API_KEY` environment variable to your API key.

```console
export CYCLEOPS_API_KEY=<cycleops_api_key>
```

#### Command line option

Configure the Cycleops client through the command line interface.

```console
cycleops --api-key=<cycleops_api_key> services update <service_id> --variable <key>=<value>
```

*Note: If both the environment variable and command line option are set, the command line option will be used by default.*

### Units

#### List of all of the available units

```
cycleops units list
```

### Services

#### List your services

```
cycleops services list
```

#### Retrieve a service

```
cycleops services retrieve <service_id>
```

#### Create a service

```
cycleops services create --name <service_name> --unit-id <unit_id>
```

#### Update a service

```
cycleops services update <service_id> --name <service_name> --description <service_description --unit-id <unit_id> --variable <key_1>=<value_1> --variable <key_2>=<value_2> ... --variable <key_n>=<value_n>
```

#### Delete a service

```
cycleops services delete <service_id>
```

#### Create a Container

```
cycleops services create-container <service_id> <container_name> --image <image_name>:<image_tag> --ports <ports>,<ports> --volumes <volume>,<volume>,<volume> --env-file <env_file_path> --command <command>
```

#### Update a Container

```
cycleops services update-container <service_id> <container_name> --name <new_container_name> --image <image_name>:<image_tag> --ports <ports>,<ports> --volumes <volume>,<volume>,<volume> --env-file <env_file_path> --command <command>
```

### Stacks

#### List your stacks

```
cycleops stacks list
```

#### Retrieve a stack

```
cycleops stacks retrieve <stack_id>
```

#### Create a stack

```
cycleops stacks create --name <stack_name>
```

#### Update a stack

```
cycleops stacks update <stack_id> --name <stack_name> --description <stack_description> --unit-id <unit_id> ... --unit-id <unit_id>
```

#### Delete a stack

```
cycleops stacks delete <stack_id>
```

### Setups

#### List your setups

```
cycleops setups list
```

#### Retrieve a setup

```
cycleops setups retrieve <setup_id>
```

#### Create a setup

```
cycleops setups create --name <setup_name>
```

#### Update a setup

```
cycleops setups update <setup_id> --name <setup_name> --stack-id <stack_id> --environment-id <environment_id> --host-id <host_id> ... --host-id <host_id> --hostgroup-id <hostgroup_id> ... --hostgroup-id <hostgroup_id> --service-id <service_id> ... --service-id <service_id>
```

#### Delete a setup

```
cycleops setups delete <setup_id>
```

#### Deploy a setup

```
cycleops setups deploy <setup_id>
```

### GitHub Actions

You can use Cycleops with your GitHub Actions to deploy a setup right from GitHub. For example this is how you could update the Docker image of a service and deploy a setup:

```yml
 deploy:
    runs-on: ubuntu-latest
    env:
      CYCLEOPS_API_KEY: ${{ secrets.CYCLEOPS_API_KEY }}
    steps:
        run: pip install cycleops
        run: cycleops services update <service_id> --variable containers.0.image=<image_name>
        run: cycleops setups deploy <setup_id>
```

## Example

You can update a service's image and deploy a setup as follows:

```console
$ cycleops services update 17 --variable containers.0.image=nginx:1.23
$ cycleops setups deploy 44
```

## License

This project is licensed under the [`MIT License`](LICENSE)

