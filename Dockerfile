FROM python:3.12-slim

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/partial/* /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 agent

WORKDIR /workspace

RUN chown agent:agent /workspace

USER agent

CMD ["sleep", "infinity"]
