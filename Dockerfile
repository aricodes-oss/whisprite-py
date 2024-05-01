FROM python:latest

RUN pip install --upgrade pip poetry
WORKDIR /code

COPY pyproject.toml poetry.lock .
RUN poetry install --no-root

# Get the project root after caching dependencies
COPY whisprite whisprite
RUN poetry install

CMD poetry run whisprite
