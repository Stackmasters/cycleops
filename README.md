# Cycleops CLI

This is the official command line interface for the Cycleops API.

## Requirements

To run the Cycleops CLI either Python 3.11 or newer, or Docker is required.

## Installation

### Python

The Cycleops CLI is available as a Python package on PyPI:

```console
pip install cycleops
CYCLEOPS_API_KEY=your-api-key cycleops --help
```

### Docker

If your system is running Docker, you can also use Cycleops directly its Docker image:

```console
docker run -e CYCLEOPS_API_KEY=your-api-key ghcr.io/stackmasters/cycleops --help
```

## Usage

### Authentication

To authenticate with the Cycleops CLI, you need to provide an API key. Documentation on how to create an API key is available at https://cycleops.io/docs/api-keys/create-a-new-api-key.

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

### Environments

#### List your environments

```
cycleops environments list
```


### Hosts

#### List your hosts

```
cycleops hosts list
```

#### Retrieve a host

```
cycleops hosts retrieve <host_name>|<host_id>
```

#### Create a host

```
cycleops hosts create --name <host_name> --ip <host_ip> --environment-id <environment_id> --jump-host true|false --hostgroup-id <hostgroup_id> ... --hostgroup-id <hostgroup_id>
```

#### Update a host

```
cycleops hosts update <host_name>|<host_id> --name <host_name> --ip <host_ip> --environment-id <environment_id> --jump-host true|false --hostgroup-id <hostgroup_id> ... --hostgroup-id <hostgroup_id>
```

#### Delete a host

```
cycleops hosts delete <host_name>|<host_id>
```


### Services

#### List your services

```
cycleops services list
```

#### Retrieve a service

```
cycleops services retrieve <service_name>|<service_id>
```

#### Create a service

```
cycleops services create --name <service_name> --unit-id <unit_id>
```

#### Update a service

```
cycleops services update <service_name>|<service_id> --name <service_name> --description <service_description --unit-id <unit_id> --variable <key_1>=<value_1> --variable <key_2>=<value_2> ... --variable <key_n>=<value_n>
```

#### Delete a service

```
cycleops services delete <service_name>|<service_id>
```

#### Create a Container

```
cycleops services create-container <service_name>|<service_id> <container_name> --image <image_name>:<image_tag> --ports <ports>,<ports> --volumes <volume>,<volume>,<volume> --env-file <env_file_path> --command <command>
```

#### Update a Container

```
cycleops services update-container <service_name>|<service_id> <container_name> --name <new_container_name> --image <image_name>:<image_tag> --ports <ports>,<ports> --volumes <volume>,<volume>,<volume> --env-file <env_file_path> --command <command>
```

### Stacks

#### List your stacks

```
cycleops stacks list
```

#### Retrieve a stack

```
cycleops stacks retrieve <stack_name>|<stack_id>
```

#### Create a stack

```
cycleops stacks create --name <stack_name>
```

#### Update a stack

```
cycleops stacks update <stack_name>|<stack_id> --name <stack_name> --description <stack_description> --unit-id <unit_id> ... --unit-id <unit_id>
```

#### Delete a stack

```
cycleops stacks delete <stack_name>|<stack_id>
```

### Setups

#### List your setups

```
cycleops setups list
```

#### Retrieve a setup

```
cycleops setups retrieve <setup_name>|<setup_id>
```

#### Create a setup

```
cycleops setups create --name <setup_name>
```

#### Update a setup

```
cycleops setups update <setup_name>|<setup_id> --name <setup_name> --stack-id <stack_id> --environment-id <environment_id> --host-id <host_id> ... --host-id <host_id> --hostgroup-id <hostgroup_id> ... --hostgroup-id <hostgroup_id> --service-id <service_id> ... --service-id <service_id>
```

#### Delete a setup

```
cycleops setups delete <setup_name>|<setup_id>
```

#### Deploy a setup

```
cycleops setups deploy <setup_name>|<setup_id> --wait
```

Using `--wait` you can wait for the deployment job to complete.

### GitHub Actions

You can use Cycleops with your GitHub Actions to deploy a setup right from GitHub. For example this is how you could update the Docker image of a service and deploy a setup:

```yml
 deploy:
    runs-on: ubuntu-latest
    env:
      CYCLEOPS_API_KEY: ${{ secrets.CYCLEOPS_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install Cycleops
        run: pip install cycleops
      - name: Update Cycleops services
        run: cycleops services update-container <service_name> <container_name> --image <image_name>:<image_tag>
      - name: Deploy Cycleops setups
        run: cycleops setups deploy <setup_name>
```

## Example

You can update a service's image and deploy a setup as follows:

```console
$ cycleops services update default-container-ngnix --variable containers.0.image=nginx:1.23
$ cycleops setups deploy default-container-ngnix
```

## License

This project is licensed under the [`MIT License`](LICENSE)
