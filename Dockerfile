FROM python:3.10-bullseye

WORKDIR /code

RUN apt-get update && apt-get -y install libpq-dev gcc && pip install psycopg2

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src
WORKDIR /code/src

CMD ["hypercorn", "--bind", "0.0.0.0:8080", "app.hyuabot.api.main:app"]
