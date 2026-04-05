# Session 1 — Jira Integration

## Pre-Session Setup

### Step 1 — Gather Your Jira Credentials

You need four values:

```
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=your-email@org.com
JIRA_API_TOKEN=<generate at https://id.atlassian.com/manage-profile/security/api-tokens>
```

Auth note: Jira Cloud Basic Auth uses `base64(email:api_token)` in the
Authorization header. With Basic Auth, Jira ignores OAuth scopes — your
request inherits your Jira account's project permissions.

## Goal

Answer one question: "Can my backend talk to Jira and get data back?"

## What This Sub-Session Produces

- FastAPI app skeleton running on port 8000
- Pydantic BaseSettings config loading from .env
- httpx async Jira client that can POST to `/rest/api/3/search/jql`
- Health endpoint confirming Jira reachability
- A temporary debug endpoint that returns raw Jira JSON (so you can see
  your project's actual field names, status names, and custom field IDs)
- No mapper, no Story model, no cache, no /api/stories endpoint

## Session 1a — Planning Prompt

Open Claude Code from `agentic-de/` root:

```bash
claude
```

Paste this:

```
Read CLAUDE.md first. Do not write any code until I approve your plan.

SESSION SCOPE: Scaffold the FastAPI backend and prove Jira Cloud connectivity.
This is the first of two sub-sessions. This sub-session builds only the
scaffold and a connectivity proof. The stories endpoint comes in Session 1b.

WHAT TO BUILD:

1. backend/ directory structure:
   backend/
     main.py                  # FastAPI app, CORS, lifespan for httpx client
     config.py                # Pydantic BaseSettings loading from ../.env
     routers/
       __init__.py
       health.py              # GET /health
       debug.py               # GET /api/debug/jira-raw (TEMPORARY — removed in 1b)
     services/
       __init__.py
       jira_client.py         # Async Jira API client
     requirements.txt
   .env.example
   .gitignore

2. config.py — Pydantic BaseSettings:
   - Fields: JIRA_BASE_URL (str), JIRA_EMAIL (str), JIRA_API_TOKEN (str),
     JIRA_PROJECT_KEY (str), CORS_ORIGINS (list[str], default ["http://localhost:5173"])
   - Load from ../.env using python-dotenv
   - Validate JIRA_BASE_URL does not end with trailing slash
   - Validate JIRA_PROJECT_KEY is not empty

3. jira_client.py — Async Jira API client:
   - Class: JiraClient
   - Constructor takes Settings, creates httpx.AsyncClient with:
     - Base URL from settings
     - Authorization header: "Basic " + base64(email:api_token)
     - Content-Type: application/json
     - Accept: application/json
     - Timeout: 15s connect, 30s read
   - Method: async def search(self, jql: str, max_results: int = 50,
     fields: list[str] | None = None) -> dict
     - POST to /rest/api/3/search/jql
     - Request body: {"jql": jql, "maxResults": max_results}
     - If fields provided, add "fields": fields to the body
     - Returns the full JSON response as a dict
     - On 401/403: raise JiraAuthError with message including the status code
     - On 5xx or timeout: raise JiraUnavailableError
     - These are custom exceptions defined in a services/exceptions.py file
   - Method: async def check_reachable(self) -> bool
     - GET to /rest/api/3/serverInfo with 5s timeout
     - Returns True if 200, False otherwise (catch all exceptions)
   - Method: async def close(self)
     - Closes the httpx.AsyncClient

4. main.py — FastAPI app:
   - Create Settings instance on startup
   - Use lifespan context manager to create JiraClient on startup,
     store on app.state, close on shutdown
   - CORS middleware: allow origins from settings.CORS_ORIGINS,
     allow methods GET and OPTIONS, allow headers Content-Type
   - Include health and debug routers

5. health.py — GET /health:
   - Returns: {"status": "healthy", "jira_reachable": bool}
   - Calls jira_client.check_reachable() to determine jira_reachable

6. debug.py — GET /api/debug/jira-raw (TEMPORARY):
   - This endpoint exists ONLY so I can inspect my real Jira JSON structure.
   - Calls jira_client.search with:
     jql = f"project={settings.JIRA_PROJECT_KEY} ORDER BY updated DESC"
     max_results = 3
     fields = ["summary", "status", "issuetype", "assignee", "reporter",
               "updated", "labels", "priority"]
   - Returns the raw Jira JSON response — no mapping, no transformation
   - Query param: ?include_custom_fields=true adds "*all" to fields list
     so I can find my custom field IDs
   - This file will be deleted in Session 1b

7. .env.example:
   JIRA_BASE_URL=https://your-org.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   JIRA_PROJECT_KEY=DE
   CORS_ORIGINS=["http://localhost:5173"]

8. .gitignore:
   .env
   __pycache__/
   *.pyc
   .mypy_cache/
   .pytest_cache/
   venv/
   .venv/

9. requirements.txt:
   fastapi>=0.115.0
   uvicorn[standard]>=0.30.0
   httpx>=0.27.0
   python-dotenv>=1.0.0
   pydantic>=2.9.0
   pydantic-settings>=2.5.0

DO NOT BUILD in this sub-session:
- No Pydantic Story response models (that's Session 1b)
- No jira_mapper.py (that's Session 1b)
- No /api/stories endpoint (that's Session 1b)
- No caching (that's Session 1b)
- No frontend code
- No database, no migrations
- No Docker/Podman files
- No tests

PLAN FORMAT:
- Help me to learn and write class after class, function after function - step by step
- i want write the code since i am new to this tech stack, you can only write if i explicitly ask for it.
-
```

---

## Session 1a — Plan Review Checklist

Before saying "Plan approved", verify these:

### ✓ Jira API endpoint

Claude must use `POST /rest/api/3/search/jql`. If you see
`GET /rest/api/3/search?jql=...` with query params, reject:

```
Stop. /rest/api/3/search is deprecated. Use POST /rest/api/3/search/jql.
The JQL goes in the request body as {"jql": "..."}, not as a query parameter.
Rewrite the plan.
```

### ✓ httpx.AsyncClient lifecycle

The client must be created once in the lifespan, not per-request:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.jira_client = JiraClient(settings)
    yield
    await app.state.jira_client.close()
```

If Claude creates `async with httpx.AsyncClient() as client:` inside a route
handler, reject — this creates and destroys a TCP connection per request.

### ✓ Auth header

Must be `"Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()`.
If Claude uses `httpx.BasicAuth(email, token)`, that's also fine — httpx
handles the encoding internally.

### ✓ Custom exceptions

Should be in a separate `services/exceptions.py`, not inline in jira_client.py.
This keeps the client clean and makes error handling composable for Session 1b.

### ✓ No Story models

The plan should NOT include any Pydantic Story/StoryAssignee models.
Those are Session 1b. If Claude adds them, say:

```
Remove the Story models. Session 1a returns raw Jira JSON via the
debug endpoint. The Story model is Session 1b scope.
```

---

## Session 1a — Approval Prompt

```
Plan approved. Implement it. After creating all files, show me:
1. The exact curl command to test GET /health
2. The exact curl command to test GET /api/debug/jira-raw
3. The exact curl command to test GET /api/debug/jira-raw?include_custom_fields=true
```

---

## Session 1a — Post-Implementation Verification

### Step 1 — Install

```bash
cd backend && pip install -r requirements.txt
```

### Step 2 — Create .env

```bash
cp .env.example ../.env
# Edit ../.env with your real Jira credentials
```

### Step 3 — Start server

```bash
cd backend && uvicorn main:app --reload --port 8000
```

### Step 4 — Test health

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

Expected:

```json
{
  "status": "healthy",
  "jira_reachable": true
}
```

If `jira_reachable` is `false`:

- Check JIRA_BASE_URL in .env (no trailing slash)
- Verify your API token at https://id.atlassian.com/manage-profile/security/api-tokens
- Check network connectivity (VPN, proxy)
- Look at the uvicorn terminal for error details

### Step 5 — Test raw Jira output

```bash
curl http://localhost:8000/api/debug/jira-raw | python3 -m json.tool
```

This is the critical step. Study the output carefully. You need to identify:

**A. Your status names**

Find the `status` field in each issue. Note down every status name your
project uses. Example — you might see:

```json
"status": {
    "name": "Backlog",
    ...
}
```

Write these down. You'll create the STATUS_MAP in Session 1b.

My canonical labels → Your Jira status names:

```
Draft                        → _______________
Analyzing                    → _______________
In Review — BA               → _______________
Agent-Ready                  → _______________
Agent Running                → _______________
Awaiting Code Review         → _______________
Awaiting Test Review         → _______________
Awaiting Validation Review   → _______________
PR Submitted                 → _______________
```

Note: Not all canonical labels may have a Jira equivalent yet. That's fine.
Map what exists. Unmapped Jira statuses will default to "Draft".

**B. Your custom field IDs**

```bash
curl "http://localhost:8000/api/debug/jira-raw?include_custom_fields=true" | python3 -m json.tool
```

Look through the `customfield_XXXXX` entries for anything that looks like
it could hold:

- Target table name (e.g. "gold.sales_summary")
- Iteration count or cycle count
- BA assignment (if not using reporter)

Write down the custom field IDs:

```
Target table field:    customfield_________
Iteration count field: customfield_________ (or none — default to 0)
BA assignment field:   customfield_________ (or use reporter)
```

If none of these custom fields exist in your Jira project, that's fine.
Session 1b will use fallbacks (labels for target_table, reporter for BA,
0 for iteration_count).

**C. Your issue type names**

Note the `issuetype.name` values. You may see "Story", "Task", "Bug", etc.
Your platform uses custom story types (Schema Change, Transformation Change,
etc.) — you'll need to decide in Session 1b whether these come from:

- Jira issue types (if you've configured custom ones)
- A label prefix (e.g. "type:Schema Change")
- A custom field

### Step 6 — Save your findings

Create a temporary file to carry this knowledge into Session 1b:

```bash
cat > JIRA_FIELD_MAPPING.md << 'EOF'
# Jira Field Mapping — Discovered in Session 1a

## Status Names (from my Jira project)
| Jira Status Name     | Maps To (Canonical)          |
|----------------------|------------------------------|
| TODO                 | Draft                        |
| ...                  | ...                          |

## Custom Fields
| Purpose              | Field ID                     |
|----------------------|------------------------------|
| Target table         | (field ID or "use labels")   |
| Iteration count      | (field ID or "default to 0") |
| BA assignment        | (field ID or "use reporter") |

## Issue Types
| Jira Type Name       | Maps To (Canonical)          |
|----------------------|------------------------------|
| Story                | (decide)                     |
| Bug                  | Bug Fix                      |
| ...                  | ...                          |
EOF
```

Edit this file with your real values.

### Step 7 — Commit

```bash
cd ..
git add backend/ .env.example .gitignore JIRA_FIELD_MAPPING.md
git commit -m "feat(backend): FastAPI scaffold + Jira connectivity proof"
```

---

## What You Have After Session 1a

| Capability                                  | Status |
| ------------------------------------------- | ------ |
| FastAPI running on port 8000                | ✅     |
| Pydantic BaseSettings config                | ✅     |
| httpx async Jira client (connection pooled) | ✅     |
| POST /rest/api/3/search/jql (correct API)   | ✅     |
| Health endpoint with Jira reachability      | ✅     |
| Debug endpoint showing raw Jira JSON        | ✅     |
| Custom field IDs identified                 | ✅     |
| Status name mapping documented              | ✅     |
| .gitignore protecting .env                  | ✅     |

---

---

# SESSION 1b — Mapper + Stories Endpoint + Cache

## Goal

Build the Stories API endpoint that the frontend dashboard will consume.
All unknowns from 1a are resolved — you know your field paths, status names,
and custom field IDs.

## What This Sub-Session Produces

- Pydantic Story and StoriesResponse models
- Jira-to-Story mapper using your real field mapping
- GET /api/stories endpoint with TTL cache
- Debug endpoint removed (no longer needed)

## Prerequisite

You must have completed Session 1a and filled in `JIRA_FIELD_MAPPING.md`
with your real Jira field paths, status names, and custom field IDs.

## Session 1b — Planning Prompt

Open a new Claude Code session:

```bash
claude
```

Paste this — **but first, fill in the three placeholder sections marked
with <<<FILL THIS IN>>> using your JIRA_FIELD_MAPPING.md findings**:

```
Read CLAUDE.md first.
Then read JIRA_FIELD_MAPPING.md — it contains field mapping data
I discovered from the Session 1a debug endpoint.
Do not write any code until I approve your plan.

SESSION SCOPE: Build the Story response models, Jira-to-Story mapper,
and the /api/stories endpoint with caching. This completes the backend
for the dashboard. Remove the debug endpoint from Session 1a.

EXISTING FILES (do not recreate — read them first):
- backend/main.py
- backend/config.py
- backend/services/jira_client.py
- backend/services/exceptions.py
- backend/routers/health.py

WHAT TO BUILD:

1. backend/models/__init__.py
2. backend/models/story.py — Pydantic response models:

   class StoryAssignee(BaseModel):
       name: str
       email: str | None = None

   class Story(BaseModel):
       id: str                              # Jira issue ID
       key: str                             # e.g. "DE-1042"
       title: str                           # summary
       story_type: str                      # canonical type label
       status: str                          # canonical lifecycle label
       target_table: str | None = None      # Hive target table
       assignee_de: StoryAssignee | None    # Data Engineer
       assignee_ba: StoryAssignee | None    # Business Analyst
       iteration_count: int = 0             # A&A iteration count
       updated: str                         # ISO 8601
       jira_url: str                        # deep link to Jira

   class StoriesResponse(BaseModel):
       stories: list[Story]
       total: int
       cached: bool                         # whether response came from cache

3. backend/services/jira_mapper.py — Maps raw Jira JSON to Story models:

   STATUS_MAP — use these exact mappings from my Jira project:
   <<<FILL THIS IN: paste your status mapping table, e.g.
   {
       "Backlog": "Draft",
       "To Do": "Draft",
       "In Progress": "Analyzing",
       "In Review": "In Review — BA",
       "Ready for Dev": "Agent-Ready",
       "Done": "PR Submitted",
   }
   >>>

   TYPE_MAP — use these mappings:
   <<<FILL THIS IN: paste your issue type mapping, e.g.
   {
       "Story": "Schema Change",
       "Bug": "Bug Fix",
       "Task": "Transformation Change",
   }
   Or if you're using labels/custom fields for story type, describe the
   extraction logic here instead.
   >>>

   Target table extraction:
   <<<FILL THIS IN: describe how to get the target table, e.g.
   "Use customfield_10089 if present. If null, look for a Jira label
   prefixed with 'table:' (e.g. label 'table:gold.sales_summary' →
   'gold.sales_summary'). If neither exists, return None."
   >>>

   Function: def map_issue_to_story(raw_issue: dict, jira_base_url: str) -> Story
   - Null-safe access at every level
   - Every dict access must use .get() with fallbacks
   - Unmapped status names default to "Draft"
   - Unmapped issue types pass through as-is (do not drop them)
   - jira_url = f"{jira_base_url}/browse/{key}"
   - assignee_de: from the issue's assignee field
   - assignee_ba: from reporter field (or custom field if specified above)
   - iteration_count: default 0 (will come from PostgreSQL in a later session)

   Function: def map_issues_to_stories(raw_response: dict, jira_base_url: str) -> list[Story]
   - Iterates over raw_response["issues"], calls map_issue_to_story for each
   - Wraps each call in try/except — if a single issue fails to map,
     log a warning and skip it (do not crash the entire response)

4. Update backend/services/jira_client.py:
   - Add method: async def fetch_stories(self) -> dict
     - JQL: f"project={self.settings.JIRA_PROJECT_KEY} ORDER BY updated DESC"
     - Fields: ["summary", "status", "issuetype", "assignee", "reporter",
                "updated", "labels", "priority"
                <<< plus any custom field IDs you identified >>>]
     - maxResults: 100
     - Handles pagination: if nextPageToken is present, fetch next page
       and merge the issues arrays
     - Returns the merged raw response dict

5. backend/routers/stories.py — GET /api/stories:
   - Query param: refresh (bool, default False) — bypasses cache if True
   - Uses an in-memory TTL cache:
     - Module-level cachetools.TTLCache (maxsize=1, ttl from settings)
     - Cache key: static string "stories" (only one project)
     - Caches the StoriesResponse, not raw JSON
   - Flow: check cache → if miss or refresh, call jira_client.fetch_stories(),
     map with jira_mapper, build StoriesResponse, store in cache
   - On JiraUnavailableError: return 503 with {"detail": "Jira is unreachable"}
   - On JiraAuthError: return 502 with {"detail": "Jira authentication failed"}

6. Update backend/config.py:
   - Add field: CACHE_TTL_SECONDS (int, default 60)

7. Update backend/main.py:
   - Add stories router
   - Remove debug router import and include

8. DELETE backend/routers/debug.py — it was temporary for Session 1a

9. Update requirements.txt — add:
   cachetools>=5.5.0

DO NOT BUILD:
- No frontend code
- No database or migrations
- No Docker/Podman files
- No tests
- No new endpoints beyond /api/stories
- Do not modify health.py

PLAN FORMAT:
List every file you will create or modify.
For each file, list every class/function and its signature.
Show the complete STATUS_MAP and TYPE_MAP dicts.
Show the complete map_issue_to_story function logic (pseudocode is fine).
Show the cache implementation approach.
Wait for my approval before writing any code.
```

---

## Session 1b — Plan Review Checklist

### ✓ STATUS_MAP matches your Jira

Every status name from your project should appear as a key. Check that no
canonical labels are used as keys (they're the values, not the keys).

### ✓ Null-safe field access everywhere

The mapper must not have any direct dict access like `issue["fields"]["assignee"]["displayName"]`.
Every level must use `.get()`:

```python
fields = issue.get("fields") or {}
assignee_raw = fields.get("assignee") or {}
name = assignee_raw.get("displayName", "Unassigned")
```

If Claude writes direct bracket access, say:

```
The mapper has unsafe dict access. Jira returns null for assignee on
unassigned issues, null for custom fields that aren't set, and sometimes
omits fields entirely. Every single dict access must use .get() with a
fallback. Rewrite the mapper with null-safe access at every level.
```

### ✓ Per-issue error handling

`map_issues_to_stories` must wrap each issue mapping in try/except.
One malformed issue should not crash the entire response:

```python
for raw_issue in raw_response.get("issues", []):
    try:
        stories.append(map_issue_to_story(raw_issue, jira_base_url))
    except Exception as e:
        logger.warning(f"Failed to map issue: {e}")
```

### ✓ Pagination handling

`fetch_stories` must handle `nextPageToken`. Check that Claude loops:

```python
all_issues = []
next_token = None
while True:
    body = {"jql": jql, "maxResults": 100, "fields": fields}
    if next_token:
        body["nextPageToken"] = next_token
    response = await self.client.post(url, json=body)
    data = response.json()
    all_issues.extend(data.get("issues", []))
    next_token = data.get("nextPageToken")
    if not next_token:
        break
```

If Claude uses `startAt` offset pagination, reject immediately.

### ✓ Cache is module-level

The TTLCache must be at module level in stories.py, NOT inside the route
handler function. If it's inside the function, it resets on every request.

### ✓ debug.py is deleted

Claude should remove the debug router from main.py AND delete the file.

---

## Session 1b — Approval Prompt

```
Plan approved. Implement it. After creating/modifying all files, show me:
1. The exact curl command to test GET /api/stories
2. The exact curl command to test GET /api/stories?refresh=true
3. Confirm that debug.py has been deleted and removed from main.py
```

---

## Session 1b — Post-Implementation Verification

### Step 1 — Install new dependency

```bash
cd backend && pip install -r requirements.txt
```

### Step 2 — Restart server

```bash
uvicorn main:app --reload --port 8000
```

### Step 3 — Test stories endpoint

```bash
curl http://localhost:8000/api/stories | python3 -m json.tool
```

Check each story in the response:

- `key` looks like "DE-1042" (your project prefix + number)
- `status` is one of your canonical labels (Draft, Analyzing, etc.),
  NOT a raw Jira status name
- `story_type` is mapped correctly
- `jira_url` opens the correct Jira issue in your browser
- `target_table` is populated (or null if not configured)
- `assignee_de` and `assignee_ba` have names (or null for unassigned)
- `cached` is `false` (first request)

### Step 4 — Test cache

```bash
# Second request — should be cached
curl http://localhost:8000/api/stories | python3 -m json.tool
# Check: "cached": true

# Force refresh
curl "http://localhost:8000/api/stories?refresh=true" | python3 -m json.tool
# Check: "cached": false
```

### Step 5 — Test error handling

```bash
# Temporarily break your Jira token in .env, restart server
curl http://localhost:8000/api/stories
# Should return 502 with "Jira authentication failed", not a stack trace
```

Fix your .env back after this test.

### Step 6 — Verify debug endpoint is gone

```bash
curl http://localhost:8000/api/debug/jira-raw
# Should return 404, not the raw Jira JSON
```

### Step 7 — Test CORS

```bash
curl -I -X OPTIONS http://localhost:8000/api/stories \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET"
```

Check: `Access-Control-Allow-Origin: http://localhost:5173` in response headers.

---

## Commit

```bash
cd ..
git add backend/
git commit -m "feat(backend): story models, Jira mapper, /api/stories with TTL cache"
git tag v0.1.0-backend
```

---

## What You Have After Session 1b

| Capability                                    | Status |
| --------------------------------------------- | ------ |
| FastAPI running on port 8000                  | ✅     |
| Jira Cloud integration (correct search/jql)   | ✅     |
| Pydantic-typed Story response model           | ✅     |
| target_table + iteration_count in response    | ✅     |
| Jira-agnostic mapper (swappable data source)  | ✅     |
| Null-safe field mapping with per-issue safety | ✅     |
| Status names mapped to canonical labels       | ✅     |
| 60-second TTL cache with manual refresh       | ✅     |
| Health endpoint with Jira reachability        | ✅     |
| CORS configured for Vite dev server           | ✅     |
| Debug endpoint removed                        | ✅     |

---

## Troubleshooting Reference

### Claude uses the deprecated Jira endpoint

If Claude writes code using `GET /rest/api/3/search`, paste this:

```
Stop. The /rest/api/3/search endpoint is deprecated since August 2025.
Use POST /rest/api/3/search/jql instead. The request body takes
{"jql": "...", "maxResults": N, "fields": [...]} and pagination uses
nextPageToken, not startAt. Rewrite jira_client.py.
```

### Module not found errors

Claude sometimes forgets `__init__.py` files. Check:

```bash
ls backend/routers/__init__.py
ls backend/services/__init__.py
ls backend/models/__init__.py
```

### Jira returns 401

API token is wrong or expired. Regenerate at:
https://id.atlassian.com/manage-profile/security/api-tokens

### Jira returns empty results

JIRA_PROJECT_KEY doesn't match any project, or the authenticated user
doesn't have browse permission. Test directly:

```bash
curl -X POST "https://your-org.atlassian.net/rest/api/3/search/jql" \
  -H "Authorization: Basic $(echo -n 'email:token' | base64)" \
  -H "Content-Type: application/json" \
  -d '{"jql": "project=DE", "maxResults": 3}'
```

### Status values show raw Jira names instead of canonical labels

Your STATUS_MAP keys don't match your actual Jira status names.
Re-run the debug endpoint from Session 1a to check exact names
(status names are case-sensitive).

### All target_table values are null

Your custom field ID is wrong, or you're not using labels with "table:" prefix.
Re-run the debug endpoint with `?include_custom_fields=true` to inspect.

---
