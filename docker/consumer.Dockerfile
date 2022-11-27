FROM python:3.10
WORKDIR /app

COPY ./docker/requirements.txt /tmp
RUN python -m venv .venv && \
    ./.venv/bin/python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    ./.venv/bin/python -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

RUN groupadd user && useradd user -g user

COPY ./src ./src

USER user

CMD ["./.venv/bin/python", "./src/consumer.py"]