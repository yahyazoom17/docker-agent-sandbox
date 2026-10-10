
# CrewAI Agent Computer
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV npm_config_cache=/tmp/npm-cache

# Install programming languages and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # JavaScript / TypeScript
    nodejs \
    npm \
    # C / C++
    gcc \
    g++ \
    make \
    cmake \
    gdb \
    # Java
    default-jdk \
    # Shell and system utilities
    bash \
    coreutils \
    findutils \
    grep \
    sed \
    gawk \
    procps \
    util-linux \
    file \
    less \
    nano \
    vim-tiny \
    # Git and downloads
    git \
    curl \
    wget \
    ca-certificates \
    unzip \
    zip \
    # Build dependencies
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create an unprivileged agent user, using an available UID
RUN if ! id -u agent >/dev/null 2>&1; then \
        useradd --create-home --shell /bin/bash agent; \
    fi \
    && mkdir -p /workspace \
    && chown -R agent:agent /workspace /home/agent

# Configure the agent environment
ENV HOME=/home/agent
ENV PATH=/home/agent/.local/bin:$PATH

WORKDIR /workspace

USER agent

# Keep the computer running so CrewAI can execute
# multiple commands inside the same container.
CMD ["sleep", "infinity"]
