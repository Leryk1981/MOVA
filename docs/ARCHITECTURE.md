# MOVA Architecture

Это документ, который даёт обзор архитектуры MOVA на высоком уровне и служит ориентиром для дальнейших улучшений.

## Core Components

- MOVA Engine
- Parsers
- Validators
- Models
- CLI
- RedisManager
- LLM Client
- Webhook
- Web Interface

## Architecture Diagram

```mermaid
graph TD
ENGINE[MOVA Engine]
PARSERS[Parsers]
VALIDATORS[Validators]
MODELS[Models]
LLM[LLM Client]
CLI[CLI]
REDIS[RedisManager]
WEBHOOK[Webhook]
WEBUI[Web Interface]

ENGINE --> PARSERS
ENGINE --> VALIDATORS
ENGINE --> MODELS
ENGINE --> LLM
ENGINE --> CLI
ENGINE --> REDIS
ENGINE --> WEBHOOK
ENGINE --> WEBUI
```

## Data Flow

Input File -> Parser -> Validator -> Engine -> Output