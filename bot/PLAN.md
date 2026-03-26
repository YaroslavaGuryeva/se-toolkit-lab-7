# LMS Telegram Bot — Development Plan

## Overview

This document outlines the plan for building a Telegram bot that lets users interact with the LMS backend through chat. The bot supports slash commands for structured actions and uses an LLM to understand plain language questions.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point (`bot.py`)** — Handles Telegram startup and `--test` mode for offline testing
2. **Handlers (`handlers/`)** — Command logic as pure functions with no Telegram dependency
3. **Services (`services/`)** — External API clients (LMS backend, LLM)
4. **Configuration (`config.py`)** — Environment variable loading from `.env.bot.secret`

This separation means handlers can be tested without Telegram, and the same handler functions work in `--test` mode, unit tests, and production.

## Task Breakdown

### Task 1: Plan and Scaffold

Create the project skeleton with testable handler architecture. Deliverables:
- `bot.py` with `--test` mode that calls handlers directly
- `handlers/` directory with placeholder command handlers
- `config.py` for loading secrets from environment files
- `pyproject.toml` with bot dependencies
- This `PLAN.md` document

**Key pattern**: Handlers are plain functions. They take input and return text. No Telegram imports.

### Task 2: Backend Integration

Connect handlers to the real LMS backend. Deliverables:
- `services/lms_api.py` — HTTP client with Bearer token authentication
- Update handlers to call the backend instead of returning placeholders
- Error handling for network failures and API errors
- `/health` reports actual backend status
- `/labs` fetches real lab data
- `/scores` fetches per-task pass rates

**Key pattern**: API client abstracts HTTP details. Handlers call `lms_api.get_labs()`, not `httpx.get()`.

### Task 3: Intent-Based Natural Language Routing

Add LLM-powered intent recognition for plain text queries. Deliverables:
- `services/llm_client.py` — LLM API client
- `handlers/intent_router.py` — Uses LLM to determine user intent
- Tool descriptions for all 9 backend endpoints
- Plain text like "what labs are available" routes to `handle_labs()`

**Key pattern**: LLM tool use. The model reads tool descriptions and decides which to call. Description quality matters more than prompt engineering.

### Task 4: Containerize and Document

Deploy the bot alongside the existing backend. Deliverables:
- `Dockerfile` for the bot container
- Add bot service to `docker-compose.yml`
- Documentation for deployment and troubleshooting
- Verify bot responds in Telegram

**Key pattern**: Docker networking. Containers use service names (`backend`), not `localhost`.

## Testing Strategy

- **Unit tests**: Test handlers directly (no Telegram)
- **Test mode**: `uv run bot.py --test "/command"` for manual verification
- **Integration tests**: Test API client against running backend
- **Deploy verification**: Send commands in Telegram after deployment

## Dependencies

- `aiogram` — Async Telegram bot framework
- `httpx` — Async HTTP client for API calls
- `pydantic-settings` — Environment variable loading
- LLM API — For intent recognition (Task 3)

## File Structure

```
bot/
├── bot.py              # Entry point with --test mode
├── config.py           # Configuration loader
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
├── handlers/
│   ├── __init__.py     # Command handlers
│   └── intent_router.py # LLM intent routing (Task 3)
└── services/
    ├── lms_api.py      # LMS API client (Task 2)
    └── llm_client.py   # LLM client (Task 3)
```
