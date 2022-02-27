FROM python:3.9

ENV TZ=Europe/Moscow

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-dev

COPY bot /app/bot

CMD ["python", "-m", "bot"]
