# TaskForge API

[English](README.md) | [Español](README.es.md)

> A professional RESTful task management API built with Flask, SQLAlchemy, and Azure SQL Database.

## Status

[![Build and Deploy](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/main_task-forge.yml/badge.svg)](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/main_task-forge.yml)
[![Code Quality](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/code-quality.yml/badge.svg)](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/code-quality.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=bugs)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)

## About

TaskForge API is a production-grade task management REST API that demonstrates backend engineering best practices with Flask: JWT authentication, role-based access control (RBAC), comprehensive testing, SonarCloud quality gates, accessibility testing, and a CI/CD pipeline targeting Azure.

Highlights:

- RESTful API architecture with Flask and the application factory pattern
- 268 pytest tests with >73% code coverage
- SonarCloud quality analysis (bugs, vulnerabilities, code smells, coverage)
- AXE-core accessibility testing (WCAG 2.1 AA)
- JWT authentication and role-based authorization
- SQLAlchemy ORM with Azure SQL Database and SQLite fallback
- CI/CD with GitHub Actions
- Swagger/OpenAPI interactive documentation

> **Deployment note:** CI/CD is configured for Azure (deployment paused — Azure subscription expired).

## Features

- **JWT Authentication** — Full auth flow with access and refresh tokens
- **RBAC** — Admin and User roles with granular permissions
- **Task CRUD** — Title, description, priority, status, and dates
- **Tag system** — Organize tasks with customizable tags and colors
- **Advanced filtering** — By status, priority, user, tags, and dates
- **Pagination & sorting** — Server-side pagination with configurable ordering
- **Data export** — Tasks to CSV or JSON
- **Rate limiting** — Flask-Limiter abuse protection
- **CORS** — Cross-origin request support
- **Interactive docs** — Swagger/OpenAPI UI
- **Docker** — Containerized with Docker Compose

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3.1, Gunicorn (WSGI) |
| ORM | SQLAlchemy 2.0 |
| Auth | Flask-JWT-Extended (JWT), bcrypt password hashing |
| Database | Azure SQL Database (prod), SQLite (dev/test) |
| Docs | Flasgger (Swagger/OpenAPI) |
| API security | Flask-CORS, Flask-Limiter |
| Testing | pytest, pytest-cov, pytest-flask, pytest-mock |
| Quality | SonarCloud, AXE-core + Playwright (accessibility) |
| Delivery | GitHub Actions, Docker, Azure App Service |

## Architecture

```
app/
├── __init__.py          # Application factory, extensions, error/JWT handlers
├── config.py            # Environment-based configuration
├── models/              # SQLAlchemy models (user, task, tag)
├── services/            # Business logic layer (auth, task, user, tag)
├── routes/              # API blueprints (health, auth, tasks, users, tags)
├── middleware/          # Auth and RBAC decorators
└── utils/               # Pagination, validation, CSV/JSON export
tests/                   # 268 tests across 9 suites
scripts/                 # DB init script, admin password reset
docs/                    # Azure, SonarCloud, and accessibility guides
.github/workflows/       # CI/CD pipelines
```

The API follows a layered design: routes (HTTP) → services (business logic) → models (ORM), with middleware enforcing authentication and authorization.

## Endpoints

Base path: `/api`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/health` | Health check | Public |
| POST | `/auth/register` | Register a user | Public |
| POST | `/auth/login` | Login, returns access + refresh tokens | Public |
| POST | `/auth/refresh` | Refresh access token | Auth |
| POST | `/auth/logout` | Revoke refresh token | Auth |
| GET | `/auth/me` | Current user profile | Auth |
| POST | `/auth/change-password` | Change password | Auth |
| GET | `/users` | List users (paginated) | Admin |
| GET/PUT/PATCH/DELETE | `/users/<id>` | Manage a user | Admin |
| POST | `/users/<id>/deactivate` · `/activate` | Suspend/reactivate user | Admin |
| GET/POST | `/tasks` | List (filter/paginate/sort) and create tasks | Auth |
| GET/PUT/PATCH/DELETE | `/tasks/<id>` | Retrieve, update, delete a task | Auth |
| POST | `/tasks/<id>/complete` | Mark a task complete | Auth |
| GET | `/tasks/statistics` | Task stats | Auth |
| GET | `/tasks/export` | Export tasks as CSV/JSON | Auth |
| GET/POST | `/tags` | List and create tags | Auth |
| GET/PUT/PATCH/DELETE | `/tags/<id>` | Manage a tag | Auth |

Interactive docs: `http://localhost:5000/api/docs` (Swagger UI)

## Run Locally

**Prerequisites:** Python 3.11+, Azure SQL Database (or SQLite for local dev), optional Docker.

```bash
git clone https://github.com/YamiDarknezz/task-forge-api.git
cd task-forge-api

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt

copy .env.example .env      # Windows
cp .env.example .env        # Linux/Mac
# then edit .env with your configuration
```

Initialize the database:

```bash
flask init-db               # SQLite (local dev)
# or run scripts/init_db_azure.sql against Azure SQL
```

Run the app:

```bash
python run.py               # API at http://localhost:5000
```

Or with Docker:

```bash
docker-compose up --build   # API at http://localhost:5000
```

## Environment Variables

Configure a `.env` file based on `.env.example`:

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=taskforge_db
AZURE_SQL_USER=your-user
AZURE_SQL_PASSWORD=YourPassword123
AZURE_SQL_PORT=1433

JWT_ACCESS_TOKEN_EXPIRES=3600        # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=2592000    # 30 days

RATELIMIT_ENABLED=true
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=200 per day;50 per hour

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Running Tests

```bash
pytest                                  # full suite (268 tests)
pytest --cov=app --cov-report=term      # with coverage report
pytest tests/test_auth.py               # single suite
pytest -v                               # verbose output
```

Results: **268 tests passing**, **>73% coverage** (1,053+ / 1,441 lines), with suites for auth, tasks, users, tags, services, models, middleware, helpers, and validators.

Accessibility checks (local):

```powershell
.\tests\accessibility\run-axe-local.ps1
```

## CI/CD

Two GitHub Actions workflows:

1. **Code Quality** (`code-quality.yml`) — runs on every push/PR: SonarCloud analysis and AXE accessibility tests.
2. **Azure Deployment** (`main_task-forge.yml`) — runs on push to `main`: build → test (requires >70% coverage) → deploy to Azure App Service (Linux, Python 3.11, Gunicorn) via OIDC.

> Deployment is currently paused because the Azure subscription expired; the pipeline remains fully configured.

Secrets required: `AZUREAPPSERVICE_CLIENTID_*`, `AZUREAPPSERVICE_TENANTID_*`, `AZUREAPPSERVICE_SUBSCRIPTIONID_*` (Azure), `SONAR_TOKEN` (SonarCloud).

## Quality & Security

- **SonarCloud** — automatic analysis of bugs, vulnerabilities, code smells, coverage, and duplications on every push/PR ([dashboard](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api))
- **Security** — bcrypt-hashed passwords, expiring JWT tokens, RBAC, rate limiting, CORS configuration, SQL injection protection via ORM, revocable refresh tokens, forced HTTPS and debug disabled in production

## License

MIT

## Author

**Erick (YamiDarknezz)** — [GitHub](https://github.com/YamiDarknezz) · [TaskForge API](https://github.com/YamiDarknezz/task-forge-api)
