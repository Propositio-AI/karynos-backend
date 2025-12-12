# Karynos Backend - AI Coding Agent Instructions

## Architecture Overview

This is a **microservices backend** with 8 independent services (dreamer, job, mentor, chat, textbook, notification, organization, user). Each service follows identical structure patterns and runs in Docker containers with dedicated PostgreSQL databases.

**Key Architectural Decisions:**
- Each service is a self-contained FastAPI application with its own DB
- Services communicate via REST API (`shared/lib/API`) or gRPC (`shared/lib/gRPC`)
- The `shared/` directory contains common code mounted as a volume into all service containers
- All services inherit from `karynos/be-python-base:latest` base image

## Project Structure Pattern

Every service follows this **exact** structure (see `services/dreamer_service/` as reference):

```
services/<service_name>/
  ├── app/
  │   ├── main.py              # FastAPI app initialization
  │   ├── crud.py              # CRUD instance declarations using shared/lib/crud
  │   ├── schemas.py           # Pydantic request/response models
  │   ├── core/
  │   │   ├── config.py        # Settings from env vars (pydantic-settings)
  │   │   └── db.py            # SQLAlchemy session creation
  │   ├── models/              # SQLAlchemy table definitions
  │   │   ├── base.py
  │   │   └── *Table.py        # Each table has its own file
  │   ├── route/
  │   │   ├── main_router.py   # Combines API & WebSocket routers
  │   │   ├── api/v1.py        # HTTP endpoints
  │   │   └── ws/v1.py         # WebSocket endpoints
  │   └── shared/              # Symlink to ../../shared (mounted in Docker)
  ├── db/
  │   └── init.sql             # Initial DB schema & triggers
  ├── .<service_name>_env      # Environment variables (not in repo, get from Google Drive)
  └── requirements.txt         # Service-specific dependencies (usually empty)
```

## Critical Development Workflows

### Build & Run Development Environment

```powershell
# First time only: Build base image
docker build -t karynos/be-python-base:latest -f ./docker/python-base.Dockerfile .

# Start all services (dev mode with hot reload)
docker compose -f ./docker/dev/docker-compose.yml up --build
```

**Important:** Services use `--reload` in development and mount `app/` as volumes for hot reloading.

### Environment Variables Setup

`.env` files are **NOT** in the repository. Download from [Google Drive](https://drive.google.com/drive/folders/12U9-36mWvZU0-SYGxlg3OeA4gWnsi3La) and place as:
- `docker/dev/.env`
- `services/<service_name>/.<service_name>_env` (e.g., `.dreamer_env`)

## Code Conventions & Patterns

### CRUD Operations

**Always use the shared CRUD class** (`shared/lib/crud/main.py`), never write raw SQLAlchemy queries:

```python
# In crud.py
from shared.lib.crud import CRUD
from core.db import session
from models.DreamerTable import DreamerTable

dreamer_crud = CRUD(session, DreamerTable)

# In route handlers
success, result, error = dreamer_crud.read([
    ["dreamer_id", "==", dreamer_id]
])
```

**Filter syntax:** `[["column_name", "operator", value], ...]`  
**Operators:** `==`, `!=`, `>`, `<`, `>=`, `<=`, `like`, `ilike`, `in`  
**Return pattern:** All CRUD methods return `(success: bool, result, error)`

### Database Models

1. Define SQLAlchemy table in `models/*Table.py`
2. Auto-generate Pydantic schema using `sqlalchemy_to_pydantic()` utility:

```python
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class DreamerTable(Base):
    __tablename__ = "dreamers"
    dreamer_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    # ... other columns

DreamerTableSchema = sqlalchemy_to_pydantic(DreamerTable)
```

**UUID Generation:** Use `shared.utils.security.gen_uuid7()` for UUIDs (UUIDv7, not v4)

### API Schemas (Pydantic)

Define separate schemas for requests/responses in `schemas.py`:

```python
class NewDreamerRequest(BaseModel):
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    
class NewDreamerResponse(BaseModel):
    dreamer_id: UUID = Field(..., description="dreamer ID")
    model_config = ConfigDict(from_attributes=True)  # Essential for ORM mapping
```

**Pattern:** `New*Request`, `New*Response`, `Update*Request`, `*Response` naming

### Error Handling

Use `@errorWrapper` decorator from `shared/lib/basicError` on all CRUD operations:

```python
from shared.lib.basicError import errorWrapper

@errorWrapper("QueryError")
def create(self, data):
    # ... implementation
    return result  # Wrapper converts to (True, result, None) or (False, None, error)
```

Error codes are defined in `shared/lib/basicError/ErrorCode.json`

### Routing Structure

Services expose versioned APIs at:
- **HTTP:** `/api/v1/<prefix>/*` (e.g., `/api/v1/dreamer/admin/new`)
- **WebSocket:** `/ws/v1/<prefix>/*`

```python
# main_router.py combines both
router.include_router(http_router, prefix=f"/api{VERSION_PREFIX}{settings.PREFIX}")
router.include_router(ws_router, prefix=f"/ws{VERSION_PREFIX}{settings.PREFIX}")
```

Prefix/tag comes from `core/config.py` settings loaded from env vars.

### gRPC Services (Textbook Service)

Special case: `textbook_service` uses gRPC instead of FastAPI:

```python
from shared.lib.gRPC import Server, Servicer

class TextbookServicer(Servicer):
    @Servicer.method(method_type="unary_stream")
    def GenerateElement(self, persona: str, structures: list):
        yield from generate_textbook(...)

server = Server(TextbookServicer())
server.serve()
```

Method types: `unary_unary` (default), `unary_stream`, `stream_unary`, `stream_stream`

### Inter-Service Communication

Use `shared/lib/API/Client` for HTTP requests between services:

```python
from shared.lib.API import Client

client = Client(key="optional_bearer_token")
success, data, error = client.post("http://user-service:8000/api/v1/users", {"name": "..."})
```

All methods (`get`, `post`, `put`, `delete`) return `(success, data, error)` tuple.

## Database Patterns

### Timestamps & Triggers

Every table should have:
```sql
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

CREATE TRIGGER update_<table>_timestamp
BEFORE UPDATE ON <table>
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();
```

Function `update_timestamp()` and `uuid_generate_v7()` are defined in each service's `db/init.sql`.

### Primary Keys

Use `UUID` with `uuid_generate_v7()` for all primary keys (UUIDv7 provides time-ordered sortability).

## Common Utilities

- **`shared/utils/security.py`:** `gen_uuid7()`, `random_string(length)`
- **`shared/utils/shema.py`:** `sqlalchemy_to_pydantic(table)` - auto-generate Pydantic models
- **`shared/utils/time.py`:** Time-related utilities
- **`shared/utils/json.py`:** JSON utilities

## Testing & Debugging

No formal test suite detected. Services log errors to stdout using `print(error, flush=True)`.

## Language & Comments

**All comments, documentation, and README files are in Japanese.** Maintain this convention when adding new code or documentation.
