# SQLAlchemy (Python) — Comprehensive Concepts Guide

> **Scope:** This guide is a **comprehensive concepts handbook** for **SQLAlchemy 2.x style** usage, with emphasis on the current stable documentation line (**2.0**). It is organized to help you revise the subject end-to-end without mixing in older 1.x habits unless migration context matters.
>
> **What this is:** a complete map of the *important concepts* you should know.
>
> **What this is not:** a line-by-line API reference for every symbol in every dialect.

---

## Table of contents

1. [What SQLAlchemy is](#1-what-sqlalchemy-is)
2. [The big mental model](#2-the-big-mental-model)
3. [Installation and package layout](#3-installation-and-package-layout)
4. [Core vs ORM](#4-core-vs-orm)
5. [Engine, DBAPI, and database URLs](#5-engine-dbapi-and-database-urls)
6. [Connections, transactions, and results](#6-connections-transactions-and-results)
7. [Connection pooling](#7-connection-pooling)
8. [Schema and metadata](#8-schema-and-metadata)
9. [Tables, columns, constraints, and indexes](#9-tables-columns-constraints-and-indexes)
10. [SQL Expression Language (Core SQL)](#10-sql-expression-language-core-sql)
11. [Core DML: INSERT, UPDATE, DELETE](#11-core-dml-insert-update-delete)
12. [Textual SQL and SQL compilation](#12-textual-sql-and-sql-compilation)
13. [Types and custom types](#13-types-and-custom-types)
14. [Defaults and server-generated values](#14-defaults-and-server-generated-values)
15. [Reflection and database inspection](#15-reflection-and-database-inspection)
16. [Declarative ORM mapping](#16-declarative-orm-mapping)
17. [Mapped attributes and typed mappings](#17-mapped-attributes-and-typed-mappings)
18. [Relationships](#18-relationships)
19. [Configuring relationship joins](#19-configuring-relationship-joins)
20. [Session, identity map, and unit of work](#20-session-identity-map-and-unit-of-work)
21. [Object state management](#21-object-state-management)
22. [Querying with the ORM (2.x style)](#22-querying-with-the-orm-2x-style)
23. [Loader strategies and relationship loading](#23-loader-strategies-and-relationship-loading)
24. [Cascades and delete behavior](#24-cascades-and-delete-behavior)
25. [Inheritance mappings](#25-inheritance-mappings)
26. [Advanced mapped attributes](#26-advanced-mapped-attributes)
27. [Additional persistence techniques](#27-additional-persistence-techniques)
28. [Async SQLAlchemy](#28-async-sqlalchemy)
29. [Events system](#29-events-system)
30. [ORM extensions you should know](#30-orm-extensions-you-should-know)
31. [Dataclasses, attrs, and typing](#31-dataclasses-attrs-and-typing)
32. [Dialect-specific behavior](#32-dialect-specific-behavior)
33. [Errors, debugging, and troubleshooting](#33-errors-debugging-and-troubleshooting)
34. [Performance and best practices](#34-performance-and-best-practices)
35. [Testing patterns](#35-testing-patterns)
36. [Migration concepts: 1.4/legacy to 2.x](#36-migration-concepts-14legacy-to-2x)
37. [How Alembic fits in](#37-how-alembic-fits-in)
38. [Revision checklist](#38-revision-checklist)
39. [Official references](#39-official-references)

---

## 1) What SQLAlchemy is

SQLAlchemy is a Python database toolkit and ORM.

It has two major layers:

- **Core**: database connectivity, SQL construction, execution, transactions, schema definitions, reflection, types, results.
- **ORM**: object-relational mapping on top of Core. You map Python classes to tables and persist/query objects through a `Session`.

The ORM is built on top of Core, not separate from it.

---

## 2) The big mental model

If you understand the following pipeline, you understand most of SQLAlchemy:

**Python code** → **SQLAlchemy objects** → **compiled SQL + bound parameters** → **DBAPI driver** → **database**

And for ORM work:

**Mapped classes** + **Session** + **Unit of Work** + **Identity Map** → synchronized object/database state

Key ideas:

- SQLAlchemy usually wants you to build SQL **as Python expressions**, not string concatenation.
- **Engine** is the entry point to the database.
- **Connection** executes SQL in Core.
- **Session** is the ORM transaction/persistence boundary.
- **MetaData / Table / Column** represent schema.
- **select()** is the central query construct in 2.x for both Core and ORM.
- **Result** objects wrap returned rows/scalars/mappings.
- The **dialect** adapts SQLAlchemy behavior to a specific backend such as PostgreSQL, SQLite, MySQL, Oracle, or SQL Server.

---

## 3) Installation and package layout

Typical install:

```bash
pip install sqlalchemy
```

You also install a **DBAPI driver** depending on the backend, for example:

- PostgreSQL: `psycopg`, `asyncpg`
- MySQL/MariaDB: `pymysql`, `mysqlclient`, `aiomysql`, `asyncmy`
- SQLite: built-in `sqlite3`, or `aiosqlite` for async
- Oracle: `oracledb`
- SQL Server: `pyodbc`

Common namespaces:

```python
from sqlalchemy import create_engine, select, insert, update, delete, text
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Session, sessionmaker
```

Rule of thumb:

- `sqlalchemy` namespace = mostly Core
- `sqlalchemy.orm` namespace = ORM-related constructs

---

## 4) Core vs ORM

### Core
Use Core when you want:

- direct SQL expression building
- explicit control over statements and execution
- lightweight use without mapped classes
- schema management primitives

### ORM
Use ORM when you want:

- Python classes mapped to tables
- working with objects rather than rows
- relationship management
- unit-of-work persistence
- identity map semantics

### Important 2.x concept
In SQLAlchemy 2.x, **ORM querying is unified with Core-style `select()`**. The old `session.query(...)` style is considered **legacy API**, not the primary style.

---

## 5) Engine, DBAPI, and database URLs

`Engine` is the top-level Core object used to interface with a database.

```python
engine = create_engine("postgresql+psycopg://user:pass@host/dbname")
```

### The Engine is responsible for:

- database connectivity
- holding the dialect
- managing connection pool behavior
- producing `Connection` objects
- execution options and logging integration

### Database URL format

```text
dialect+driver://username:password@host:port/database
```

Examples:

```python
create_engine("sqlite+pysqlite:///app.db")
create_engine("postgresql+psycopg://scott:tiger@localhost/test")
create_engine("mysql+pymysql://scott:tiger@localhost/test")
```

### Common engine options

- `echo=True` — log SQL emitted
- `pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`, `pool_pre_ping`
- `future=True` — old transitional 1.4 flag; not needed in 2.x style code
- `connect_args={...}` — pass DBAPI-specific connect options
- `isolation_level=...`

### Engine best practices

- Usually create **one engine per database URL per process**
- Reuse the engine across your application
- Do not create a new engine for each query
- In multiprocess/forking scenarios, initialize engines per process

---

## 6) Connections, transactions, and results

### Connection
A `Connection` is obtained from the `Engine`:

```python
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("select 1"))
```

### Transaction styles in Core

#### A. Begin once
```python
with engine.begin() as conn:
    conn.execute(...)
    conn.execute(...)
```

This opens a transaction and commits on success, rolls back on exception.

#### B. Commit as you go
```python
with engine.connect() as conn:
    conn.execute(...)
    conn.commit()
    conn.execute(...)
    conn.rollback()
```

SQLAlchemy 2.x explicitly supports this style.

### Important transaction concepts

- Many DBAPIs begin transactions implicitly when first used.
- SQLAlchemy wraps this into explicit transaction control.
- `commit()` persists the transaction.
- `rollback()` reverts the current transaction.
- Savepoints and nested transactions are available via `begin_nested()`.

### Result objects

Execution returns a `Result` object:

```python
result = conn.execute(select(user_table))
```

Useful access patterns:

- `result.all()` → list of rows
- `result.first()` → first row or `None`
- `result.one()` → exactly one row, else exception
- `result.one_or_none()`
- `result.scalar()` → first column of first row
- `result.scalars()` → scalar stream for one-column/entity results
- `result.mappings()` → dictionary-like row mappings

### Row behavior

Rows can be accessed:

- by position: `row[0]`
- by column name / key: `row.username`
- as mapping via `result.mappings()`

### Execution options
Statements, connections, and engines can carry execution options such as stream behavior, isolation, yield strategies, or dialect-specific flags.

---

## 7) Connection pooling

SQLAlchemy uses connection pools for efficiency.

### Why pooling exists
Creating DB connections is expensive. Pools let your application reuse existing DBAPI connections.

### Main pool concepts

- **checked-in** connection: back in the pool
- **checked-out** connection: currently in use
- **overflow** connections: temporary connections beyond `pool_size`
- **pre-ping**: tests a connection before use to avoid stale connection errors

### Pool settings you should know

- `pool_size`
- `max_overflow`
- `pool_timeout`
- `pool_recycle`
- `pool_pre_ping=True`

### Common pool implementations

- `QueuePool` — common default for many backends
- `NullPool` — no pooling
- `StaticPool` — often used for special SQLite/testing cases
- `SingletonThreadPool` — certain SQLite/thread-local patterns

### Pool-related failures
A classic problem is pool exhaustion, often caused by:

- sessions/connections not being closed
- long-running transactions
- too many concurrent requests for current pool config

---

## 8) Schema and metadata

`MetaData` is the collection object that stores table definitions and related schema constructs.

```python
metadata = MetaData()
```

### What MetaData does

- collects `Table` objects
- tracks schema namespace
- can emit DDL via `create_all()` and `drop_all()`
- supports reflection from an existing database
- provides dependency-aware ordering with `sorted_tables`

### Core schema objects

- `MetaData`
- `Table`
- `Column`
- `ForeignKey`
- `PrimaryKeyConstraint`
- `UniqueConstraint`
- `CheckConstraint`
- `Index`
- schema-qualified names

Example:

```python
metadata = MetaData()

user_table = Table(
    "user_account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(30), nullable=False),
    Column("fullname", String),
)
```

### Creating tables

```python
metadata.create_all(engine)
```

### Dropping tables

```python
metadata.drop_all(engine)
```

### Important limitation
`create_all()` is **not** a migration system. It creates missing tables/objects; it is not a full schema evolution tool.

---

## 9) Tables, columns, constraints, and indexes

### Table
Represents a database table.

### Column
Represents a table column with type and options.

Common options:

- `primary_key=True`
- `nullable=False`
- `unique=True`
- `index=True`
- `default=...`
- `server_default=...`
- `ForeignKey("other_table.id")`

### Constraints

- **Primary key**
- **Foreign key**
- **Unique**
- **Check**
- composite constraints via explicit `Constraint` objects

Example:

```python
Table(
    "address",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email", String, nullable=False),
    UniqueConstraint("email"),
)
```

### Indexes

```python
Index("ix_address_email", address_table.c.email)
```

Indexes may be:

- single-column
- composite
- unique
- functional/expression indexes on supported dialects

### Naming conventions
A very important real-world concept: use `MetaData(naming_convention=...)` to create stable names for constraints and indexes, especially when using Alembic autogenerate.

---

## 10) SQL Expression Language (Core SQL)

This is the heart of SQLAlchemy Core.

### Central constructs

- `select()`
- `insert()`
- `update()`
- `delete()`
- `text()`
- `func`
- `case`
- `and_()`, `or_()`, `not_()`
- `bindparam()`
- `literal()`
- subqueries, aliases, CTEs, unions

### SELECT basics

```python
stmt = select(user_table)
stmt = select(user_table.c.name, user_table.c.fullname)
stmt = select(user_table).where(user_table.c.name == "spongebob")
```

### WHERE clauses
Expressions are built using Python operators:

```python
stmt = select(user_table).where(
    (user_table.c.name == "a") | (user_table.c.name == "b")
)
```

Use parentheses because Python operator precedence matters.

### ORDER BY / GROUP BY / HAVING / LIMIT
```python
stmt = (
    select(user_table.c.name)
    .order_by(user_table.c.name)
    .limit(10)
    .offset(20)
)
```

### Joins
```python
stmt = select(user_table, address_table).join(
    address_table, user_table.c.id == address_table.c.user_id
)
```

### Aliases and subqueries
```python
subq = select(address_table.c.user_id).subquery()
u = user_table.alias()
stmt = select(u)
```

### CTEs
```python
cte = select(user_table).cte("users_cte")
stmt = select(cte)
```

### Set operations
- `union()`
- `union_all()`
- `intersect()`
- `except_()`

### SQL functions
Use `func`:

```python
stmt = select(func.count(user_table.c.id))
```

### CASE expressions
```python
stmt = select(
    case(
        (user_table.c.name == "admin", "A"),
        else_="U",
    )
)
```

### EXISTS
```python
stmt = select(user_table).where(
    select(address_table.c.id)
    .where(address_table.c.user_id == user_table.c.id)
    .exists()
)
```

### Window functions
Supported through SQL expression constructs when the backend supports them.

### SQLAlchemy expression principle
You generally build **expression trees**, not strings.

---

## 11) Core DML: INSERT, UPDATE, DELETE

### INSERT
```python
stmt = insert(user_table).values(name="alice", fullname="Alice A")
conn.execute(stmt)
```

### Multi-row INSERT
```python
conn.execute(
    insert(user_table),
    [
        {"name": "a", "fullname": "A"},
        {"name": "b", "fullname": "B"},
    ],
)
```

### UPDATE
```python
stmt = (
    update(user_table)
    .where(user_table.c.name == "alice")
    .values(fullname="Alice Updated")
)
conn.execute(stmt)
```

### DELETE
```python
stmt = delete(user_table).where(user_table.c.name == "alice")
conn.execute(stmt)
```

### RETURNING
On supported backends:

```python
stmt = insert(user_table).values(name="x").returning(user_table.c.id)
```

This is important for server-generated values and efficient fetch-after-write behavior.

---

## 12) Textual SQL and SQL compilation

### `text()`
Use `text()` for raw SQL while still letting SQLAlchemy manage execution and parameters:

```python
stmt = text("select * from user_account where id=:id")
conn.execute(stmt, {"id": 1})
```

Prefer bound parameters instead of string interpolation.

### When to use textual SQL

- complex vendor-specific statements
- hand-written SQL already available
- migration/administration tasks
- incremental adoption

### Compilation
SQLAlchemy compiles Python expressions into dialect-specific SQL.

Useful ideas:

- same expression may compile differently on PostgreSQL vs SQLite
- literal rendering for debugging exists, but not for routine production logic
- custom compilation is possible for advanced extensions via compiler hooks

---

## 13) Types and custom types

### Built-in type families

- `Integer`
- `BigInteger`
- `String`
- `Text`
- `Boolean`
- `Date`
- `DateTime`
- `Time`
- `Float`
- `Numeric`
- `LargeBinary`
- `JSON`
- `Enum`
- `UUID` or dialect-specific UUID handling

### TypeEngine
All SQLAlchemy types derive from `TypeEngine`.

### Dialect adaptation
A type may compile differently depending on backend. Example: JSON support is dialect-aware.

### Type decorators
Use `TypeDecorator` to customize bind/result behavior.

Typical reasons:

- serialize/deserialize custom Python types
- normalize values going in/out
- wrap existing types with custom behavior

Example sketch:

```python
from sqlalchemy.types import TypeDecorator, String

class LowercaseString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.lower() if value is not None else value
```

### Important distinction
- `TypeEngine` = core type abstraction
- `TypeDecorator` = custom behavior around an existing type
- dialect-specific types = backend-specific features

---

## 14) Defaults and server-generated values

There are multiple layers of “default” behavior.

### Client-side default
Executed on the Python/SQLAlchemy side:

```python
Column("created_at", DateTime, default=datetime.utcnow)
```

### Server-side default
Defined at the database side:

```python
Column("created_at", DateTime, server_default=func.now())
```

### Other concepts

- `onupdate=...`
- sequences / identity columns
- autoincrement behavior
- fetched values / server-generated defaults
- computed columns on supporting backends

### Important distinction
Client defaults are generated by Python when SQLAlchemy builds the statement.
Server defaults are generated by the database itself.

---

## 15) Reflection and database inspection

Reflection means building SQLAlchemy schema objects from an existing database.

### Reflect a table
```python
user_table = Table("user_account", metadata, autoload_with=engine)
```

### Reflect many tables
```python
metadata.reflect(engine)
```

### Uses of reflection

- integrating with existing databases
- admin/reporting tools
- automap
- migration scripts
- schema discovery/introspection

### Reflection caveats

- reflected objects depend on database capabilities
- some backend-specific features may not round-trip perfectly
- explicit models are still better for long-term application design

---

## 16) Declarative ORM mapping

Declarative is the dominant ORM mapping style.

### Base class
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### Basic mapped class
```python
class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None]
```

### Declarative concepts

- class ↔ table mapping
- attributes ↔ columns / relationships
- class registry
- metadata integration through `Base.metadata`
- optional explicit `__table_args__`
- optional explicit `__mapper_args__`

### Declarative vs imperative mapping

- **Declarative**: mapping info is placed on the class body
- **Imperative/classical**: mapping is configured separately

Both are supported, but declarative is the normal modern choice.

---

## 17) Mapped attributes and typed mappings

### `Mapped[...]`
`Mapped[T]` is the modern typed annotation used for ORM mapped attributes.

### `mapped_column()`
Modern ORM column declaration helper.

### Type inference
With typed declarative mapping, SQLAlchemy can infer datatype/nullability from `Mapped[...]` in many cases.

Examples:

```python
name: Mapped[str]
age: Mapped[int | None]
```

### Common mapped attribute categories

- scalar columns
- relationships
- column properties
- hybrid attributes
- composite attributes
- synonyms / custom descriptors

### Key attribute options

- `nullable`
- `default`
- `server_default`
- `index`
- `unique`
- `deferred`
- `init`, `repr`, `compare` in dataclass-oriented patterns

### Non-mapped attributes
Not every attribute on the class is mapped. Plain Python attributes can exist too.

---

## 18) Relationships

Relationships are one of the most important ORM topics.

### Basic relationship patterns

- one-to-many
- many-to-one
- one-to-one
- many-to-many
- association object pattern

### One-to-many / many-to-one
```python
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)

    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="addresses")
```

### One-to-one
Usually modeled by a scalar relationship plus a uniqueness guarantee in the schema.

### Many-to-many
Uses an association table:

```python
association_table = Table(
    "user_group",
    Base.metadata,
    Column("user_id", ForeignKey("user_account.id"), primary_key=True),
    Column("group_id", ForeignKey("group_table.id"), primary_key=True),
)
```

Then:

```python
relationship(secondary=association_table, back_populates=...)
```

### Association object pattern
Use when the join table has additional columns and should be mapped as its own class.

### Common relationship arguments

- `back_populates`
- `backref` (convenience, but explicit `back_populates` is often clearer)
- `secondary`
- `uselist`
- `order_by`
- `cascade`
- `lazy`
- `viewonly`
- `foreign_keys`
- `primaryjoin`
- `secondaryjoin`
- `remote_side`
- `passive_deletes`
- `single_parent`

### Important principle
A relationship is **not** just a foreign key. It is an ORM-level mapping rule that tells SQLAlchemy how objects are associated.

---

## 19) Configuring relationship joins

Default relationship joins are inferred from foreign keys, but advanced schemas often need custom configuration.

### Common advanced cases

- multiple foreign key paths between same tables
- self-referential relationships
- composite foreign keys
- custom join conditions
- relationships using secondary joins
- aliased targets
- adjacency lists / trees

### Tools you should know

- `foreign_keys=...`
- `primaryjoin=...`
- `secondaryjoin=...`
- `remote_side=...`
- `overlaps=...` (when SQLAlchemy warns about overlapping write paths)
- `viewonly=True` for read-only relationship definitions

### Self-referential example concept
Parent/child categories often use `remote_side` to distinguish local vs remote column role.

---

## 20) Session, identity map, and unit of work

The `Session` is the ORM’s central working object.

### What the Session does

- tracks ORM objects
- stages inserts/updates/deletes
- manages transaction boundaries
- coordinates flushes
- maintains an **identity map**
- issues SQL as needed to synchronize Python objects with the database

### Identity map
Within one session, one database row generally corresponds to one Python object identity.

That means repeated loads of the same row usually return the same in-memory instance within that session.

### Unit of Work
SQLAlchemy collects object changes and decides which INSERT/UPDATE/DELETE statements to emit during flush.

### Session creation patterns

```python
with Session(engine) as session:
    ...
```

Or factory-based:

```python
SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as session:
    ...
```

### Common session methods

- `add()`
- `add_all()`
- `delete()`
- `flush()`
- `commit()`
- `rollback()`
- `execute()`
- `scalars()`
- `get()`
- `refresh()`
- `expire()`
- `expunge()`
- `merge()`
- `close()`

### Autoflush
Autoflush means SQLAlchemy may flush pending changes before certain query/execution operations so results remain consistent.

You can disable globally or temporarily:

- `sessionmaker(autoflush=False)`
- `with session.no_autoflush: ...`

### Expiration
By default, committed objects may be expired so later attribute access refreshes from the database if needed. `expire_on_commit=False` is often used in web-app patterns.

### Autobegin
In 2.x, sessions automatically begin a transaction on first use unless configured otherwise.

### Best practices

- treat a session as a **unit-of-work boundary**, not a global singleton
- do not share one session across unrelated requests/jobs
- close sessions promptly
- rollback after exceptions before reusing a session
- a session is not the same as a database connection

---

## 21) Object state management

ORM instances move through states.

### Main object states

- **transient** — plain Python object, not in a session, not persisted
- **pending** — added to session, not yet flushed to DB
- **persistent** — associated with a session and represented in DB
- **deleted** — marked for deletion in current unit of work
- **detached** — not currently associated with a session, but previously persistent

### Common state transitions

- `obj = User(...)` → transient
- `session.add(obj)` → pending
- `session.flush()` / `commit()` → persistent
- `session.delete(obj)` → deleted
- `session.close()` / `expunge(obj)` → detached

### Expire / refresh
- `expire(obj)` marks attributes to be reloaded later
- `refresh(obj)` immediately reloads from DB

### Merge
`merge()` copies state from a detached/transient object graph into the current session.

Use with care; it is powerful but often misunderstood.

### Inspection
`inspect(obj)` can expose state information.

---

## 22) Querying with the ORM (2.x style)

### Core idea
Use `select()` with ORM entities.

```python
stmt = select(User)
users = session.scalars(stmt).all()
```

### Filtering
```python
stmt = select(User).where(User.name == "alice")
```

### Filter by keyword convenience
```python
stmt = select(User).filter_by(name="alice")
```

### Get by primary key
```python
user = session.get(User, 1)
```

### Scalar vs execute

- `session.execute(stmt)` → generic result
- `session.scalars(stmt)` → scalar/entity stream
- `session.scalar(stmt)` → one scalar value

### Joins
```python
stmt = select(User).join(User.addresses)
```

### Load options
```python
stmt = select(User).options(selectinload(User.addresses))
```

### Aggregates
```python
stmt = select(func.count(User.id))
count = session.scalar(stmt)
```

### ORM-enabled DML
2.x also supports ORM-enabled `insert()`, `update()`, and `delete()` patterns, especially bulk-style operations with WHERE criteria. These bypass some normal per-instance unit-of-work behavior, so you must understand synchronization implications.

### Legacy Query API
`session.query(...)` still exists as a legacy API, but **do not learn it as the primary modern style**.

---

## 23) Loader strategies and relationship loading

Relationship loading is a major performance topic.

### Main loader strategies

- **lazy loading** (`lazy="select"`): loads relationship when accessed
- **joined eager loading** (`joinedload`)
- **select IN eager loading** (`selectinload`)
- **subquery eager loading** (`subqueryload`)
- **raise loading** (`raiseload`)
- **no loading** (`noload`)

### Recommended default instinct
For collection relationships in many real applications, `selectinload()` is often a strong default choice because it avoids many N+1 issues without row explosion.

### N+1 problem
If you load many parent objects and then lazily access each child collection one by one, you may emit one query for parents plus many additional queries for children.

### `joinedload()`
Uses joins to eager load, good for certain scalar/low-cardinality relationships, but can duplicate parent rows and may need `unique()` when consuming ORM rows.

### `selectinload()`
Loads related rows in a second query using `IN (...)` against loaded parent keys.

### `subqueryload()`
Older eager pattern still available; useful in some cases but `selectinload()` is often preferred.

### `raiseload()`
Very useful in performance-sensitive code/tests because it raises if an unexpected lazy load occurs.

### `contains_eager()`
Used when you already wrote explicit joins and want SQLAlchemy to populate relationship attributes from them.

### Column loading options
Also learn:

- `load_only()`
- `defer()`
- `undefer()`
- `undefer_group()`

---

## 24) Cascades and delete behavior

Cascades control how operations propagate across relationships.

### Common cascade options

- `save-update`
- `merge`
- `delete`
- `delete-orphan`
- `refresh-expire`
- `expunge`
- `all` (shorthand)

### Important ideas

#### `delete`
Deleting a parent may also mark related children for deletion.

#### `delete-orphan`
If a child is removed from its parent collection and should no longer exist independently, `delete-orphan` is often appropriate.

Typical use: true ownership relationships.

### ORM cascade vs database cascade
These are different layers:

- **ORM cascade** = SQLAlchemy object graph behavior
- **database `ON DELETE CASCADE`** = database foreign-key behavior

They can be combined, but you must configure them intentionally.

### `passive_deletes`
Useful when relying on database-side cascades and you do not want SQLAlchemy to load dependent rows unnecessarily.

### Caution
Do not apply delete cascades casually on many-to-many/shared-child models.

---

## 25) Inheritance mappings

SQLAlchemy ORM supports three inheritance strategies.

### 1. Single-table inheritance
- all classes stored in one table
- discriminator column identifies subtype
- simplest schema
- can create sparse/null-heavy tables

### 2. Joined-table inheritance
- base table plus subclass tables
- normalized schema
- subclass load often requires joins

### 3. Concrete-table inheritance
- each class has its own full table
- less commonly used
- can be more complex for polymorphic queries

### Concepts to know

- polymorphic loading
- discriminator / `polymorphic_on`
- `polymorphic_identity`
- base vs subclass mappers
- performance tradeoffs by inheritance style

---

## 26) Advanced mapped attributes

Beyond plain columns and relationships, SQLAlchemy ORM supports richer attribute techniques.

### `column_property()`
Map SQL expressions as attributes.

### Hybrids
`hybrid_property` and `hybrid_method` allow attributes/methods that work both:

- in Python instance logic
- in SQL expression context

Very powerful for reusable business logic.

### Synonyms
Expose alternate names for mapped attributes.

### Composites
Group multiple columns into one value object.

### Validators / attribute behavior
Validation and attribute transformation can be handled with:

- `@validates`
- descriptors / properties
- events
- custom attribute instrumentation

---

## 27) Additional persistence techniques

This section covers advanced write patterns.

Important topics:

- fetching server-generated defaults efficiently
- ORM-enabled INSERT/UPDATE/DELETE statements
- bulk operations and their caveats
- upserts, where supported by dialect-specific insert helpers
- partitioning/custom bind routing patterns
- version counters / optimistic concurrency control
- persistence hooks/events where appropriate

### Version counters
You can map a version column for optimistic concurrency checks.

### Bulk caveat
Bulk-style ORM DML is not the same as regular object-by-object unit-of-work persistence. It may bypass in-memory relationship bookkeeping and some per-instance events.

---

## 28) Async SQLAlchemy

SQLAlchemy supports asyncio through its async extension.

### Main async constructs

- `create_async_engine(...)`
- `AsyncEngine`
- `AsyncConnection`
- `AsyncSession`
- `async_sessionmaker`

### Basic pattern

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async with SessionLocal() as session:
    result = await session.scalars(select(User))
    users = result.all()
```

### Important async rules

- Use an **async-capable driver** (`asyncpg`, `aiosqlite`, etc.)
- `await` async execution methods
- Be careful with lazy loading in async contexts
- Use explicit eager loading patterns to avoid surprising IO during attribute access
- There are sync/async bridging helpers like `run_sync()` in some contexts

### Async caveats
Not every ecosystem integration behaves identically under async; driver support and dialect maturity matter.

---

## 29) Events system

SQLAlchemy has a deep event system for Core and ORM.

### Core event categories
Examples include:

- engine / connection events
- pool events
- transaction lifecycle events
- execution events

### ORM event categories
Examples include:

- mapper events
- session events
- instance events
- attribute events
- query/load lifecycle hooks

### When events are useful

- auditing/logging
- data normalization
- custom lifecycle behaviors
- instrumentation/metrics
- enforcing application rules
- advanced extension points

### Caution
Events are powerful, but excessive event-driven logic can make code harder to reason about. Prefer explicit model/session logic first; use events where cross-cutting behavior is genuinely warranted.

---

## 30) ORM extensions you should know

Not every project needs these, but you should know they exist.

### Asynchronous I/O
Official async extension.

### Association Proxy
Expose a simplified relationship-based attribute view over association objects or related attributes.

### Automap
Generate mapped classes automatically from an existing reflected schema.

### Hybrid Attributes
Reusable Python/SQL dual-context properties/methods.

### Mutation Tracking
Tracks in-place changes for mutable column values like JSON/list/dict wrappers.

### Ordering List
Helps maintain position/index fields in ordered child collections.

### Horizontal Sharding
Advanced partitioning/sharding support.

### Indexable
Helpers for indexable column structures.

### Alternate Class Instrumentation
Advanced customization of ORM instrumentation.

### Baked Queries
Historically relevant extension; not a central concept for modern 2.x learning.

---

## 31) Dataclasses, attrs, and typing

### Dataclass integration
SQLAlchemy can integrate with Python dataclasses for mapped classes.

Concepts to know:

- generated `__init__`
- field defaults vs SQLAlchemy defaults
- mapped fields vs non-mapped fields
- dataclass configuration interacting with ORM instrumentation

### attrs integration
Also supported.

### Typing support
Modern SQLAlchemy emphasizes typed mappings:

- `Mapped[T]`
- `mapped_column()`
- typing-friendly declarative patterns
- mypy / PEP 484 support

### Practical takeaway
For new code, typed declarative mappings are the modern standard.

---

## 32) Dialect-specific behavior

SQLAlchemy is backend-agnostic in API design, but not everything is identical across databases.

### What the dialect affects

- SQL rendering syntax
- types
- autoincrement / identity behavior
- `RETURNING` support
- JSON support
- upsert syntax
- reflection capabilities
- transaction quirks
- locking syntax
- schema semantics

### Examples

- PostgreSQL has rich `RETURNING`, JSON/JSONB, array, upsert support
- SQLite has unique transactional and connection caveats, especially in-memory/testing use
- MySQL/MariaDB have engine/isolation/autocommit specific behaviors
- Oracle and SQL Server have their own identity, schema, and SQL syntax differences

### Important mindset
Write to SQLAlchemy abstractions where possible, but know your target database.

---

## 33) Errors, debugging, and troubleshooting

### Common failure categories

- connection failures
- pool exhaustion
- invalid transaction state
- mapping configuration errors
- relationship ambiguity
- detached-instance errors
- flush/constraint violations
- integrity errors from database
- lazy loading in invalid contexts
- async driver / greenlet related issues

### Debugging tools

- `echo=True`
- Python logging for `sqlalchemy.engine`
- inspecting compiled SQL
- `inspect()` for ORM objects/mappers
- reading exception chains carefully

### Important exception families
You should recognize:

- DBAPI-wrapped exceptions such as integrity/operational/programming errors
- ORM configuration exceptions
- result cardinality exceptions (`NoResultFound`, `MultipleResultsFound`)
- pool/timeout issues

### Rule
When the DB raises an integrity or syntax issue, SQLAlchemy often wraps but preserves the underlying database error context.

---

## 34) Performance and best practices

### Core performance ideas

- use connection pooling correctly
- keep transactions short
- batch inserts when possible
- avoid per-row round trips
- use `RETURNING` efficiently where available
- understand when textual SQL may be appropriate

### ORM performance ideas

- avoid N+1 relationship loads
- choose loader strategies intentionally
- avoid loading huge object graphs if you only need a few columns
- use `load_only`, `defer`, and SQL aggregates when full objects are unnecessary
- beware row explosion with joined eager loading
- do not keep sessions open forever
- bulk patterns differ from unit-of-work patterns

### Design best practices

- one engine per DB/process
- one session per request/job/unit of work
- explicit transaction scopes
- explicit relationship configuration
- use naming conventions for schema objects
- separate schema migrations from app startup
- prefer 2.x style `select()` API consistently

---

## 35) Testing patterns

### Common testing ideas

- create a dedicated test engine
- create/drop schema around tests, or use migrations
- wrap each test in a transaction and roll it back
- use session fixtures/factories
- use SQLite carefully; behavior can differ from production DB
- if production uses PostgreSQL, integration tests against PostgreSQL catch more real issues

### SQLite caution
SQLite is great for many tests, but it is not behaviorally identical to PostgreSQL/MySQL/Oracle/SQL Server.

---

## 36) Migration concepts: 1.4/legacy to 2.x

This matters a lot because older tutorials often teach outdated habits.

### Major migration ideas

- **ORM querying is unified with Core `select()`**
- explicit transaction handling is emphasized
- older implicit patterns are reduced/removed
- the legacy `Query` interface is no longer the primary style
- old “autocommit” application patterns are removed; driver-level autocommit is a separate concept
- typed declarative mappings with `Mapped[...]` / `mapped_column()` are the modern style

### Practical migration advice

If you are revising SQLAlchemy now, learn these as defaults:

- `select(User)` not `session.query(User)`
- `with Session(...) as session:` explicit scoping
- explicit commit/rollback logic
- typed declarative models
- modern loader options and result APIs (`scalars()`, `scalar()`, `mappings()`)

---

## 37) How Alembic fits in

Alembic is the migration tool commonly used with SQLAlchemy.

### Why it matters
SQLAlchemy itself defines schema objects and can emit create/drop DDL, but **schema migration/versioning** is normally handled by Alembic.

### Conceptual relation

- SQLAlchemy = schema definitions, runtime DB toolkit, ORM
- Alembic = schema migration history and upgrade/downgrade scripts

### Important real-world practice
Do not rely on `create_all()` as your production migration strategy.

---

## 38) Revision checklist

If you can explain all of these clearly, your SQLAlchemy fundamentals are strong:

### Foundation
- [ ] What Core is
- [ ] What ORM is
- [ ] How 2.x unifies ORM querying with `select()`
- [ ] What a dialect and DBAPI driver are

### Engine / execution
- [ ] `create_engine()`
- [ ] `Engine`, `Connection`, `Result`
- [ ] transactions, commit, rollback, savepoints
- [ ] pooling and common pool settings

### Schema
- [ ] `MetaData`, `Table`, `Column`
- [ ] foreign keys, unique/check constraints, indexes
- [ ] `create_all()`, `drop_all()`
- [ ] reflection

### SQL Expression Language
- [ ] `select()`
- [ ] joins, subqueries, aliases, CTEs
- [ ] `func`, `case`, `exists`
- [ ] `insert()`, `update()`, `delete()`
- [ ] textual SQL via `text()`

### Types / defaults
- [ ] built-in types
- [ ] `TypeDecorator`
- [ ] Python defaults vs server defaults
- [ ] server-generated values and `RETURNING`

### ORM mapping
- [ ] `DeclarativeBase`
- [ ] `Mapped[...]`
- [ ] `mapped_column()`
- [ ] relationships and relationship arguments
- [ ] `__table_args__`, `__mapper_args__`

### Session / unit of work
- [ ] identity map
- [ ] unit of work
- [ ] object states
- [ ] autoflush
- [ ] expire/refresh
- [ ] detached objects and `merge()`

### Querying / loading
- [ ] `session.get()`
- [ ] `session.scalars(select(...))`
- [ ] eager vs lazy loading
- [ ] `joinedload`, `selectinload`, `subqueryload`
- [ ] N+1 problem
- [ ] `load_only`, `defer`, `raiseload`

### Advanced ORM
- [ ] cascades and `delete-orphan`
- [ ] `ON DELETE CASCADE` vs ORM cascades
- [ ] inheritance styles
- [ ] hybrid properties
- [ ] association proxy
- [ ] automap
- [ ] version counters

### Async / ecosystem
- [ ] `create_async_engine()`
- [ ] `AsyncSession`
- [ ] async driver requirements
- [ ] Alembic’s role
- [ ] dialect-specific behavior

---

## 39) Official references

These are the best official references for continuing revision.

### Top-level docs
- SQLAlchemy 2.0 documentation home: https://docs.sqlalchemy.org/en/20/
- Unified tutorial: https://docs.sqlalchemy.org/en/20/tutorial/index.html
- Overview: https://docs.sqlalchemy.org/intro.html

### Core
- Engine configuration: https://docs.sqlalchemy.org/en/20/core/engines.html
- Engines and connections: https://docs.sqlalchemy.org/en/20/core/connections.html
- Connection pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html
- Metadata/schema: https://docs.sqlalchemy.org/en/20/core/metadata.html
- Constraints and indexes: https://docs.sqlalchemy.org/en/20/core/constraints.html
- Defaults: https://docs.sqlalchemy.org/en/20/core/defaults.html
- Reflection: https://docs.sqlalchemy.org/en/20/core/reflection.html
- Type basics: https://docs.sqlalchemy.org/en/20/core/type_basics.html
- Custom types: https://docs.sqlalchemy.org/en/20/core/custom_types.html
- SQL expression elements: https://docs.sqlalchemy.org/en/20/core/sqlelement.html
- Selectables: https://docs.sqlalchemy.org/en/20/core/selectable.html
- Core events: https://docs.sqlalchemy.org/en/20/core/events.html

### ORM
- ORM quick start: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- ORM mapped class overview: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html
- Declarative table configuration: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
- Basic relationships: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
- Join condition configuration: https://docs.sqlalchemy.org/en/20/orm/join_conditions.html
- Session basics: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- ORM querying guide: https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
- Relationship loading techniques: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- Cascades: https://docs.sqlalchemy.org/en/20/orm/cascades.html
- Inheritance mappings: https://docs.sqlalchemy.org/en/20/orm/inheritance.html
- Mapped attributes / changing attribute behavior: https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html
- Persistence techniques: https://docs.sqlalchemy.org/en/20/orm/persistence_techniques.html
- ORM events: https://docs.sqlalchemy.org/en/20/orm/events.html
- Dataclasses / attrs integration: https://docs.sqlalchemy.org/en/20/orm/dataclasses.html

### Extensions
- Asyncio extension: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- ORM extensions index: https://docs.sqlalchemy.org/en/20/orm/extensions/index.html
- Hybrid attributes: https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html
- Association proxy: https://docs.sqlalchemy.org/en/20/orm/extensions/associationproxy.html
- Automap: https://docs.sqlalchemy.org/en/20/orm/extensions/automap.html
- Mypy / typing support: https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html

### Migration / troubleshooting
- Error messages: https://docs.sqlalchemy.org/en/20/errors.html
- FAQ: https://docs.sqlalchemy.org/en/20/faq/index.html
- Major migration guide to 2.0: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
- What’s new in 2.0: https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html

---

## Final advice for revision

When revising SQLAlchemy, study in this order:

1. Engine / Connection / transactions
2. MetaData / Table / Column / SQL expressions
3. Declarative mapping
4. Session / unit of work / object states
5. Relationships
6. ORM querying + loader strategies
7. Cascades / inheritance / advanced attributes
8. Async / events / extensions
9. Dialect-specific behavior
10. Migration concepts

If you internalize the **Core + Session + mapping + relationship loading** model, most of the library becomes much easier.
