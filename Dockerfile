FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl build-essential

ENV POETRY_VERSION=1.8.1

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . /app

RUN poetry install --no-root

CMD ["/root/.local/bin/poetry", "run", "uvicorn", "src.main:app", "--reload", "--host=0.0.0.0", "--port=5050"]
