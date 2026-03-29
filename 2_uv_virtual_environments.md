# Production-Grade Python Project Management with `uv` + Python Virtual Environment Internals

_Last validated against official `uv`, Python, and PEP documentation on 2026-03-29._

---

## How to use this document

This is a revision-grade reference for two topics:

1. **Production-grade Python project management with `uv`**
2. **How Python virtual environments actually work internally across operating systems**

The document is intentionally opinionated where “production-grade” workflow choices matter, but the technical details are grounded in the current official `uv` and Python documentation.

---

## Table of contents

1. [What `uv` is and where it fits](#what-uv-is-and-where-it-fits)
2. [The production-grade mental model](#the-production-grade-mental-model)
3. [Core project files managed by `uv`](#core-project-files-managed-by-uv)
4. [Choosing the right project shape](#choosing-the-right-project-shape)
5. [Python version management with `uv`](#python-version-management-with-uv)
6. [Dependency modeling in `pyproject.toml`](#dependency-modeling-in-pyprojecttoml)
7. [Sources, workspaces, editables, and local development](#sources-workspaces-editables-and-local-development)
8. [Locking, syncing, and reproducibility](#locking-syncing-and-reproducibility)
9. [Running commands and scripts correctly](#running-commands-and-scripts-correctly)
10. [Configuration that matters in real projects](#configuration-that-matters-in-real-projects)
11. [Build systems, packaging, and publishing](#build-systems-packaging-and-publishing)
12. [Private indexes, authentication, and enterprise concerns](#private-indexes-authentication-and-enterprise-concerns)
13. [Resolution controls for difficult dependency graphs](#resolution-controls-for-difficult-dependency-graphs)
14. [Caching, CI, Docker, and deployment patterns](#caching-ci-docker-and-deployment-patterns)
15. [Tools, scripts, audit, and ecosystem integration](#tools-scripts-audit-and-ecosystem-integration)
16. [Production-grade defaults checklist](#production-grade-defaults-checklist)
17. [Common mistakes and anti-patterns](#common-mistakes-and-anti-patterns)
18. [Python virtual environments: the real internal model](#python-virtual-environments-the-real-internal-model)
19. [What activation really does](#what-activation-really-does)
20. [Cross-platform virtualenv layout and behavior](#cross-platform-virtualenv-layout-and-behavior)
21. [Advanced virtualenv internals](#advanced-virtualenv-internals)
22. [Debugging and introspection snippets](#debugging-and-introspection-snippets)
23. [Short revision summary](#short-revision-summary)
24. [Official references](#official-references)

---

## What `uv` is and where it fits

`uv` is a Python package and project manager that brings together workflows that historically required multiple tools such as `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, and `virtualenv`. In one toolchain, it can:

- create and manage Python projects
- create virtual environments
- install and manage Python versions
- resolve and lock dependencies
- run scripts with isolated dependencies
- install and run Python-based tools
- build and publish packages
- provide a pip-compatible interface when you need lower-level control

For production work, the most important feature is not just speed. It is that `uv` gives you a **single coherent model** for:

- Python interpreter selection
- dependency declaration
- environment creation
- locking
- syncing
- packaging
- CI and container usage

That coherence is what reduces “works on my machine” failures.

### The most important conceptual split in `uv`

`uv` has **two major interfaces**:

### 1. The **high-level project interface**
This is the preferred model for modern projects.

Typical commands:

```bash
uv init
uv add
uv remove
uv lock
uv sync
uv run
uv tree
uv build
uv publish
uv version
uv audit
```

Use this for repositories that should be reproducible, collaborative, and production-safe.

### 2. The **pip-compatible interface**
This is for migration, legacy workflows, or cases where you need direct environment mutation.

Typical commands:

```bash
uv venv
uv pip install
uv pip sync
uv pip compile
uv pip freeze
uv pip list
uv pip check
```

Use this when:
- you are migrating from `pip` / `pip-tools`
- you are not ready to fully adopt project-managed environments
- you need one-off low-level control

For new production repositories, prefer the **project interface**.

---

## The production-grade mental model

The cleanest mental model is:

### 1. Python version is part of the contract
You should declare and pin which Python you develop against.

### 2. Dependencies are declared statically
They live in `pyproject.toml`, not in ad-hoc shell history.

### 3. Exact resolution is recorded
That is what `uv.lock` is for.

### 4. Environments are disposable
`.venv` is an artifact, not source code.

### 5. CI must verify, not silently mutate
In CI and release pipelines, use commands that **fail** if lockfiles drift.

### 6. Project commands should run inside the managed environment
Use `uv run` instead of depending on manual shell activation.

### 7. Packaging is explicit
If a repo is a package, define a build system. If it is not a package, do not pretend it is one.

### 8. Production reproducibility depends on discipline
Committing `uv.lock`, pinning Python, and separating dev groups from runtime dependencies matters more than any single tool.

---

## Core project files managed by `uv`

A `uv` project revolves around a small set of files.

## `pyproject.toml`

This is the source of truth for:

- project metadata
- supported Python range
- dependencies
- optional dependencies (“extras”)
- dependency groups
- build system
- `tool.uv` configuration

This is the file you review in code review.

## `.python-version`

This pins the default Python version for the project.

Use it so that:
- local development is consistent
- CI can respect the same version
- `uv` knows which interpreter to create the environment with

## `.venv`

This is the project environment.

Important:
- treat it as disposable
- do **not** commit it
- do **not** treat it as portable
- recreate it from the project metadata and lockfile when necessary

## `uv.lock`

This records the exact resolved dependency set.

For production application repos, commit it.

That gives you:
- deterministic installs across machines
- consistent CI
- known dependency state for deployments

### Recommended repo treatment

Commit:
- `pyproject.toml`
- `.python-version`
- `uv.lock`

Do not commit:
- `.venv`
- cache directories
- build artifacts like `dist/`

---

## Choosing the right project shape

`uv init` supports multiple shapes, and production correctness starts with choosing the right one.

## Application vs library

### Application
Choose this when:
- the repo primarily runs a service, script collection, CLI app, worker, API, or batch job
- you do not primarily publish the project as a reusable distribution

### Library
Choose this when:
- the repo is meant to be imported by other projects
- you care about packaging semantics, entry points, wheels, and publishing

## Packaged vs non-packaged project

This is a very important distinction in `uv`.

If a project has a `[build-system]` table, `uv` treats it as something that should be built and installed into the environment.

If a project does **not** define a build system:
- `uv` will not build/install the project itself during normal `uv sync`
- it will still manage dependencies for the repo

That means some repositories should intentionally stay as **non-package apps**:
- simple internal apps
- script repos
- flat-layout repositories
- repos that do not need distribution metadata

And some should definitely be **packages**:
- libraries
- reusable internal components
- projects with console entry points
- projects using a `src/` layout
- things you publish or version as artifacts

### Good rule

If the repository should be importable and installable as a first-party package, define a build system.

If it is mostly “run code in this repo with these dependencies”, you may not need packaging.

---

## Python version management with `uv`

Interpreter management is one of the biggest reasons `uv` is useful in production.

## Key commands

### Install Python
```bash
uv python install
uv python install 3.12
uv python install 3.11 3.12
```

### Install alternative implementations
```bash
uv python install [email protected]
```

### List versions
```bash
uv python list
```

### Create a venv with a specific interpreter
```bash
uv venv --python 3.12
```

## What `uv` does here

`uv` can:
- use a system Python if suitable
- install a managed Python automatically when needed
- honor project version pins
- create environments from the selected interpreter

Important nuance:
- Python does **not** publish official distributable CPython binaries for this purpose
- `uv` uses Astral’s `python-build-standalone` distributions for managed Python installs

## What to pin

### Pin the Python family in `pyproject.toml`
```toml
[project]
requires-python = ">=3.12,<3.13"
```

This controls:
- which syntax your project can rely on
- which dependency versions are eligible during resolution

### Pin the working interpreter in `.python-version`
Example:
```text
3.12
```

This controls the default local interpreter used for the repo.

## Production recommendation

For production application repos:

- use a narrow `requires-python` range
- commit `.python-version`
- ensure CI uses the same major/minor version
- avoid “whatever Python is on this machine”

### Good example

```toml
[project]
name = "my-service"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
```

and

```text
# .python-version
3.12
```

This is much safer than:
```toml
requires-python = ">=3.9"
```

unless you truly test all supported versions.

---

## Dependency modeling in `pyproject.toml`

This is where many Python repos become messy. `uv` supports a very good dependency taxonomy. Use it.

## The four important buckets

### 1. `project.dependencies`
Runtime dependencies required by the project.

Example:
```toml
[project]
dependencies = [
  "fastapi>=0.115,<1",
  "uvicorn>=0.30,<1",
  "pydantic>=2.10,<3",
]
```

Use for:
- packages required in production runtime
- dependencies that ship with your application or library

### 2. `project.optional-dependencies`
Published optional dependencies, also called **extras**.

Example:
```toml
[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.2,<4"]
redis = ["redis>=5,<6"]
```

Use for:
- installable feature sets
- public package options
- user-facing optional functionality

Do **not** use extras as your default place for internal dev tooling unless you specifically want those extras to be part of the package’s public surface.

### 3. `dependency-groups`
Local groups of dependencies, especially for development.

Example:
```toml
[dependency-groups]
dev = ["pytest>=8,<9", "ruff>=0.11,<0.12", "mypy>=1.15,<2"]
docs = ["mkdocs>=1.6,<2"]
```

Use for:
- linting
- testing
- typing
- docs
- build-only helpers
- local/dev/CI concerns

This is the best default place for development dependency organization.

### 4. `tool.uv.sources`
Non-standard development sources such as:
- Git dependencies
- path dependencies
- workspace members
- index-specific sources
- editable path installs

---

## Adding dependencies with `uv`

### Runtime dependency
```bash
uv add httpx
```

### Explicit version range
```bash
uv add "httpx>=0.27,<1"
```

### Dev dependency
```bash
uv add --dev pytest
```

### Specific dependency group
```bash
uv add --group lint ruff
uv add --group typecheck mypy
```

### Optional dependency / extra
```bash
uv add --optional postgres "psycopg[binary]>=3.2,<4"
```

### Remove dependencies
```bash
uv remove httpx
uv remove --group lint ruff
```

---

## Version specifier strategy

For production-grade repos, avoid both extremes.

### Too loose
```toml
dependencies = ["fastapi"]
```

### Too strict too early
```toml
dependencies = ["fastapi==0.115.0"]
```

### Better
```toml
dependencies = ["fastapi>=0.115,<1"]
```

Let:
- `pyproject.toml` express acceptable policy
- `uv.lock` express exact reality

That split is one of the healthiest packaging patterns.

---

## Markers and platform-specific dependencies

Use environment markers when the dependency truly varies by platform or interpreter version.

Example:
```bash
uv add "jax; sys_platform == 'linux'"
uv add "importlib_metadata; python_version < '3.10'"
```

This keeps the dependency model explicit instead of encoding platform logic in CI scripts.

### Good uses
- Windows-only packages
- Linux-only GPU/runtime packages
- backports for older Python versions

### Bad uses
- hiding inconsistent application behavior
- papering over undeclared platform support

---

## Dependency groups done properly

A mature project rarely has only `dev`. Split by purpose.

### Recommended group layout

```toml
[dependency-groups]
test = [
  "pytest>=8,<9",
  "pytest-cov>=5,<6",
]

lint = [
  "ruff>=0.11,<0.12",
]

typecheck = [
  "mypy>=1.15,<2",
]

dev = [
  { include-group = "test" },
  { include-group = "lint" },
  { include-group = "typecheck" },
]
```

This gives you:
- narrow CI jobs
- reusable group combinations
- clearer local intent

### Important behavior

- `uv` resolves all groups together when locking
- conflicting groups must be declared as conflicts if they are intentionally mutually exclusive
- the `dev` group is special-cased and is included by default

### Default groups

By default, `uv` includes the `dev` group in the environment for commands like `uv run` and `uv sync`.

You can control this with:

```toml
[tool.uv]
default-groups = ["dev", "docs"]
```

or

```toml
[tool.uv]
default-groups = "all"
```

### Useful commands

```bash
uv sync --group test
uv sync --only-group lint
uv sync --no-group docs
uv sync --all-groups
uv sync --no-default-groups
```

---

## Group-specific Python requirements

Sometimes a group legitimately needs a newer Python than the application runtime.

Example:
- app supports Python 3.10+
- type-checking or docs tool only supports 3.11+

`uv` allows group-level `requires-python` configuration under `tool.uv.dependency-groups`.

Use this carefully. In most repos, it is simpler if tooling works on the project’s primary Python version.

---

## Sources, workspaces, editables, and local development

This is where `uv` becomes much stronger than plain `pip`.

## Git sources

Example:
```bash
uv add "httpx @ git+https://github.com/encode/httpx"
```

This stores the dependency in the standard dependency list and the source mapping in `tool.uv.sources`.

Use Git sources when:
- you truly need unreleased upstream changes
- you maintain an internal fork

Avoid them when:
- a published release would do
- you are just bypassing version policy discipline

Git dependencies increase operational risk.

---

## Path dependencies

These are useful for local development and monorepos.

Example pattern:
```toml
[project]
dependencies = ["shared-lib"]

[tool.uv.sources]
shared-lib = { path = "../shared-lib" }
```

### Editable path dependency

For active development:
```bash
uv add --editable ../shared-lib
```

Use editable installs for:
- code you are actively changing
- local multi-repo development
- internal iteration

Do not overuse them in deployment builds.

---

## Workspace members

For monorepos, prefer **workspaces** instead of ad-hoc path wiring.

A workspace is a collection of packages managed together with a **single lockfile**.

Example:
```toml
[tool.uv.workspace]
members = [
  "packages/api",
  "packages/core",
  "packages/cli",
]
```

A workspace member dependency is declared with:

```toml
[project]
dependencies = ["core"]

[tool.uv.sources]
core = { workspace = true }
```

### Why workspaces matter

They give you:
- one dependency universe
- one lockfile
- explicit relationships between packages
- reproducibility across the monorepo
- less path-hacking

### Important workspace behavior

- `uv lock` operates on the entire workspace
- `uv run` and `uv sync` default to the workspace root
- use `--package <name>` to target a specific member
- workspace packages are always editable by default

### When to use workspaces

Use them when:
- multiple packages live in one repo
- they share common dependency policy
- they should be resolved together

Do not use them when:
- packages are independent and should evolve separately
- one repo is just vendoring unrelated projects

---

## Virtual dependencies

`uv` can treat some path dependencies as “virtual”, meaning the dependency’s package itself is not installed, but its transitive dependencies are.

This is advanced and mainly useful for special repository structures where a directory is dependency-bearing but not a normal package. Most teams do not need this.

---

## Locking, syncing, and reproducibility

This is the heart of production-grade workflow.

## Locking

Locking resolves broad dependency requirements into exact versions.

```bash
uv lock
```

## Syncing

Syncing installs a selected subset of the lockfile into the project environment.

```bash
uv sync
```

## The most important behavior

`uv` automatically locks and syncs in many workflows.

For example:
- `uv run` ensures lockfile and environment are up to date before running
- commands that read the lockfile, such as `uv tree`, also keep it current

This is one reason `uv` feels much more coherent than older Python workflows.

---

## The contract between `pyproject.toml` and `uv.lock`

### `pyproject.toml`
Declares the allowed universe.

### `uv.lock`
Records the chosen exact universe.

That means:

- changing `pyproject.toml` may or may not require new exact versions
- the lockfile is considered outdated if the current locked versions no longer satisfy the metadata
- the lockfile is **not** considered outdated merely because new package releases appeared upstream

This is correct and important.

---

## Exact vs inexact sync

### `uv sync`
By default, this performs **exact sync**.

That means:
- packages present in the lockfile are installed
- packages not present in the lockfile are removed

This is exactly what you want for:
- CI
- clean local environments
- deterministic deployments

### `uv run`
By default, this uses **inexact sync**:
- required packages are ensured present
- extraneous packages are not removed

Use:
```bash
uv run --exact ...
```

when you want exactness during execution.

### `--inexact`
If you explicitly need to keep extra packages:
```bash
uv sync --inexact
```

This is usually a temporary escape hatch, not the default you should build around.

---

## The three most important safety flags

### `--locked`
Use the lockfile, but fail if it is out of date.

```bash
uv run --locked ...
uv sync --locked
```

Use in:
- CI
- release jobs
- production image builds

### `--frozen`
Use the lockfile without checking whether it is up to date.

```bash
uv run --frozen ...
```

Use when:
- you need speed
- you already separately enforce freshness

### `--no-sync`
Run without checking if the environment is up to date.

```bash
uv run --no-sync ...
```

Use sparingly. This weakens guarantees.

---

## Upgrading dependencies intentionally

With an existing lockfile, `uv` prefers already locked versions until you intentionally upgrade.

### Upgrade everything
```bash
uv lock --upgrade
```

### Upgrade one package
```bash
uv lock --upgrade-package fastapi
```

This is excellent for controlled maintenance:
- keep the system stable
- upgrade deliberately
- review lockfile diffs

---

## Exporting lockfiles

The native lockfile is `uv.lock`.

If you must integrate with external tooling:

### Export requirements
```bash
uv export --format requirements.txt
```

### Export `pylock.toml`
```bash
uv export --format pylock.toml
```

Use export only when required.

### Better default
Prefer:
- `pyproject.toml` + `uv.lock`

over:
- maintaining both `uv.lock` and handwritten `requirements.txt`

A second lock representation becomes another drift vector.

---

## Running commands and scripts correctly

## `uv run`

This is the default way to run project commands safely.

Example:
```bash
uv run python -m my_service
uv run pytest
uv run ruff check .
uv run alembic upgrade head
```

Why this is better than manual activation:
- it does not depend on your shell state
- it ensures the environment is current
- it is more reproducible in docs, CI, and team workflows

### Additional dependencies per invocation

You can request extra dependencies for one run:

```bash
uv run --with httpx==0.26.0 python -c "import httpx; print(httpx.__version__)"
```

This is useful for experiments, not for production contracts. If a dependency matters repeatedly, declare it.

---

## PEP 723 scripts

For standalone scripts, `uv` can manage inline metadata.

Example conceptual flow:
```bash
uv add --script tool.py requests
uv run tool.py
uv lock --script tool.py
```

This is excellent for:
- automation scripts
- one-file internal utilities
- reproducible operational scripts

It is not a replacement for a proper project repo when the codebase grows.

---

## Activation vs `uv run`

You can activate `.venv`, but in production-grade workflow:

- prefer `uv run` in documentation
- prefer `uv run` in Makefiles / task runners / CI
- use activation mainly for interactive shell sessions

Manual activation is a convenience layer, not the primary contract.

---

## Configuration that matters in real projects

`uv` configuration can live in:
- `[tool.uv]` in `pyproject.toml`
- `uv.toml`
- user/system config files

For project behavior, the most important place is usually `[tool.uv]`.

---

## High-value `tool.uv` settings

### `default-groups`
Controls which dependency groups are included by default.

```toml
[tool.uv]
default-groups = ["dev", "docs"]
```

### `conflicts`
Declare mutually exclusive extras or groups.

```toml
[tool.uv]
conflicts = [
  [
    { group = "cuda" },
    { group = "cpu" },
  ]
]
```

Use this when a universal lock is possible only if incompatible sets are treated as mutually exclusive.

### `environments`
Restrict the set of environments considered during resolution.

```toml
[tool.uv]
environments = ["sys_platform == 'darwin'"]
```

Use this when you intentionally support a narrower platform set and want faster or simpler locking.

### `required-environments`
Require packages to be available for specific platforms when they lack source distributions.

```toml
[tool.uv]
required-environments = [
  "sys_platform == 'darwin' and platform_machine == 'arm64'",
  "sys_platform == 'linux' and platform_machine == 'x86_64'",
  "sys_platform == 'win32' and platform_machine == 'AMD64'",
]
```

This is valuable in cross-platform teams using binary-heavy dependencies.

### `constraint-dependencies`
Restrict versions during resolution without adding a dependency by itself.

```toml
[tool.uv]
constraint-dependencies = ["grpcio<1.65"]
```

### `override-dependencies`
Force a version even if it violates normal dependency bounds.

```toml
[tool.uv]
override-dependencies = ["werkzeug==2.3.0"]
```

Use overrides very carefully. They are escape hatches, not normal policy.

### `build-constraint-dependencies`
Pin or constrain build dependencies.

```toml
[tool.uv]
build-constraint-dependencies = ["setuptools==60.0.0"]
```

This helps when a package only builds correctly against certain build-time tool versions.

---

## Project environment path

By default, the project environment lives at `.venv`.

You can change the environment path with `UV_PROJECT_ENVIRONMENT`.

Example use case:
- CI
- Docker
- special single-project deployment paths

Do **not** point multiple projects at the same absolute environment path. That is a recipe for corruption and confusion.

---

## Build systems, packaging, and publishing

## Build system basics

A build system defines how a project becomes:
- a wheel
- a source distribution

Example:
```toml
[build-system]
requires = ["uv_build>=0.9.0,<0.10.0"]
build-backend = "uv_build"
```

Or with another backend:
```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"
```

## `uv_build`

`uv` ships a native backend called `uv_build`.

It is a strong default for most **pure Python** projects.

Use it when:
- your package is pure Python
- you want tight integration with `uv`
- you want good defaults and strong metadata validation

Do **not** use it when:
- you need extension modules / compiled native code
- you need more complex custom build behavior than it supports

For those cases, use an alternative backend such as `hatchling` or the backend appropriate to your packaging stack.

---

## Entry points

If your project defines CLI commands, GUI hooks, or plugin entry points, you need packaging.

### CLI example
```toml
[project.scripts]
my-cli = "my_package.cli:main"
```

Then:
```bash
uv run my-cli
```

### Plugin example
```toml
[project.entry-points.'myapp.plugins']
json = "my_package.plugins.json_plugin"
```

Entry points are part of package metadata. They belong in packaged projects.

---

## Build and publish workflow

### Build
```bash
uv build
```

This produces artifacts in `dist/`.

### Version management
```bash
uv version
uv version 1.0.0
uv version --bump patch
uv version --bump minor
```

### Publish
```bash
uv publish
```

For PyPI:
- use a token
- or use a Trusted Publisher flow in CI

### Important packaging recommendation

When publishing, use:

```bash
uv build --no-sources
```

This checks that your package builds correctly **without** relying on local `tool.uv.sources` tricks that downstream build tools will not understand.

That is a production-quality safeguard.

---

## Build isolation and difficult packages

Some packages are problematic at build time.

`uv` provides mechanisms for:
- augmenting build dependencies
- disabling build isolation for specific packages
- making runtime/build versions consistent for packages like `torch`-dependent extensions

This matters especially for:
- scientific Python
- GPU packages
- extension modules
- projects with fragile build metadata

If you need those features:
- keep the changes narrowly scoped
- document why they exist
- treat them as explicit packaging policy, not shell folklore

---

## Private indexes, authentication, and enterprise concerns

Production teams often need:
- private package indexes
- authenticated registries
- internal certificates
- vendor package mirrors

## Defining indexes

Example:
```toml
[[tool.uv.index]]
name = "internal"
url = "https://packages.example.com/simple"
default = true
```

### What `default = true` means
That index becomes the default low-priority fallback index, replacing the default PyPI role.

Indexes are prioritized in definition order, except the designated default index is always lowest priority.

---

## Authentication

`uv` supports authentication for:
- package indexes
- Git dependencies
- TLS certificate workflows
- third-party services like common artifact registries

In production:

- never hardcode credentials in committed files
- prefer environment variables, CI secret injection, or supported credential flows
- document the auth model in your repo README or platform docs

### Corporate certificates

If your organization uses a corporate trust root or mandatory proxy, certificate configuration matters. That is not optional infrastructure detail; it directly affects reproducible installs.

---

## Resolution controls for difficult dependency graphs

Most teams only need normal locking. Some teams need more.

## Constraints

Constraints **restrict** allowed versions but do not add the package as a dependency.

Use them when:
- a transitive dependency is bad above/below a threshold
- you need to keep the rest of the dependency graph flexible

Example:
```toml
[tool.uv]
constraint-dependencies = ["grpcio<1.65"]
```

## Overrides

Overrides **force** a version even if the graph would normally reject it.

Use them when:
- an upstream bound is incorrect
- you need an emergency temporary escape hatch

Example:
```toml
[tool.uv]
override-dependencies = ["werkzeug==2.3.0"]
```

This is powerful and dangerous. Add comments in the repo whenever you use it.

## Conflicts

Mutually incompatible groups or extras must be declared as conflicts if you want a universal resolution to succeed.

Typical example:
- CPU build dependencies
- CUDA build dependencies

or
- mutually exclusive backend integrations

## Limited environments vs required environments

These solve different problems.

### `environments`
Narrow what `uv` considers while resolving.

Use when:
- the project only targets a subset of platforms

### `required-environments`
Demand that wheel-only packages are available on certain platforms.

Use when:
- your team supports multiple platforms
- you need to fail early if a binary dependency is missing on one of them

This distinction is easy to confuse. Remember:

- `environments` **narrows the solve**
- `required-environments` **expands platform guarantees**

---

## Pre-releases

`uv` intentionally treats pre-releases cautiously and requires user opt-in patterns for correctness.

Production default:
- do not consume pre-releases casually
- if you must, document why and isolate the policy change

---

## Caching, CI, Docker, and deployment patterns

## Caching

`uv` uses aggressive caching for:
- registry downloads
- direct URLs
- Git dependencies
- local builds

This improves speed substantially, but you still need correct cache hygiene.

### Useful commands
```bash
uv cache clean
uv cache clean ruff
uv cache prune
uv cache prune --ci
```

### Important operational detail

`uv`’s cache is designed for concurrent use and uv locks the target environment during installation to avoid concurrent modifications.

That means it is suitable for serious automation, but you should **not** manually mutate its cache directories.

---

## CI pattern

A strong baseline CI flow is:

```bash
uv sync --locked
uv run pytest
uv run ruff check .
uv run mypy .
uv audit
```

### Why `--locked`?
Because CI should fail if:
- `pyproject.toml` changed
- but `uv.lock` was not updated

CI is a verification layer, not a silent repair layer.

### GitHub Actions

`uv` recommends the official `astral-sh/setup-uv` action.

It is best practice to:
- pin the action version
- pin the `uv` version used
- respect the repo’s `.python-version` or `requires-python`

---

## Pre-commit integration

If you use pre-commit, the official `uv-pre-commit` hook can:
- keep `uv.lock` current
- export requirements if necessary
- compile requirement files

This is useful for repositories where lockfile freshness is frequently forgotten.

---

## Docker pattern

Containers are one of the most important production use cases.

### Baseline installation

```dockerfile
WORKDIR /app
COPY . /app
ENV UV_NO_DEV=1
RUN uv sync --locked
```

### Better pattern: split dependency layer from project layer

Use `uv sync --no-install-project` so transitive dependencies live in a separate Docker layer.

Why:
- dependencies change less often than your code
- image rebuilds become much faster

### Bytecode compilation

For startup-sensitive production images:
```dockerfile
RUN uv sync --compile-bytecode
```

This usually improves startup time at the cost of:
- longer build time
- larger image size

That is often a good tradeoff in production containers.

### Cache mount optimization

With Docker cache mounts:
```dockerfile
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv uv sync
```

The `UV_LINK_MODE=copy` setting is useful when the cache and target environment are on different filesystems and linking would otherwise fail.

### `--system` in containers

In containers, the system Python environment can be acceptable because the container is already isolated. But if you use a project-managed repo, using a dedicated virtual environment inside the image is still often cleaner.

---

## Deployment pattern summary

### Good production deploy strategy
- pin Python
- commit `uv.lock`
- build from clean environment
- use `uv sync --locked`
- avoid ad-hoc `uv pip install` in deployment scripts
- separate build-time and runtime concerns

### Bad deploy strategy
- rely on whatever Python is present
- install from unconstrained package names
- run `uv lock` inside production deploy
- mutate environments manually after sync

---

## Tools, scripts, audit, and ecosystem integration

## User-wide tools: `uvx` and `uv tool`

This replaces the old “install random dev tools globally” pattern.

### Run a tool one-off
```bash
uvx ruff
uvx [email protected] check
```

### Install a tool user-wide
```bash
uv tool install ruff
uv tool install black
```

Use this for:
- developer workstation tools
- one-off CLIs
- tools that should not become part of a project dependency graph

Do **not** automatically put every tool in every repo’s `dev` group if it is really just a personal workstation utility.

### Good separation

Put in project dependency groups:
- tools required by CI or repository contribution workflow

Install via `uv tool` / `uvx`:
- personal convenience tools
- globally useful Python CLIs
- tools not required for repo correctness

---

## Audit

Use:
```bash
uv audit
```

This audits project dependencies for:
- known vulnerabilities
- adverse statuses such as deprecation and quarantine

In production repos, this is worth automating.

---

## `uv pip` in migration workflows

The `uv pip` interface is very useful for:
- migrating legacy `requirements.txt` projects
- getting a speed boost without changing repository structure immediately
- lower-level environment work

But for long-term maintainability, move toward:
- `pyproject.toml`
- `uv.lock`
- `uv sync`
- `uv run`

That is the cleaner end state.

---

## Production-grade defaults checklist

Use this section as a practical review list.

## Repository structure
- [ ] `pyproject.toml` exists and is authoritative
- [ ] `.python-version` is committed
- [ ] `uv.lock` is committed
- [ ] `.venv/` is ignored
- [ ] build artifacts are ignored

## Python policy
- [ ] `project.requires-python` is narrow and intentional
- [ ] CI uses the same Python family as local development
- [ ] production runtime Python is not implicit

## Dependency policy
- [ ] runtime dependencies live in `project.dependencies`
- [ ] user-facing optional features live in `project.optional-dependencies`
- [ ] dev/test/lint/docs dependencies live in `dependency-groups`
- [ ] platform-specific needs use markers, not shell hacks
- [ ] path/Git/workspace sources are intentional and documented

## Locking policy
- [ ] developers run `uv sync`
- [ ] CI runs `uv sync --locked`
- [ ] upgrades are intentional via `uv lock --upgrade` or `--upgrade-package`
- [ ] deployments do not re-resolve dependencies ad hoc

## Execution policy
- [ ] docs prefer `uv run ...`
- [ ] CI uses `uv run ...`
- [ ] activation is treated as convenience, not required protocol

## Packaging policy
- [ ] packaged repos define `[build-system]`
- [ ] non-packaged repos do not fake packaging without a reason
- [ ] published packages test `uv build --no-sources`
- [ ] versions are managed explicitly

## Security / platform policy
- [ ] `uv audit` is run periodically or in CI
- [ ] private indexes are configured explicitly
- [ ] secrets are not hardcoded in repo config
- [ ] platform support policy is encoded in `environments`, markers, or `required-environments` where needed

---

## Common mistakes and anti-patterns

## 1. Treating `.venv` as source
Wrong mindset:
- copying it between machines
- committing it
- assuming it is portable

Correct mindset:
- delete and recreate it freely

## 2. Letting CI mutate the lockfile
Wrong:
```bash
uv sync
```

in CI without a lock discipline check.

Better:
```bash
uv sync --locked
```

## 3. Using `uv pip install` inside a managed project for routine dependency changes
This causes drift.

Better:
```bash
uv add ...
uv remove ...
uv lock
uv sync
```

## 4. Using extras for everything
Extras are public optional package features.
Development groups are a better home for:
- test
- lint
- docs
- typing

## 5. Depending on shell activation in every script and doc
That makes docs shell-dependent and stateful.

Better:
```bash
uv run pytest
uv run python -m my_app
```

## 6. Leaving Python version policy vague
“Works on 3.9+ probably” is not a production contract.

## 7. Shipping Git dependencies without documenting why
Git dependencies are operationally expensive.
Use them only when justified.

## 8. Sharing one environment between multiple projects
This defeats isolation and makes `uv sync` dangerous.

## 9. Forgetting build-system implications
If there is no build system:
- your project may not be installed into `.venv`
- entry points may not exist
- package-centric expectations can fail

## 10. Treating overrides as normal dependency policy
They are emergency levers. Keep them visible and temporary whenever possible.

---

# Python virtual environments: the real internal model

Now the lower-level half.

A Python virtual environment is **not** a full independent Python installation cloned from scratch.

The cleanest mental model is:

> A virtual environment is a directory that points Python at a different prefix and different `site-packages`, while still relying on the base interpreter installation for the standard library and related base resources.

This behavior is specified by **PEP 405** and implemented by `venv` and venv-like tools that follow the same `pyvenv.cfg` model.

---

## The minimal conceptual model of a venv

At minimum, a PEP 405-style venv consists of:

- a directory
- a `pyvenv.cfg` file in that directory
- a Python executable in `bin/` (POSIX) or `Scripts/` (Windows)
- a venv-local `site-packages` directory

The key effect is:

- `sys.prefix` and `sys.exec_prefix` point to the venv
- `sys.base_prefix` and `sys.base_exec_prefix` point to the base Python installation

That difference is the standard way to detect a venv:

```python
import sys
in_venv = sys.prefix != sys.base_prefix
```

---

## Startup sequence: what really happens

When Python starts, it builds its module search path and interpreter prefix information.

For PEP 405-style virtual environments, this is driven by `pyvenv.cfg`.

## `pyvenv.cfg`

A venv places a `pyvenv.cfg` file in the environment prefix.

That file acts as:

- the marker that this is a venv
- configuration input for startup and site initialization

Important fields include:

### `home`
Points at the base Python installation used to create the environment.

### `include-system-site-packages`
Controls whether the system site-packages should also be visible.

Typical values:
- `false` → isolated venv
- `true` → system packages are also added after venv packages

---

## Prefix behavior

Inside a venv:

- `sys.prefix` → venv prefix
- `sys.exec_prefix` → venv exec prefix
- `sys.base_prefix` → base install prefix
- `sys.base_exec_prefix` → base install exec prefix

This split is fundamental.

### Why it matters

The standard library and low-level install metadata are found relative to the **base** prefixes, while venv-local `site-packages` are found relative to the **venv** prefixes.

PEP 405 explicitly changed `site` and `sysconfig` behavior to support exactly this model.

---

## Python 3.14 startup nuance

In Python 3.14, `sys.prefix` and `sys.exec_prefix` are set from `pyvenv.cfg` during **path initialization**, rather than later through `site`.

That means older assumptions involving `-S` can differ from newer behavior.

If you are debugging very low-level interpreter startup behavior across Python versions, this detail matters.

---

## Isolation from system packages

By default, venvs are isolated from system site-packages.

If `include-system-site-packages = true`, Python’s `site` module adds system site directories **after** the venv site directories.

That ordering matters:

- system packages become importable
- but packages installed in the venv take precedence over same-named system packages

Also note:
- user site-packages are treated as part of system site-packages for this purpose

So a default isolated venv excludes both:
- system site-packages
- user site-packages

unless configured otherwise.

---

## The standard library is not duplicated in the normal sense

A common misconception is that a venv copies “all of Python”.

It does not.

A normal venv:
- has its own interpreter entry point
- has its own local `site-packages`
- still relies on the base Python installation for the standard library and related base files

That is why venvs are lightweight compared to fully self-contained language runtimes.

---

## What activation really does

Activation is a **shell convenience**.

It is not the core mechanism that makes a venv work.

### What activation actually changes

Typically activation:

- prepends the venv’s `bin/` or `Scripts/` directory to `PATH`
- adjusts your shell prompt
- may set `VIRTUAL_ENV`

### What activation does **not** do

It does not:
- “turn on” isolation at the Python interpreter level
- modify `pyvenv.cfg`
- change package metadata
- make the venv fundamentally usable in a new way

You can use a venv perfectly well without activating it by running:
- the interpreter directly
- scripts installed inside it
- a launcher like `uv run` that targets it

This is why production docs should not overemphasize activation.

---

## `VIRTUAL_ENV` is not a reliable detector

When a venv is activated, the shell usually sets `VIRTUAL_ENV`.

But Python’s docs are explicit: because activation is not required to use a venv, `VIRTUAL_ENV` is **not reliable** for detecting whether Python is running in a virtual environment.

Use:
```python
sys.prefix != sys.base_prefix
```

instead.

---

## Shebangs and why scripts still work without activation

Scripts installed into a venv are expected to work without requiring activation.

Why?

Because they carry a shebang line pointing to the venv interpreter.

On POSIX that conceptually looks like:

```text
#!/path/to/venv/bin/python
```

So even if your shell `PATH` is not activated, executing the script uses the correct interpreter.

On Windows, shebang processing is supported when the appropriate Python launcher/manager support is installed, and installed scripts are expected to run correctly without activation too.

This is the key reason activation is convenience rather than necessity.

---

## Why venvs are inherently non-portable

This point is critical and often misunderstood.

Because installed scripts use **absolute interpreter paths** in their shebangs, virtual environments are inherently non-portable in the general case.

That means:

- do not move a venv
- do not rename its parent directory and assume it will keep working
- do not copy it between machines and expect correctness

The official guidance is simple:

> recreate the environment at the target location

This is exactly why production workflows should rely on:
- declarative dependency metadata
- a lockfile
- reproducible environment creation

not on environment copying.

---

## Cross-platform virtualenv layout and behavior

## POSIX layout

Typical layout:

```text
.venv/
├── bin/
│   ├── python
│   ├── pip
│   ├── activate
│   ├── activate.fish
│   ├── activate.csh
│   └── Activate.ps1
├── lib/
│   └── pythonX.Y/
│       └── site-packages/
└── pyvenv.cfg
```

### Notable points
- executables live in `bin/`
- `site-packages` lives under `lib/pythonX.Y/site-packages`
- multiple activation scripts may exist for different shells
- PowerShell Core activation script also exists on POSIX in modern Python

---

## Windows layout

Typical layout:

```text
.venv\
├── Scripts\
│   ├── python.exe
│   ├── pip.exe
│   ├── activate.bat
│   └── Activate.ps1
├── Lib\
│   └── site-packages\
└── pyvenv.cfg
```

### Notable points
- executables live in `Scripts\`
- `site-packages` is `Lib\site-packages`
- activation differs between `cmd.exe` and PowerShell
- PowerShell script execution policy can matter

---

## Activation commands by platform / shell

### POSIX
#### bash / zsh
```bash
source .venv/bin/activate
```

#### fish
```bash
source .venv/bin/activate.fish
```

#### csh / tcsh
```csh
source .venv/bin/activate.csh
```

#### PowerShell Core on POSIX
```powershell
.venv/bin/Activate.ps1
```

### Windows
#### cmd.exe
```cmd
.venv\Scripts\activate.bat
```

#### PowerShell
```powershell
.venv\Scripts\Activate.ps1
```

---

## Windows-specific caveats

## PowerShell execution policy

On Windows, `Activate.ps1` may require enabling script execution for the user, commonly with a policy like `RemoteSigned`.

This is a shell policy issue, not a venv correctness issue.

## Symlinks on Windows

Although symlinks are supported, Python’s docs do **not** recommend them on Windows.

A major gotcha:
- double-clicking `python.exe` in File Explorer may resolve the symlink eagerly and ignore the virtual environment

If you are doing Windows-focused tooling or distribution work, this subtlety matters.

---

## Copies vs symlinks

The `venv` module supports both:
- `--symlinks`
- `--copies`

Platform defaults vary.

Conceptually:
- symlinks are lighter
- copies can avoid certain platform issues
- either way, the venv still relies on the base installation model specified by PEP 405

Do not confuse “copies of the interpreter executable” with “fully self-contained Python installation”.

---

## Advanced virtualenv internals

## `site` processing

After path initialization, Python processes the `site` module unless disabled.

This is where:
- `site-packages` directories are added
- virtualenv `include-system-site-packages` policy is applied
- `.pth` files are processed
- `sitecustomize` / `usercustomize` hooks can be imported

This means a lot of “weird import path behavior” is actually `site` behavior.

---

## `.pth` files

A `.pth` file in a relevant site-packages directory can:

- add paths to `sys.path`
- and, if a line starts with `import`, execute code at interpreter startup

This is powerful and dangerous.

### Important implications

- `.pth` files are executed at every startup
- startup can change even if your application code did not
- third-party tooling can insert import hooks this way
- debugging import surprises often requires inspecting `.pth` files

Production implication:
- treat unexpected `.pth` files as real startup configuration, not harmless metadata

---

## `sitecustomize` and `usercustomize`

These are optional modules that can further modify interpreter behavior when `site` runs.

If you see mysterious import path changes or environment-specific startup behavior, check whether these modules exist.

---

## `PYTHONHOME`

`PYTHONHOME` overrides `pyvenv.cfg` detection.

This is a very important debugging detail.

If someone sets `PYTHONHOME`, the interpreter may not behave like the venv you expected.

Production recommendation:
- avoid setting `PYTHONHOME` unless you very specifically know why
- when debugging “venv ignored” behavior, inspect this variable first

---

## `._pth` files

On Windows especially, `._pth` files can completely override normal `sys.path` initialization.

This is an advanced mechanism that can put Python into a much more isolated path configuration mode.

If present, a `._pth` file can radically change import behavior.

This is uncommon in normal app development, but it matters in:
- embedded Python
- packaged Windows distributions
- unusual launcher setups

---

## Non-standard environment implementations

Python’s documentation is specifically describing venv-like environments built around the `pyvenv.cfg` model.

Some tools may implement “virtual environment” behavior differently.

Most mainstream tools follow the same general model, but if a tool diverges from PEP 405 behavior, low-level assumptions may break.

---

## How `uv` interacts with virtual environments

`uv` is not itself dependent on Python, but it knows how to locate and operate on Python environments.

## Project-managed environments

In a `uv` project, the default environment is `.venv`.

Project commands operate against that managed environment automatically.

## `uv pip` environment discovery order

When mutating an environment, `uv` searches in this order:

1. active venv from `VIRTUAL_ENV`
2. active Conda environment from `CONDA_PREFIX`
3. `.venv` in the current directory or nearest parent directory

If no virtual environment is found, `uv` prompts to create one.

This is one of the best safety features in `uv`:
- it defaults toward isolation
- it avoids silently mutating system Python the way `pip` often can

---

## Why `uv` is safer than default `pip` behavior

By default:

- `uv pip install` targets an active venv or discovered `.venv`
- `pip install` can target a global/system environment if no venv is active

That difference matters a lot operationally.

It prevents accidental system-environment mutation.

To install into system Python with `uv`, you must opt in with:
- `--system`
- or `--python /path/to/python`

That explicitness is a feature.

---

## `uv sync` and environment convergence

In a project, `uv sync` is more than “install some packages”.

It converges the environment toward the lockfile.

By default it does exact sync:
- install what belongs
- remove what does not belong

That is exactly the kind of behavior you want from an environment manager in production-grade workflows.

---

## Debugging and introspection snippets

Use these snippets to inspect what is really happening.

## 1. Am I in a venv?

```python
import sys

print("sys.executable      =", sys.executable)
print("sys.prefix          =", sys.prefix)
print("sys.base_prefix     =", sys.base_prefix)
print("sys.exec_prefix     =", sys.exec_prefix)
print("sys.base_exec_prefix=", sys.base_exec_prefix)
print("in_venv             =", sys.prefix != sys.base_prefix)
```

---

## 2. What paths am I importing from?

```python
import sys

for i, p in enumerate(sys.path):
    print(f"{i:02d}: {p}")
```

Use this when:
- imports differ between machines
- a package seems to come from the wrong place
- `.pth` files may be involved

---

## 3. What does the venv config say?

```python
from pathlib import Path
import sys

cfg = Path(sys.prefix) / "pyvenv.cfg"
print(cfg)
print(cfg.read_text())
```

Use this to inspect:
- base home
- include-system-site-packages
- other venv metadata

---

## 4. What site-packages are active?

```python
import site

print("site.getsitepackages():")
for p in site.getsitepackages():
    print("  ", p)

print("\nsite.getusersitepackages():")
print("  ", site.getusersitepackages())
```

Note:
- behavior can vary by interpreter and platform
- user site visibility depends on isolation settings

---

## 5. What interpreter is a script actually using?

On POSIX:
```bash
head -n 1 .venv/bin/my-script
```

This shows the shebang, which is often the root cause of portability surprises.

---

## 6. Where is `uv` installing with the pip interface?

```bash
uv pip list
python -c "import sys; print(sys.executable)"
```

If you are unsure which environment `uv` selected, inspect both the environment and `uv`’s discovery context.

---

## Short revision summary

If you only want the highest-signal recap, memorize this.

## `uv` side
- `pyproject.toml` declares policy
- `uv.lock` records exact resolution
- `.venv` is disposable
- `.python-version` pins the working interpreter
- `uv add` / `uv remove` change dependency declarations
- `uv lock` updates exact versions
- `uv sync` converges environment to the lockfile
- `uv run` is the safest default way to execute project commands
- `uv sync --locked` belongs in CI
- `dependency-groups` are for dev/test/lint/docs
- `optional-dependencies` are extras
- workspaces are the right monorepo model
- packaging is explicit via `[build-system]`

## virtualenv side
- venvs are based on `pyvenv.cfg`
- `sys.prefix` points at the venv
- `sys.base_prefix` points at the base install
- activation is convenience, not core mechanism
- scripts work without activation because of shebangs / launchers
- venvs are inherently non-portable
- `site` and `.pth` files can change import behavior significantly
- `PYTHONHOME` can override venv detection
- `uv` is safer than raw `pip` because it defaults to venv use

---

## Official references

### `uv` documentation
- `uv` home: <https://docs.astral.sh/uv/>
- Working on projects: <https://docs.astral.sh/uv/guides/projects/>
- Creating projects: <https://docs.astral.sh/uv/concepts/projects/init/>
- Structure and files: <https://docs.astral.sh/uv/concepts/projects/layout/>
- Managing dependencies: <https://docs.astral.sh/uv/concepts/projects/dependencies/>
- Running commands: <https://docs.astral.sh/uv/concepts/projects/run/>
- Locking and syncing: <https://docs.astral.sh/uv/concepts/projects/sync/>
- Configuring projects: <https://docs.astral.sh/uv/concepts/projects/config/>
- Using workspaces: <https://docs.astral.sh/uv/concepts/projects/workspaces/>
- Exporting a lockfile: <https://docs.astral.sh/uv/concepts/projects/export/>
- Building distributions: <https://docs.astral.sh/uv/concepts/projects/build/>
- Python versions: <https://docs.astral.sh/uv/concepts/python-versions/>
- Configuration files: <https://docs.astral.sh/uv/concepts/configuration-files/>
- Package indexes: <https://docs.astral.sh/uv/concepts/indexes/>
- Resolution: <https://docs.astral.sh/uv/concepts/resolution/>
- Build backend: <https://docs.astral.sh/uv/concepts/build-backend/>
- Authentication: <https://docs.astral.sh/uv/concepts/authentication/>
- TLS certificates: <https://docs.astral.sh/uv/concepts/authentication/certificates/>
- Caching: <https://docs.astral.sh/uv/concepts/cache/>
- The pip interface: <https://docs.astral.sh/uv/pip/>
- Using environments: <https://docs.astral.sh/uv/pip/environments/>
- Compatibility with pip: <https://docs.astral.sh/uv/pip/compatibility/>
- Using tools: <https://docs.astral.sh/uv/guides/tools/>
- Running scripts: <https://docs.astral.sh/uv/guides/scripts/>
- Building and publishing a package: <https://docs.astral.sh/uv/guides/package/>
- Using uv in GitHub Actions: <https://docs.astral.sh/uv/guides/integration/github/>
- Using uv in Docker: <https://docs.astral.sh/uv/guides/integration/docker/>
- Using uv in pre-commit: <https://docs.astral.sh/uv/guides/integration/pre-commit/>
- CLI reference: <https://docs.astral.sh/uv/reference/cli/>
- Settings reference: <https://docs.astral.sh/uv/reference/settings/>

### Python / PEP references
- `venv` module docs: <https://docs.python.org/3/library/venv.html>
- `site` module docs: <https://docs.python.org/3/library/site.html>
- `sys.path` initialization: <https://docs.python.org/3/library/sys_path_init.html>
- `sys` module docs: <https://docs.python.org/3/library/sys.html>
- PEP 405 — Python Virtual Environments: <https://peps.python.org/pep-0405/>
- PEP 735 — Dependency Groups in `pyproject.toml`: <https://peps.python.org/pep-0735/>

---

## Final note

For a production Python repository, the safest high-level pattern is:

1. declare metadata and dependency policy in `pyproject.toml`
2. pin Python intentionally
3. commit `uv.lock`
4. use `.venv` as a disposable artifact
5. run everything through `uv run`
6. verify lock freshness with `uv sync --locked` in CI
7. treat environment recreation as normal, not exceptional
