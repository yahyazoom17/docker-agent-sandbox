
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    nodejs \
    npm \
    sudo \
    nano \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace

WORKDIR /workspace

# Root inside this container
USER root

CMD ["sleep", "infinity"]
