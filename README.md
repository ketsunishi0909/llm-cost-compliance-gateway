# LLM Cost & Compliance Gateway

A gateway layer for LLM applications that focuses on **cost control, privacy, routing, and safe prompt handling** before requests reach a model provider.

> **Status:** active build. The performance, quality-agreement, and PII-recall figures below are targets until reproduced by this repository's benchmark suite.

## Goals

- Route prompts between model tiers based on task complexity
- Cache repeated and semantically similar prompts
- Redact PII before prompts leave the gateway
- Enforce token and budget limits
- Record routing decisions and policy outcomes
- Benchmark quality/cost tradeoffs on a repeatable prompt set

## Target Resume Metrics

- 54% lower LLM API cost
- 94% quality agreement on a 1,000-prompt benchmark
- <12 ms semantic-cache hit latency
- 96% PII-redaction recall

These are **engineering targets, not claimed results**, until reproduced in code and benchmark artifacts here.

## Architecture

```text
Client
  |
  v
FastAPI Gateway
  |
  +----> PII redaction
  +----> policy / token checks
  +----> exact + semantic cache (Redis)
  +----> model router
  |
  +---- cache hit ----------> response
  |
  +---- cache miss ---------> LLM provider
                                |
                                v
                           cached response
```

## Tech Stack

- Python
- FastAPI
- Redis
- OpenAI API
- Sentence Transformers
- Docker Compose

## Run Locally

```bash
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## Current Scaffold

The initial API already includes:
- deterministic routing tiers,
- basic regex-based PII redaction,
- request/response schemas,
- health endpoint.

The next implementation steps are Redis-backed exact caching, semantic embeddings, provider calls, benchmarking, and policy telemetry.

## Build Plan

- [x] Repository + API scaffold
- [x] Initial PII-redaction layer
- [x] Initial routing policy
- [ ] Redis exact cache
- [ ] Sentence-transformer semantic cache
- [ ] OpenAI provider adapter
- [ ] Token/budget enforcement
- [ ] Prompt benchmark harness
- [ ] Quality-agreement evaluator
- [ ] PII recall benchmark
- [ ] Publish measured cost/latency results
