FROM ghcr.io/withlogicco/poetry:1.4.0-python-3.11 as base

WORKDIR /usr/src/app
COPY pyproject.toml poetry.lock ./
RUN poetry check && poetry lock --check
RUN poetry install

COPY ./ ./

FROM base as cli

RUN poetry install
ENTRYPOINT [ "cycleops" ]

FROM base
