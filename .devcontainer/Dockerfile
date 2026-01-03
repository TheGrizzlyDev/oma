FROM mcr.microsoft.com/devcontainers/base:bookworm

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    coreutils \
    curl \
  && rm -rf /var/lib/apt/lists/*

ENV PATH="/home/vscode/.local/bin:/root/.local/bin:${PATH}"
