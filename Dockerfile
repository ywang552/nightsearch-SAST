FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates git openssh-client nodejs npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --global @openai/codex@latest

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt

COPY scripts/run-codex.sh /usr/local/bin/run-codex
RUN chmod +x /usr/local/bin/run-codex

ENTRYPOINT ["run-codex"]
