FROM python:3.11-slim-bullseye as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    # Immediately send stdout and stderr to terminal to catch more info on crash
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl gcc libffi-dev g++
RUN curl -LsSf https://astral.sh/uv/0.2.11/install.sh | sh

WORKDIR /app

# Build virtualenv
COPY requirements/requirements.linux.txt ./requirements.txt
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN /root/.cargo/bin/uv venv --python $(which python3.11) $VIRTUAL_ENV \
    && /root/.cargo/bin/uv pip sync ./requirements.txt

COPY . .
RUN /root/.cargo/bin/uv pip install .

ENV PORT=8000
CMD uvicorn telebot_lm.main:app --host 0.0.0.0 --port $PORT
