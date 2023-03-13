FROM ghcr.io/withlogicco/poetry:1.4.0

# COPY pyproject.toml poetry.lock ./
# RUN poetry install

COPY ./ ./