# Agentic Data Engineering Platform — CLAUDE.md

## What This Is

Enterprise multi-agent platform automating Jira story → validated GitHub PR.
Internal tool for a data engineering team.

## Stack

- Backend: FastAPI (Python 3.11+)
- Frontend: React 18 + Vite + TypeScript (future sessions)

## Commands

cd backend && poetry install # install all deps
cd backend && poetry run uvicorn main:app --reload --port 8000 # dev server
cd backend && poetry add <package> # add a dependency

## Monorepo Layout

agentic-de/
frontend/ # Future sessions
backend/ # FastAPI — building now
.env # Never committed
CLAUDE.md

## Jira API — Critical

- Endpoint: POST /rest/api/3/search/jql (old /rest/api/3/search is DEPRECATED)
- Auth: Basic Auth with base64(email:api_token)
- Pagination: uses nextPageToken, NOT startAt offset
- Use httpx (async), never requests

## Story Status Lifecycle — Canonical Labels

Draft → Analyzing → In Review — BA → Agent-Ready → Agent Running →
Awaiting Code Review → Awaiting Test Review → Awaiting Validation Review → PR Submitted

## Story Types — Canonical Labels

Schema Change, Transformation Change, Bug Fix, New Pipeline,
DQ Enhancement, Data Backfill

## Learning Mode — Active

- Do NOT generate complete files. Teach me to write them.
- Introduce ONE concept at a time. Explain WHY before showing HOW.
- Show me the function signature and purpose. I write the body.
- After I write code, review it. Point out what is wrong and why.
- If I am using a tool/library for the first time (httpx, FastAPI, Pydantic),
  explain what it does, why we chose it over alternatives, and show a
  minimal working example before asking me to write production code.
- Never write more than 15 lines of code in a single response.
- Ask me to run the code after each micro-task and report what happened.
- If something fails, do not fix it for me — explain the error and
  hint at the fix. Let me try first.
- When I say "I'm stuck", show me the answer and explain each line.

## Rules

- Type everything — no `Any` or untyped `dict` returns
- No speculative code outside the current micro-task
- Commit messages use conventional commits

## What Claude Gets Wrong — Guard Against This

- Do not use pip install — use poetry add for dependencies
- Do not create requirements.txt — use pyproject.toml via poetry
