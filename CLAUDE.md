# Agentic DE Platform — CLAUDE.md

## What This Is

Enterprise multi-agent platform automating Jira story → validated GitHub PR.
Internal tool for a data engineering team. Not a chatbot.

## Stack

- Frontend: React 18 + Vite + TypeScript (no Next.js)
- Backend: FastAPI (Python 3.11+)
- Database: PostgreSQL with pgvector
- Styling: shadcn/ui + Tailwind CSS (custom theme tokens)
- State: Zustand
- Tables: TanStack Table v8
- DAG: React Flow + dagre

## Monorepo Layout

agentic-de/
frontend/ # React + Vite + TypeScript
backend/ # FastAPI
db/ # Migrations (Alembic) — future
.env # Never committed
CLAUDE.md # You are reading this

## Personas (role-based access)

DE (Data Engineer), BA (Business Analyst), PO (Product Owner),
TPM (Technical Program Manager), Director/MD

## Story Status Lifecycle — Canonical Labels

Draft → Analyzing → In Review — BA → Agent-Ready → Agent Running →
Awaiting Code Review → Awaiting Test Review → Awaiting Validation Review → PR Submitted

## Story Types — Canonical Labels

Schema Change, Transformation Change, Bug Fix, New Pipeline,
DQ Enhancement, Data Backfill

## Jira API — Critical

- Endpoint: POST /rest/api/3/search/jql (the old /rest/api/3/search is DEPRECATED)
- Auth: Basic Auth with base64(email:api_token)
- Pagination: uses nextPageToken, NOT startAt/maxResults offset
- Always use httpx (async), never requests

## Commands

cd backend && pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000
cd frontend && npm run dev
cd frontend && npx tsc --noEmit

## Rules — Never Violate

- Use the exact status labels above in all code — no paraphrasing
- Use the exact story type labels above — no paraphrasing
- One target table per story is a hard constraint
- Backend never exposes raw Jira credentials to the frontend
- Type everything — no `Any` or untyped `dict` returns
- All Pydantic models use snake_case fields with camelCase aliases for JSON
- Always run type checks after code changes: cd backend && mypy . --ignore-missing-imports
- No speculative refactoring outside the declared session scope
- No inline styles in frontend — Tailwind only
- Commit messages use conventional commits: feat(), fix(), chore()

## What Claude Gets Wrong — Guard Against This

- Do not use the deprecated /rest/api/3/search endpoint
- Do not use requests library — use httpx with AsyncClient
- Do not hardcode Jira field paths without null-safe access
- Do not return raw Jira JSON to the frontend — always map through Pydantic models
- Do not create files outside the current session's declared scope
