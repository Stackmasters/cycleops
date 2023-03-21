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

### Services

#### Update a service

```
services update <service_id> --variable <key_1>=<value_1> --variable <key_2>=<value_2> ...  --variable <key_n>=<value_n>
```

### Setups

#### Deploy a setup

```
setups deploy <setup_id>
```

## Example

You can update a service's image and deploy a setup as follows:

```console
$ cycleops services update 17 --variable container.image=nginx:1.23
$ cycleops setups deploy 44
```

## License

This project is licensed under the [`MIT License`](LICENSE)

