FROM docker.io/ubuntu:26.10
ARG LLM="qwen3.5:0.8b"
ARG LLM_ORCH="granite3-moe:latest"

WORKDIR /ai_agent
ENV LLM=$LLM

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl python3-venv zstd python3-pip \
    && curl -fsSL https://ollama.com/install.sh | sh

RUN ollama serve & sleep 10 && ollama pull $LLM && ollama pull $LLM_ORCH

RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip3 install ollama ddgs

COPY ai.py ./

ENV LLM_ORCH=$LLM_ORCH


CMD nohup ollama serve > /dev/null 2>&1 & sleep 10 && . venv/bin/activate && python3 ai.py