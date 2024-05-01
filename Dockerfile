FROM python:latest

RUN pip install --upgrade pip poetry
WORKDIR /code

COPY pyproject.toml poetry.lock .
RUN poetry install --no-root --without dev

# Get the project root after caching dependencies
COPY whisprite whisprite
RUN poetry install --without-dev

CMD poetry run whisprite
