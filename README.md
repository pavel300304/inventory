# inventory-practice

A small inventory and orders API that serves two separate businesses (tenants) from one codebase and one database. The core rule: one tenant must never see or change another tenant's data.

This is a 14-day practice project. It is built step by step, and this README is updated as each part starts working.

## Status

**Day 1 — project skeleton only. Nothing runs yet.**

- [ ] Database connection (`app/db.py`)
- [ ] Schema migrations (Alembic)
- [ ] Inventory endpoints
- [ ] Order endpoints
- [ ] Tokens and tenant checks (`app/auth.py`)
- [ ] Tests (pytest)
- [ ] Dockerfile and `compose.yaml`
- [ ] CI pipeline (GitHub Actions)

## Stack

| Part | Tool |
| --- | --- |
| Language | Python |
| API framework | FastAPI |
| Database | PostgreSQL |
| Migrations | Alembic |
| Tests | pytest |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions |

## Project layout

```text
inventory-practice/
├── app/
│   ├── main.py           # the API endpoints
│   ├── db.py             # database connection
│   └── auth.py           # tokens and tenant checks
├── migrations/           # Alembic schema changes
├── tests/                # pytest tests
├── .github/workflows/    # CI pipeline
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env                  # local secrets, never committed
├── .gitignore
├── README.md
└── NOTES.md              # daily explanations
```

## How tenant isolation works

_To be written once `auth.py` exists._ The plan:

1. Every request carries a token.
2. The token identifies which tenant the caller belongs to.
3. Every database query is filtered by that tenant, so a request can only reach its own tenant's rows.
4. Tests prove it: tenant A asks for tenant B's data and gets nothing back.

## Running locally

_Not working yet. These are the intended steps and will be confirmed as each part lands._

```bash
# 1. Create local secrets (never committed)
cp .env.example .env

# 2. Start the API and the database
docker compose up --build

# 3. Apply schema migrations
docker compose exec api alembic upgrade head
```

The API will then be at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## Running the tests

_Not working yet._

```bash
pytest
```

## Configuration

Settings are read from `.env`, which is listed in `.gitignore`.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Key used to sign tokens |

_Variable names are placeholders until `db.py` and `auth.py` are written._

## API

_No endpoints yet. This table is filled in as they are built._

| Method | Path | What it does |
| --- | --- | --- |
| | | |

## Notes

Daily explanations of what was built and why are in [NOTES.md](NOTES.md).