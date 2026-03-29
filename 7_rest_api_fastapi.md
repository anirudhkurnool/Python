# Production-Grade REST APIs with Python and FastAPI

A comprehensive revision handbook for designing, building, testing, deploying, and operating production-grade REST APIs with Python and FastAPI.

---

## Table of Contents

1. [What REST is, and when to use it](#1-what-rest-is-and-when-to-use-it)  
2. [When not to use REST](#2-when-not-to-use-rest)  
3. [REST and HTTP fundamentals you must know](#3-rest-and-http-fundamentals-you-must-know)  
4. [Core design principles for a production API](#4-core-design-principles-for-a-production-api)  
5. [Recommended production architecture for FastAPI](#5-recommended-production-architecture-for-fastapi)  
6. [Project structure](#6-project-structure)  
7. [Configuration and environment management](#7-configuration-and-environment-management)  
8. [FastAPI application setup](#8-fastapi-application-setup)  
9. [Request/response modeling with Pydantic](#9-requestresponse-modeling-with-pydantic)  
10. [Validation strategy](#10-validation-strategy)  
11. [Dependency injection](#11-dependency-injection)  
12. [Routing and API organization](#12-routing-and-api-organization)  
13. [Error handling](#13-error-handling)  
14. [Authentication, authorization, and security](#14-authentication-authorization-and-security)  
15. [Database access, transactions, and migrations](#15-database-access-transactions-and-migrations)  
16. [Pagination, filtering, sorting, and search](#16-pagination-filtering-sorting-and-search)  
17. [Caching, idempotency, and concurrency control](#17-caching-idempotency-and-concurrency-control)  
18. [Files, streaming, and background work](#18-files-streaming-and-background-work)  
19. [Documentation and API contracts](#19-documentation-and-api-contracts)  
20. [Testing strategy](#20-testing-strategy)  
21. [Observability](#21-observability)  
22. [Performance and scalability](#22-performance-and-scalability)  
23. [Deployment and runtime operations](#23-deployment-and-runtime-operations)  
24. [CI/CD and release management](#24-cicd-and-release-management)  
25. [Production operations checklist](#25-production-operations-checklist)  
26. [Common mistakes and anti-patterns](#26-common-mistakes-and-anti-patterns)  
27. [A practical build order](#27-a-practical-build-order)  
28. [Minimal production blueprint](#28-minimal-production-blueprint)  
29. [Authoritative references](#29-authoritative-references)  

---

## 1. What REST is, and when to use it

### What REST actually means

REST is not “just JSON over HTTP.” In practice, a good REST API is:

- **resource-oriented**: it exposes resources such as `users`, `orders`, `invoices`, `products`
- **HTTP-native**: it uses HTTP methods, status codes, headers, caching, and conditional requests correctly
- **stateless**: each request contains everything the server needs to understand it
- **contract-driven**: clients rely on stable representations and semantics
- **cache-aware**: safe reads can often benefit from HTTP caching
- **operationally simple**: HTTP tooling, proxies, CDNs, auth gateways, and debuggers work well with it

Strict academic REST includes hypermedia constraints, but most real production APIs are **pragmatic REST**: resource-oriented HTTP APIs with stable semantics and predictable contracts.

### Use REST when

REST is usually the right default when most of the following are true:

- You are exposing **resources** and standard CRUD-style operations.
- Clients are heterogeneous: browser apps, mobile apps, partner integrations, scripts, internal tools.
- You want an API that is easy to inspect with standard HTTP tools.
- You benefit from HTTP semantics such as:
  - cacheability for reads
  - idempotent updates/deletes
  - conditional requests
  - authentication and proxy infrastructure
- Your API must be understandable by teams that did not build it.
- You need strong interoperability with API gateways, load balancers, reverse proxies, WAFs, and observability systems.
- Your domain maps well to nouns and state transitions rather than arbitrary remote procedure calls.
- You want OpenAPI-based documentation, client generation, testing, and governance.

### REST is especially strong for

- Public APIs
- Partner APIs
- B2B integrations
- Backends for web/mobile apps with mostly request/response behavior
- Admin/internal control planes
- CRUD-heavy line-of-business systems
- APIs where caching, pagination, filters, and stable contracts matter more than query flexibility

### A good rule of thumb

If your API is mostly:

- “create/read/update/delete a resource”
- “list resources with filters”
- “perform a business action on a resource”
- “return representations that should be stable and documented”

then REST is usually the right first choice.

---

## 2. When not to use REST

REST is not always the best interface. Do **not** force everything into REST.

### Prefer GraphQL when

Use GraphQL when clients need **highly variable, graph-shaped reads** across related entities and over-fetching/under-fetching is a real problem.

Examples:

- complex frontend pages assembling many related entities
- mobile clients that need tight control over payload shape
- product experiences where the UI composition changes frequently

Why: GraphQL lets clients request exactly the data they need and follow relationships in one request.

Do **not** pick GraphQL just because it is fashionable. It adds complexity in query planning, authorization, caching, operational limits, and N+1 avoidance.

### Prefer gRPC when

Use gRPC for **low-latency, strongly typed, service-to-service communication**, especially internally.

Examples:

- microservice-to-microservice calls in a controlled environment
- streaming RPCs
- performance-sensitive internal systems
- polyglot systems with strict interface contracts and code generation

Why: gRPC is optimized around RPC semantics, binary transport, generated clients, and streaming.

Do not expose gRPC as your only external/public API unless your consumers can support it operationally.

### Prefer WebSockets or similar real-time channels when

Use WebSockets when you need **bidirectional, real-time communication**.

Examples:

- chat
- multiplayer collaboration
- live dashboards
- real-time trading or presence updates
- server push without polling

Why: REST is request/response. Real-time bidirectional messaging is a different interaction model.

### Prefer event-driven architecture when

Use message brokers/queues/events when work is **asynchronous, decoupled, retried, or long-running**.

Examples:

- order processing pipelines
- email delivery
- analytics ingestion
- image/video processing
- webhook fanout
- fraud analysis
- batch enrichments

In many systems, the right answer is hybrid:

- **REST** to accept the command or create the job
- **queue/events** to execute the work
- **REST** again to query job status

### Prefer object storage or batch interfaces when

Do not use REST endpoints as the main transport for huge data exchanges if object storage, signed URLs, batch ingestion, or file-based pipelines are more appropriate.

Examples:

- large CSV/Parquet imports/exports
- backups
- media uploads/downloads at scale
- ML datasets

### Avoid REST as the only abstraction when

REST is a poor fit when:

- the system is primarily command-oriented rather than resource-oriented
- interactions are long-lived and conversational
- the contract needs streaming in both directions
- performance depends on binary protocols and generated stubs
- client read requirements differ drastically across many screens and products

### Decision table

| Need | Best default |
|---|---|
| Standard resource CRUD over HTTP | REST |
| Client-specific graph reads | GraphQL |
| Internal strongly typed RPC and streaming | gRPC |
| Real-time bidirectional messaging | WebSockets / real-time transport |
| Long-running decoupled workflows | Queue / events |
| Very large file or batch transfer | Object storage / batch pipeline |
| Public or partner-friendly HTTP integration | REST |

---

## 3. REST and HTTP fundamentals you must know

This section matters. Many “REST APIs” are actually just RPC over HTTP because teams ignore HTTP semantics.

### Resources vs actions

Prefer nouns over verbs:

- Good: `/users`, `/orders/{id}`, `/invoices/{id}/payments`
- Usually bad: `/createUser`, `/getOrders`, `/deleteInvoice`

If you need an action, model it carefully:

- `POST /orders/{id}/cancel`
- `POST /payments/{id}/refund`

This is acceptable when the action is a domain command that does not fit cleanly as a CRUD replacement.

### Method semantics

#### GET
Use for safe reads.

- Must not change server state as part of the requested semantics.
- Should be cache-friendly where possible.
- Do not design APIs that depend on GET request bodies.

Examples:
- `GET /users/123`
- `GET /orders?status=paid&limit=50`

#### POST
Use for non-idempotent processing, creation without client-chosen URI, or action submission.

Examples:
- `POST /users`
- `POST /orders/{id}/cancel`
- `POST /jobs`

#### PUT
Use for **full replacement** of a resource representation at a known URI.

Example:
- `PUT /profiles/{user_id}`

Do not use PUT if your semantics are partial update.

#### PATCH
Use for partial update.

Example:
- `PATCH /users/123`

Define PATCH semantics clearly. Do not make it a mystery bag of side effects.

#### DELETE
Use to remove a resource or mark it deleted according to your domain.

Example:
- `DELETE /sessions/{id}`

#### HEAD
Use when clients only need headers/metadata.

#### OPTIONS
Useful for capability discovery and browser preflight handling.

### Safe and idempotent methods

Know the difference:

- **Safe** means read-only in requested semantics: GET, HEAD, OPTIONS, TRACE.
- **Idempotent** means repeated identical requests have the same intended effect: PUT, DELETE, and safe methods.

This matters for retries, gateways, clients, and load balancers.

### Status code discipline

Use the right class of status codes:

#### 2xx success
- `200 OK`: generic successful read/update with body
- `201 Created`: new resource created; include `Location` when appropriate
- `202 Accepted`: work accepted but not completed yet
- `204 No Content`: success without response body

#### 4xx client errors
- `400 Bad Request`: malformed request
- `401 Unauthorized`: authentication required or invalid
- `403 Forbidden`: authenticated but not allowed
- `404 Not Found`: resource absent or intentionally undisclosed
- `409 Conflict`: state conflict, uniqueness violation, invalid transition
- `412 Precondition Failed`: failed ETag/conditional update
- `415 Unsupported Media Type`: wrong content type
- `422 Unprocessable Content`: syntactically valid payload but semantic validation failure

FastAPI commonly returns `422` for request validation failures.

#### 5xx server errors
- `500 Internal Server Error`: unexpected server failure
- `502/503/504`: upstream or availability issues

### Headers that matter in production

- `Authorization`
- `Location`
- `Content-Type`
- `Accept`
- `Cache-Control`
- `ETag`
- `If-Match`
- `If-None-Match`
- `Last-Modified`
- `Idempotency-Key` (custom, common practice)
- `X-Request-ID` or `Traceparent`
- `Retry-After`
- `Link` (pagination/deprecation/discovery when useful)

### Caching fundamentals

If an endpoint is safe and its response is cacheable, you can reduce latency and server load significantly.

Use HTTP caching for:
- public or semi-public GET endpoints
- reference data
- infrequently changing lookups
- CDN-backed public resources

Do **not** blindly cache:
- personalized responses
- auth-sensitive data
- rapidly mutating data unless validators/TTL are well designed

### Conditional requests and optimistic concurrency

To avoid lost updates:

- include `ETag` on representations
- require `If-Match` for state-changing updates when concurrent modification matters
- return `412 Precondition Failed` on validator mismatch

This is cleaner than inventing ad hoc “version” query parameters.

---

## 4. Core design principles for a production API

### 4.1 Design for explicit contracts

Your API is a product. Clients need:

- predictable field names
- stable types
- stable enum values
- stable pagination semantics
- stable error format
- documented authentication rules
- versioning/deprecation strategy

### 4.2 Separate external contract from internal models

Never let ORM entities become your public API by accident.

Use separate models for:

- create input
- update input
- read output
- internal domain/service models
- database models

### 4.3 Make reads and writes explicit

Do not make one endpoint behave differently based on mysterious optional fields or flags.

Bad:
- `POST /user` sometimes creates, sometimes updates

Good:
- `POST /users`
- `PATCH /users/{id}`

### 4.4 Keep routes thin

Path operations should mostly do this:

1. parse and validate request
2. call service logic
3. map domain result to response
4. set status code/headers

Business rules belong in services, not in controllers.

### 4.5 Be consistent everywhere

Consistency beats cleverness.

Pick one approach for:

- timestamps
- pagination
- sorting syntax
- filter syntax
- naming conventions
- versioning
- error envelope
- authentication style
- partial update semantics

Then use it everywhere.

### 4.6 Prefer boring defaults

Boring APIs are easier to consume and operate.

Prefer:
- JSON
- UTC timestamps
- snake_case internally, stable external naming by deliberate choice
- path versioning if you need simplicity
- limit/offset or cursor pagination used consistently
- OpenAPI-first contract discipline

---

## 5. Recommended production architecture for FastAPI

A robust FastAPI codebase usually has these layers:

- **API layer**: routers, request parsing, response models, status codes
- **service layer**: business logic, orchestration, policies
- **repository/data access layer**: database queries and persistence
- **domain layer**: core rules, value objects, invariants
- **infrastructure layer**: database engines, caches, queues, email, external APIs, auth clients
- **cross-cutting concerns**: config, logging, tracing, security, middleware, exceptions

### Recommended responsibilities

#### Router / controller
- translate HTTP to application calls
- no deep business logic
- no SQL
- no hidden commits

#### Service
- enforce use cases and business rules
- own transaction boundaries or coordinate them consistently
- emit domain/application events
- decide what repositories/external services are called

#### Repository
- encapsulate persistence details
- no HTTP objects
- minimal business policy

#### Schema / DTO
- external contract only
- validation/serialization rules
- no DB session behavior

---

## 6. Project structure

One clean structure:

```text
app/
  api/
    deps.py
    errors.py
    routers/
      users.py
      orders.py
      auth.py
  core/
    config.py
    logging.py
    security.py
    lifespan.py
  db/
    base.py
    models.py
    session.py
    repositories/
      users.py
      orders.py
  domain/
    exceptions.py
    services/
      users.py
      orders.py
  schemas/
    common.py
    users.py
    orders.py
    auth.py
  integrations/
    email.py
    payments.py
    storage.py
  main.py

tests/
  unit/
  integration/
  contract/
  e2e/

alembic/
pyproject.toml
Dockerfile
.env.example
README.md
```

### Structure principles

- organize by feature or bounded context once the app grows
- keep shared infrastructure under `core/`, `db/`, `integrations/`
- separate `schemas/` from `db/models.py`
- make imports obvious and cyclic dependencies rare

---

## 7. Configuration and environment management

### Use typed settings

Use `pydantic-settings` for configuration. This gives you:

- typed settings
- environment variable loading
- dotenv support for local development
- validation at startup

Typical settings include:

- app name/environment
- debug flag
- database URL
- redis URL
- JWT signing config
- CORS origins
- log level
- feature flags
- third-party credentials
- storage bucket names
- timeouts

### Rules for configuration

- Never hardcode secrets.
- Never commit real `.env` files.
- Keep `.env.example` updated.
- Validate required settings at startup.
- Separate local/dev/staging/prod values externally, not in code branches.
- Prefer env vars and secret managers in production.

### Good pattern

Use a cached settings dependency so tests can override it.

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "my-api"
    environment: str = "local"
    database_url: str
    log_level: str = "INFO"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Production configuration rules

- Production must fail fast if critical config is missing.
- Use different secrets per environment.
- Rotate secrets.
- Keep config immutable during process lifetime unless you explicitly support reloads.

---

## 8. FastAPI application setup

### Use lifespan, not legacy startup/shutdown hooks

Use FastAPI’s lifespan API for startup and shutdown resource management:

- database engine creation
- redis client startup
- telemetry initialization
- model loading
- graceful cleanup

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize resources
    yield
    # cleanup resources

app = FastAPI(lifespan=lifespan)
```

### Main application responsibilities

Your `main.py` should do only composition:

- create the FastAPI app
- register middleware
- register exception handlers
- include routers
- attach lifespan
- possibly expose health routes

### Suggested `main.py`

```python
from fastapi import FastAPI
from app.api.routers import users, orders
from app.core.lifespan import lifespan

def create_app() -> FastAPI:
    app = FastAPI(
        title="My API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
    return app

app = create_app()
```

### Things to initialize in lifespan

Good candidates:
- DB engine/session factory
- cache clients
- tracing providers/exporters
- outbound HTTP clients
- model registries
- background schedulers you explicitly own

### Health endpoints

Use at least:

- `/health/live` or `/livez`: process is alive
- `/health/ready` or `/readyz`: app can serve traffic
- optionally `/health/startup`: app completed startup

Do not make liveness too expensive.
Readiness can validate essential dependencies.

---

## 9. Request/response modeling with Pydantic

Pydantic is central to FastAPI correctness.

### Core rule: use separate schemas for separate purposes

Typical schema set:

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserUpdate(BaseModel):
    full_name: str | None = None

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

class UserInDB(BaseModel):
    id: int
    email: str
    hashed_password: str
    full_name: str
    created_at: datetime
```

### Use `response_model` deliberately

Always declare response models for public endpoints unless you have a strong reason not to.

Why:
- output validation
- output filtering
- better docs
- contract safety
- accidental field leakage prevention

This is especially important for secrets or internal fields.

### Never return secrets by accident

Do not return:
- `hashed_password`
- internal IDs unless intended
- auth secrets
- feature flag internals
- moderation/risk internals
- audit-only metadata unless contract requires it

### Pydantic configuration that matters

For external request models, common safe defaults are:

- `extra="forbid"` for strict body contracts
- `strict=True` selectively for fields/models where coercion is risky
- aliases only when external naming differs intentionally

Example:

```python
from pydantic import BaseModel, ConfigDict

class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str
    password: str
```

### When strict mode helps

Use strict mode for:
- sensitive numeric fields
- IDs that must not be coerced
- money or quantity inputs when type coercion is risky
- external/public APIs where silent coercion causes bugs

Do **not** enable strictness blindly everywhere. Pydantic’s default coercion is often practical for query params, headers, dates, UUIDs, and environment values.

### Serialization discipline

Be deliberate with:
- `datetime` format
- enum representation
- aliasing
- optional/null handling
- decimal/money types
- camelCase vs snake_case externally

### Recommended modeling rule

Keep external JSON contracts boring and explicit.

Avoid:
- magical unions unless they are truly needed
- deeply polymorphic payloads when a discriminated union is not clearly documented
- “optional means many different behaviors” semantics

---

## 10. Validation strategy

Validation has levels. Use all of them.

### 10.1 Transport-level validation
Handled by FastAPI/Pydantic:
- path params
- query params
- headers
- body shape
- required vs optional fields
- types/formats

### 10.2 Domain validation
Handled in service/domain layer:
- business invariants
- allowed state transitions
- uniqueness rules not guaranteed by body schema alone
- authorization-aware constraints
- cross-field rules involving persistence

Example:
- “cannot cancel an already shipped order”
- “discount code cannot be applied to archived products”

### 10.3 Persistence-level validation
Handled by the database:
- unique constraints
- foreign keys
- check constraints
- not-null
- indexes

Never trust only application validation for invariants the database can enforce.

### Good validation pattern

- Pydantic validates structure
- services validate business rules
- DB enforces critical invariants
- exceptions are mapped to clean HTTP errors

---

## 11. Dependency injection

FastAPI’s dependency system is one of its strongest features.

Use dependencies for:
- DB session access
- settings
- current user
- authorization checks
- request-scoped services
- external clients
- shared validation logic

### Example: settings dependency

```python
from fastapi import Depends

def get_settings_dep():
    return get_settings()
```

### Example: database session dependency

```python
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Rules for dependencies

- Keep them small and composable.
- Avoid hidden side effects.
- Do not commit transactions deep inside generic dependencies unless that is a deliberate unit-of-work policy.
- Make dependencies overrideable in tests.

### Good dependency categories

- pure dependency: no side effects, just returns object/value
- policy dependency: e.g. current authenticated user
- resource dependency: DB session, external client
- guard dependency: authz or request constraints

---

## 12. Routing and API organization

### Use `APIRouter`

Organize by feature/domain:

- `users.router`
- `orders.router`
- `auth.router`

Keep each router focused.

### Recommended conventions

- version your external API, for example `/api/v1/...`
- use tags consistently for docs
- use prefixes per router
- centralize dependencies where shared
- give endpoints clear names and summaries

### Naming conventions

Collections:
- `GET /users`
- `POST /users`

Single resource:
- `GET /users/{user_id}`
- `PATCH /users/{user_id}`
- `DELETE /users/{user_id}`

Subresources:
- `GET /users/{user_id}/orders`

Actions:
- `POST /orders/{order_id}/cancel`

### Nested resources: use carefully

Good nesting:
- when containment is real
- when the child is not meaningful without the parent

Bad nesting:
- long chains like `/companies/{c}/departments/{d}/teams/{t}/members/{m}/permissions`
- better handled by top-level resources plus filters

---

## 13. Error handling

Error handling is part of the contract, not an afterthought.

### Goals of a good error model

Clients should be able to answer:
- what failed?
- why did it fail?
- is it the client’s fault or the server’s?
- can it be retried?
- what should the client change?
- what request/trace ID should support use?

### Use consistent error envelopes

A strong choice is RFC 9457 Problem Details for HTTP APIs.

Typical fields:
- `type`
- `title`
- `status`
- `detail`
- `instance`

You can add extensions:
- `request_id`
- `error_code`
- `field_errors`

### Differentiate error classes cleanly

- validation error
- authentication failure
- authorization failure
- not found
- conflict
- rate limit
- dependency failure
- unexpected server failure

### Never leak internals

Do not leak:
- stack traces
- SQL
- secrets
- raw upstream credentials
- internal topology
- implementation details that create security or support risk

### Centralize exception mapping

Create application/domain exceptions and map them to HTTP responses in one place.

Pattern:

```python
class DomainError(Exception):
    pass

class ResourceNotFound(DomainError):
    pass

class StateConflict(DomainError):
    pass
```

Then map centrally in FastAPI exception handlers.

### Validation errors

FastAPI already handles request validation well. Decide whether to:
- keep FastAPI’s default structure, or
- normalize it into your standard error envelope

Be consistent from day one.

### Use proper status codes for concurrency errors

When ETag or preconditions fail:
- return `412 Precondition Failed`

When a uniqueness or state conflict occurs:
- return `409 Conflict`

---

## 14. Authentication, authorization, and security

Security is not one feature. It is a system.

### 14.1 Authentication choices

Common options:
- bearer tokens (often OAuth2/OIDC)
- session cookies
- API keys
- mTLS for internal trusted systems

### 14.2 Common recommendation

For most modern APIs:
- use OAuth2/OIDC concepts where appropriate
- use short-lived bearer access tokens
- validate signature, issuer, audience, expiry, and not-before claims
- separate authentication from authorization

### 14.3 JWT basics you must understand

JWTs are **signed**, not necessarily encrypted.

That means:
- clients and attackers can read claims unless you use encryption separately
- never put secrets in JWT payloads
- verify signature and claims, not just decode

### 14.4 Password handling

Never store plaintext passwords.
Store strong password hashes only.

### 14.5 Authorization

Design authorization at multiple levels:

- route-level access
- resource ownership
- scope/role permission checks
- field-level restrictions if necessary
- tenant isolation
- object-level authorization

### 14.6 CORS

CORS matters for browser-based clients only.

Rules:
- configure explicit allowed origins
- understand that origin = protocol + domain + port
- avoid `*` with credentials
- keep methods and headers deliberate

CORS is **not** authentication.

### 14.7 CSRF

Relevant mainly when you use cookie-based auth in browsers.
If you use bearer tokens in `Authorization` headers, CSRF risk is different, but XSS remains critical.

### 14.8 Input and file security

- validate content type
- validate size
- sanitize file names
- malware-scan uploads if your domain needs it
- do not trust client-provided MIME alone
- do not serve uploaded files directly from app disks without thought

### 14.9 Secrets management

- no secrets in repo
- use secret stores or environment injection
- rotate keys
- audit access
- support key rollover for JWT signing or third-party credentials

### 14.10 Rate limiting and abuse protection

Implement at gateway, proxy, service, or middleware layer depending architecture.

Use for:
- login
- signup
- OTP verification
- password reset
- expensive search
- public APIs
- webhook endpoints exposed to the internet

### 14.11 Security headers and transport

- use HTTPS end to end or at least to trusted termination points
- redirect or terminate plaintext HTTP appropriately
- consider Trusted Host / HTTPS redirect middleware where useful
- trust forwarded headers only from known proxies

### 14.12 Security logging

Audit:
- auth attempts
- privilege changes
- key admin actions
- unusual rate-limit patterns
- token issuance/revocation events

Redact:
- passwords
- tokens
- secrets
- sensitive PII

---

## 15. Database access, transactions, and migrations

### Choose a production database deliberately

For most production APIs, PostgreSQL is the default strong choice.

### Use SQLAlchemy intentionally

You can use sync or async SQLAlchemy.
What matters most is consistency.

### Recommended async stack pattern

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
```

### Session lifecycle

A SQLAlchemy session:

- obtains a connection when needed
- starts a transaction
- flushes pending work before query/commit as needed
- returns the connection to the pool when the transaction ends

This is why **one session per request/use case** is a clean baseline.

### Core rules

- Do not use one global session shared across requests.
- Keep transaction boundaries explicit.
- Roll back on failure.
- Avoid long-lived transactions.
- Avoid mixing too many business concerns inside one transaction unless truly atomic.

### Repository pattern guidance

The repository layer should:
- hide SQLAlchemy query details
- return domain-meaningful objects
- avoid owning HTTP concerns

### Transaction boundary guidance

Pick one rule and enforce it:

Option A:
- service layer owns commit/rollback

Option B:
- unit-of-work dependency owns commit/rollback per request

I prefer **service-layer explicit transaction control** for non-trivial systems because it makes multi-step workflows easier to reason about.

### Async vs sync guidance

- If your endpoints are `async def`, prefer async database drivers/session usage.
- Do not call blocking database/network code directly inside `async def` handlers.
- CPU-bound work is not made faster by `async`.

### Connection pooling

Connection pooling is essential in server applications.

Tune when necessary:
- `pool_size`
- `max_overflow`
- `pool_recycle`
- `pool_timeout`

Do not guess. Tune based on:
- DB capacity
- pod/worker count
- concurrency profile
- p95/p99 latency
- connection utilization

### Migrations with Alembic

Use Alembic for schema migrations.

Important rule:
- autogenerate is a **starting point**, not a final guarantee

Always review generated migrations manually.

Check for:
- data migration needs
- index naming
- constraint naming
- safe nullability changes
- column type changes
- backward compatibility during rolling deploys

### Expand/contract migrations

For zero-downtime releases, prefer:

1. expand schema safely
2. deploy app that writes to both/new fields if needed
3. backfill data
4. switch reads
5. contract/remove old fields later

### Never rely on ORM schema creation in production

Do not use auto-create tables on app startup as your production migration strategy.
Use explicit migrations.

---

## 16. Pagination, filtering, sorting, and search

List endpoints become production pain points unless standardized.

### Pagination options

#### Offset/limit
Simple and fine for many systems.

Example:
- `GET /users?limit=50&offset=100`

Pros:
- easy to understand
- easy to implement

Cons:
- unstable under frequent inserts/deletes
- expensive at large offsets

#### Cursor/keyset pagination
Better for large, hot datasets.

Example:
- `GET /events?limit=100&cursor=eyJpZCI6MTIzfQ==`

Pros:
- stable
- performant for deep pagination

Cons:
- more implementation complexity

### Recommendation

- small/internal APIs: offset/limit is usually enough
- large/public/high-volume feeds: prefer cursor/keyset

### Filtering

Use query parameters consistently.

Examples:
- `GET /orders?status=paid`
- `GET /users?email=foo@example.com`
- `GET /products?category=books&in_stock=true`

Rules:
- define exact operators
- keep naming consistent
- document supported fields/operators
- reject unsupported filters explicitly

### Sorting

Use one syntax consistently, for example:

- `sort=created_at`
- `sort=-created_at`
- `sort=last_name,-created_at`

Document:
- allowed fields
- default ordering
- null ordering if it matters

### Search

If you provide text search:

- clarify whether it is exact, prefix, or full text
- return paginated results
- document ranking stability expectations
- set timeouts/limits

Do not expose raw database query semantics as your public contract.

---

## 17. Caching, idempotency, and concurrency control

### 17.1 HTTP caching

Use cache headers for safe GET endpoints when possible.

Tools:
- `Cache-Control`
- `ETag`
- `Last-Modified`

### 17.2 Server-side caching

Cache expensive derived reads:
- reports
- expensive lookups
- repeated aggregations
- permission snapshots if safe

Watch out for:
- stale data
- cache invalidation
- per-tenant isolation
- auth-sensitive data leakage

### 17.3 Idempotency keys

For non-idempotent POST requests that may be retried by clients or intermediaries, use idempotency keys.

Typical cases:
- payment creation
- order placement
- signup finalization
- external side-effectful operations

Rules:
- client sends `Idempotency-Key`
- server stores request fingerprint/result
- repeated same key returns same logical result
- conflicting payload with same key should fail explicitly

### 17.4 Optimistic concurrency

When resource races matter:
- return `ETag` on reads
- require `If-Match` on updates/deletes
- reject mismatches with `412`

### 17.5 Retry semantics

Be careful with retries:

- GET/PUT/DELETE are usually safer to retry
- POST is dangerous without idempotency strategy
- distinguish transient dependency failures from permanent errors

---

## 18. Files, streaming, and background work

### File uploads

FastAPI supports file uploads via `UploadFile` and `File(...)`.

Prefer `UploadFile` for larger files because it uses a spooled file approach and avoids loading everything into memory at once.

### Upload rules

- set max upload size at proxy/app level
- validate content type and extension
- stream or spool, do not read giant files eagerly into memory
- store metadata separately from blob contents
- prefer object storage for durable production file handling

### Streaming responses

Use streaming for:
- large downloads
- generated exports
- progressive delivery

Ensure:
- timeouts are sane
- clients know content type and content disposition
- you do not hold unnecessary resources too long

### BackgroundTasks

FastAPI’s `BackgroundTasks` is appropriate for:
- small post-response work
- same-process tasks
- lightweight follow-up actions

Examples:
- write small audit/log records
- send a simple email
- trigger a lightweight callback
- enqueue a durable job to a real queue

Do **not** use same-process background tasks as your durable distributed job system.

For heavy or durable work, use a real worker/queue system.

### Long-running jobs pattern

Good production pattern:

1. `POST /jobs`
2. return `202 Accepted` with job ID
3. process asynchronously in workers
4. expose `GET /jobs/{id}`
5. optionally provide webhook/callback on completion

---

## 19. Documentation and API contracts

### OpenAPI is a production asset

Your OpenAPI schema should be treated as part of the product.

Use it for:
- docs
- client SDK generation
- contract tests
- review and governance
- change detection in CI

### What to document well

- auth scheme
- examples
- response models
- error models
- pagination
- enums
- deprecations
- rate limits
- idempotency behavior
- async job semantics

### FastAPI strengths here

FastAPI gives you:
- automatic OpenAPI generation
- `/docs` and `/redoc`
- schema generation from type hints and Pydantic models
- route metadata such as tags, summaries, descriptions, examples

### Documentation discipline

- add summaries and descriptions to routes
- define request/response examples for important endpoints
- document non-obvious business constraints
- document error responses explicitly
- pin operation IDs if SDK generation matters

### Input/output schema separation

Use separate DTOs for input and output when they differ.
This is especially important for:
- password fields
- write-only fields
- server-generated fields
- internal-only fields

### Production docs exposure

For public APIs:
- docs may stay public by design

For private/internal APIs:
- restrict docs or OpenAPI exposure if appropriate

Do not expose docs thoughtlessly in sensitive environments.

---

## 20. Testing strategy

Testing a production API is not one thing. It is a pyramid.

### 20.1 Unit tests
Test:
- service logic
- validators
- policy checks
- utility code
- edge cases

Fast, isolated, no real DB/network.

### 20.2 Integration tests
Test:
- database integration
- repository behavior
- migrations
- transaction semantics
- serialization and endpoint behavior together

### 20.3 Contract tests
Test:
- OpenAPI compatibility
- request/response shape
- status code expectations
- consumer-driven contracts when relevant

### 20.4 End-to-end tests
Test:
- full deployed behavior
- auth flow
- external dependencies or stubs
- critical business journeys

### 20.5 Non-functional tests
Test:
- load
- stress
- soak
- performance regressions
- security checks
- resilience/failure modes

### FastAPI testing basics

Use:
- `TestClient` for standard tests
- async tests with AnyIO and HTTPX `AsyncClient` when the test itself is async or interacts with async DB code
- `app.dependency_overrides` to inject fake dependencies
- `pytest` fixtures for setup/teardown
- `monkeypatch` for env vars and external function patching

### Recommended test categories

```text
tests/
  unit/
  integration/
  contract/
  e2e/
```

### What every production API should test

- auth success/failure
- validation success/failure
- not-found behavior
- conflict behavior
- pagination semantics
- permission boundaries
- DB constraint mapping
- idempotent retry behavior
- optimistic concurrency behavior
- serialization of timestamps/enums/nulls
- migration up/down strategy where relevant

### Test data strategy

- factories > hardcoded giant payloads
- isolated DB per test run
- rollback or recreate DB state deterministically
- keep fixtures explicit and small

### Performance testing targets

Track at minimum:
- throughput
- p50/p95/p99 latency
- error rate under load
- DB connection usage
- memory growth
- queue depth if using workers

---

## 21. Observability

If you cannot observe it, you cannot run it in production.

### 21.1 Logging

Use structured logs.
Include:
- timestamp
- level
- message
- request ID / trace ID
- route
- method
- status code
- latency
- user/tenant identifiers when safe
- deployment version

Redact:
- tokens
- passwords
- secrets
- sensitive PII

### 21.2 Metrics

At minimum, track RED metrics:
- **Rate**: requests per second
- **Errors**: by route/status/error type
- **Duration**: latency distributions

Useful additional metrics:
- DB pool usage
- cache hit rate
- queue depth
- external API latency/error rate
- background job timings

### 21.3 Tracing

Use distributed tracing to follow requests across:
- API service
- database
- cache
- outbound HTTP calls
- message queues
- worker services

OpenTelemetry is the standard baseline approach in Python ecosystems.

### 21.4 Correlation IDs

Every request should have a stable correlation ID or trace context.

Pattern:
- accept incoming request ID if trusted, otherwise generate one
- include it in logs
- return it in response headers
- propagate it to downstream systems

### 21.5 Health and diagnostics

Expose:
- liveness
- readiness
- version/build info endpoint if useful
- dependency diagnostics internally, not publicly

### 21.6 Audit logging

For sensitive domains:
- who did what
- to which resource
- from where
- before/after state where policy requires it

Audit logs are not the same as debug logs.

---

## 22. Performance and scalability

### 22.1 Know what `async` helps with

`async` helps with **I/O-bound concurrency**, not CPU-bound work.

Good fits:
- DB calls with async drivers
- outbound HTTP requests
- Redis
- file/network I/O

Bad fit:
- CPU-heavy image transforms
- data science computation
- compression/encryption-heavy CPU work
- giant in-process loops

For CPU-bound work:
- process pools
- worker systems
- external job runners

### 22.2 Avoid blocking the event loop

Inside `async def`:
- do not call blocking libraries directly
- do not run long CPU work directly
- do not use sync DB/network libraries casually

### 22.3 Reduce payload size

- paginate
- select only needed fields
- compress where beneficial
- avoid giant nested response shapes
- use summaries vs detailed views when sensible

### 22.4 Control database load

- index real query patterns
- avoid N+1 queries
- select only needed columns
- batch related loads carefully
- measure query count and latency
- tune pool and worker counts together

### 22.5 Horizontal scaling

Make the app stateless where possible:

- no local session state
- no critical local file dependence
- shared cache/queue/storage
- externalized uploads
- idempotent handlers

### 22.6 Concurrency limits and backpressure

Protect the service:
- server concurrency limits
- queue bounds
- DB pool limits
- timeouts
- circuit breaking / fail-fast patterns where needed

### 22.7 Measure before “optimizing”

Do not optimize based on vibes.
Use profiling, tracing, and load tests.

---

## 23. Deployment and runtime operations

### Development vs production startup

Development:
- autoreload
- verbose debug logs

Production:
- no reload
- explicit worker/process strategy
- proper timeouts
- structured logs
- health probes
- graceful shutdown

### Containerization

Containers are a strong default for FastAPI production deployments.

Guidelines:
- build from an official Python base image
- use multi-stage builds if helpful
- pin dependencies
- run as non-root where practical
- keep image small
- inject config via env/secrets
- make the filesystem assumptions explicit

### Worker/process strategy

General guidance:
- on plain VMs or self-managed hosts, multiple worker processes can help use multiple cores
- in Kubernetes/container platforms, it is often cleaner to run **one app process per container** and scale horizontally

### Reverse proxy / ingress

Use a trusted proxy/load balancer/ingress for:
- TLS termination
- routing
- buffering
- size limits
- rate limiting
- WAF integration
- request logging
- static/object traffic offload

Trust forwarded headers **only** from trusted proxies.

### Startup sequencing

A production deploy often needs:

1. secrets/config present
2. migrations run safely
3. app starts
4. readiness passes
5. traffic begins

Do not let app startup silently succeed with broken dependencies unless that is a deliberate degraded mode.

### Graceful shutdown

Ensure the app:
- stops taking new traffic
- finishes in-flight work within timeout
- closes DB/cache clients
- flushes telemetry if possible

### Timeouts you need

- inbound request timeout
- keep-alive timeout
- DB connect/query timeout
- external HTTP connect/read timeout
- graceful shutdown timeout
- worker health timeout

### Static and media files

Do not make the API process your primary static/media server in serious production deployments.
Use CDN/object storage/reverse proxy patterns.

### Docs/OpenAPI exposure in prod

Decide consciously whether `/docs`, `/redoc`, `/openapi.json` should be:
- public
- authenticated
- internal-only
- disabled in selected environments

---

## 24. CI/CD and release management

### CI must check

- linting
- formatting
- type checks
- tests
- security scanning
- migration integrity
- OpenAPI generation/validation
- image build
- dependency review

### CD should support

- reproducible builds
- environment promotion
- migration gates
- rollback plan
- version tagging
- release notes/change log

### Backward compatibility discipline

Before breaking changes, ask:
- will existing clients fail?
- do enums change?
- do required fields change?
- do status codes change?
- do error bodies change?
- does pagination syntax change?
- does auth behavior change?

### Deprecation strategy

For public/shared APIs:
- announce deprecations clearly
- document timeline
- keep old versions long enough
- use headers/docs/changelog consistently
- monitor real client usage before removal

### Database rollout discipline

Application and schema should be deployed in compatible order.
Prefer expand/contract patterns.

---

## 25. Production operations checklist

Use this as a revision checklist.

### API design
- [ ] resources are noun-based
- [ ] methods follow HTTP semantics
- [ ] status codes are consistent
- [ ] error format is standardized
- [ ] pagination/filter/sort conventions are documented
- [ ] versioning strategy is explicit

### FastAPI/Pydantic
- [ ] lifespan is used for startup/shutdown resources
- [ ] `response_model` is declared for public endpoints
- [ ] request DTOs and response DTOs are separate
- [ ] sensitive fields cannot leak accidentally
- [ ] external request models use strict enough validation
- [ ] dependencies are overrideable for testing

### Security
- [ ] HTTPS is enforced through trusted infrastructure
- [ ] auth scheme is clearly defined
- [ ] tokens/passwords are handled safely
- [ ] CORS is explicit, not permissive by accident
- [ ] secrets are externalized
- [ ] rate limiting/abuse controls exist
- [ ] logs redact sensitive data

### Data layer
- [ ] one session per request/use case
- [ ] transaction boundaries are explicit
- [ ] pool settings are tuned consciously
- [ ] migrations are managed with Alembic
- [ ] autogenerated migrations are reviewed manually
- [ ] DB constraints back critical invariants

### Testing
- [ ] unit tests cover service logic
- [ ] integration tests cover DB/repositories
- [ ] dependency overrides are used where needed
- [ ] async tests are correct
- [ ] error cases are tested
- [ ] performance tests exist for critical flows

### Observability
- [ ] structured logs exist
- [ ] request/trace IDs are propagated
- [ ] latency/error/rate metrics exist
- [ ] tracing exists for critical dependencies
- [ ] health probes exist
- [ ] audit logs exist where required

### Deployment
- [ ] no `--reload` in production
- [ ] worker/process strategy matches platform
- [ ] readiness/liveness are configured
- [ ] graceful shutdown works
- [ ] trusted proxy headers are configured correctly
- [ ] migration rollout order is safe

### Operations
- [ ] runbooks exist
- [ ] rollback is tested
- [ ] backups and restore drills exist if stateful systems matter
- [ ] deprecation policy exists
- [ ] incident ownership is clear
- [ ] SLOs/alerts are defined

---

## 26. Common mistakes and anti-patterns

### API design mistakes
- using verbs everywhere
- misusing POST for all operations
- returning `200` for every situation
- changing response shape casually
- undocumented breaking changes
- no pagination on list endpoints
- inconsistent error responses

### FastAPI/Python mistakes
- giant route handlers with business logic
- returning raw ORM objects everywhere without response models
- blocking calls inside `async def`
- global mutable singletons used unsafely
- hidden commits in repositories
- mixing sync/async carelessly
- startup logic scattered across modules

### Security mistakes
- storing plaintext passwords
- putting secrets in JWT payloads
- trusting all forwarded headers
- permissive CORS by default
- leaking stack traces or raw DB errors
- logging access tokens

### Database mistakes
- one global session reused across requests
- long transactions spanning external calls
- missing indexes on hot queries
- relying on app checks instead of DB constraints
- unreviewed autogenerated migrations
- destructive schema changes in one risky deploy

### Operational mistakes
- no request IDs
- no readiness probe
- no timeout budgets
- no rate limiting
- no load test before launch
- no rollback plan
- no alerting on latency/error spikes

---

## 27. A practical build order

If you are building a real production API from scratch, build in this order:

1. define resources, contracts, and auth model  
2. create Pydantic schemas and OpenAPI shape  
3. set up app factory, lifespan, settings, routers  
4. add DB engine/session/repositories  
5. implement service layer and domain rules  
6. wire exception mapping and error contract  
7. add authentication and authorization  
8. add pagination/filter/sort conventions  
9. add tests for main flows and failures  
10. add logging, metrics, tracing, request IDs  
11. add migrations and rollout discipline  
12. containerize and configure readiness/liveness  
13. load test and tune pool/workers/timeouts  
14. add runbooks, alerts, deprecation policy

---

## 28. Minimal production blueprint

This is a compact blueprint you can memorize.

### 28.1 App factory
```python
def create_app() -> FastAPI:
    app = FastAPI(
        title="Orders API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(...)
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
    register_exception_handlers(app)
    return app
```

### 28.2 Router
```python
@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    order = await service.create_order(current_user.id, payload)
    return order
```

### 28.3 Service
```python
class OrderService:
    def __init__(self, repo: OrderRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_order(self, user_id: int, payload: OrderCreate) -> Order:
        # business validation
        order = await self.repo.create(user_id=user_id, payload=payload)
        await self.session.commit()
        await self.session.refresh(order)
        return order
```

### 28.4 Repository
```python
class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, payload: OrderCreate) -> Order:
        order = Order(user_id=user_id, **payload.model_dump())
        self.session.add(order)
        return order
```

### 28.5 Error mapping
```python
@app.exception_handler(ResourceNotFound)
async def not_found_handler(request: Request, exc: ResourceNotFound):
    return JSONResponse(
        status_code=404,
        content={
            "type": "https://api.example.com/problems/not-found",
            "title": "Resource not found",
            "status": 404,
            "detail": str(exc),
            "instance": str(request.url.path),
        },
    )
```

### 28.6 Settings
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    jwt_secret_key: str
    environment: str = "local"
```

### 28.7 DB session dependency
```python
async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
```

### 28.8 Health routes
```python
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    # optional lightweight dependency checks
    return {"status": "ready"}
```

### 28.9 Test override
```python
app.dependency_overrides[get_settings] = get_test_settings
```

### 28.10 Production mindset
- clear contract
- clean layering
- explicit transactions
- safe auth
- strong testing
- observable runtime
- predictable deployment

That is the core of a production-grade FastAPI REST API.

---

## 29. Authoritative references

These are the primary references behind the guidance in this document and are worth revising directly.

### HTTP / REST semantics
- RFC 9110 — HTTP Semantics: https://www.rfc-editor.org/rfc/rfc9110.html
- RFC 9457 — Problem Details for HTTP APIs: https://www.rfc-editor.org/rfc/rfc9457.html

### FastAPI
- FastAPI docs: https://fastapi.tiangolo.com/
- Lifespan / startup-shutdown: https://fastapi.tiangolo.com/advanced/events/
- Bigger applications / routers: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Settings: https://fastapi.tiangolo.com/advanced/settings/
- Response models: https://fastapi.tiangolo.com/tutorial/response-model/
- Extra models / separate input-output models: https://fastapi.tiangolo.com/tutorial/extra-models/
- Error handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
- Security: https://fastapi.tiangolo.com/tutorial/security/
- OAuth2 + JWT example: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- CORS: https://fastapi.tiangolo.com/tutorial/cors/
- Background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Middleware: https://fastapi.tiangolo.com/advanced/middleware/
- Request files / UploadFile: https://fastapi.tiangolo.com/tutorial/request-files/
- Testing: https://fastapi.tiangolo.com/tutorial/testing/
- Async tests: https://fastapi.tiangolo.com/advanced/async-tests/
- Testing dependency overrides: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- Deployment: https://fastapi.tiangolo.com/deployment/
- Uvicorn workers via FastAPI docs: https://fastapi.tiangolo.com/deployment/server-workers/
- Containers / Docker: https://fastapi.tiangolo.com/deployment/docker/
- OpenAPI docs and extensions: https://fastapi.tiangolo.com/reference/openapi/docs/ and https://fastapi.tiangolo.com/how-to/extending-openapi/

### Pydantic
- Pydantic docs: https://docs.pydantic.dev/latest/
- Strict mode: https://docs.pydantic.dev/latest/concepts/strict_mode/
- Settings management: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Serialization: https://docs.pydantic.dev/latest/concepts/serialization/
- Model config: https://docs.pydantic.dev/latest/api/config/

### SQLAlchemy / Alembic
- SQLAlchemy session basics: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- SQLAlchemy asyncio: https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html
- SQLAlchemy connection pooling: https://docs.sqlalchemy.org/en/21/core/pooling.html
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Alembic autogenerate: https://alembic.sqlalchemy.org/en/latest/autogenerate.html

### Testing / async support
- pytest docs: https://docs.pytest.org/en/stable/
- pytest monkeypatch: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- AnyIO testing: https://anyio.readthedocs.io/en/stable/testing.html
- HTTPX async support: https://www.python-httpx.org/async/

### Observability
- OpenTelemetry Python: https://opentelemetry.io/docs/languages/python/
- OpenTelemetry FastAPI instrumentation: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html

### Alternatives to REST
- GraphQL: https://graphql.org/
- gRPC: https://grpc.io/
- WebSocket API overview: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

---

## Final revision summary

If you only memorize one page, memorize this:

1. REST is best for stable resource-oriented HTTP APIs.  
2. Do not use REST for everything; use GraphQL, gRPC, WebSockets, or queues when the interaction model demands it.  
3. Honor HTTP semantics: methods, status codes, caching, idempotency, validators.  
4. Keep FastAPI routes thin and move business logic to services.  
5. Use separate Pydantic models for create, update, read, and internal data.  
6. Use `response_model`, typed settings, lifespan, dependency injection, and explicit error mapping.  
7. Make DB sessions request-scoped, transactions explicit, and migrations reviewed manually.  
8. Secure the API end to end: auth, authz, CORS discipline, secret handling, rate limits, HTTPS, redaction.  
9. Test at multiple layers and make the API observable with logs, metrics, traces, and health probes.  
10. Treat deployment and operations as part of the API design, not a separate afterthought.
