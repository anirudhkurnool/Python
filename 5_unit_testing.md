# Pytest and Production-Grade Python Testing: Complete Revision Guide

This guide is a **single-file revision handbook** for **pytest** and for **testing production-grade Python systems**. It is designed to help you revise the practical, high-signal concepts that matter when writing tests for real codebases: correctness, maintainability, speed, determinism, isolation, observability, and CI confidence.

It is intentionally biased toward:

- modern `pytest`-first Python codebases
- application and library code that runs in CI/CD
- production-safe defaults
- examples you can adapt directly
- avoiding flaky, misleading, and over-mocked tests

**Target baseline:** modern Python 3.x and the current stable documentation stream as verified on **March 28, 2026**, primarily against official docs for `pytest`, `unittest.mock`, `coverage.py`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist`, and Hypothesis.

---

## Table of contents

1. [What production-grade testing means](#1-what-production-grade-testing-means)
2. [Testing strategy: what kinds of tests you need](#2-testing-strategy-what-kinds-of-tests-you-need)
3. [Recommended project layout and configuration](#3-recommended-project-layout-and-configuration)
4. [Core pytest mental model](#4-core-pytest-mental-model)
5. [Daily pytest command-line workflow](#5-daily-pytest-command-line-workflow)
6. [Assertions, exceptions, warnings, logs, and output](#6-assertions-exceptions-warnings-logs-and-output)
7. [Fixtures: the most important pytest concept](#7-fixtures-the-most-important-pytest-concept)
8. [Parametrization](#8-parametrization)
9. [Markers, skip, and xfail](#9-markers-skip-and-xfail)
10. [Mocking, monkeypatching, and test doubles](#10-mocking-monkeypatching-and-test-doubles)
11. [Testing real-world boundaries](#11-testing-real-world-boundaries)
12. [Async testing with pytest-asyncio](#12-async-testing-with-pytest-asyncio)
13. [Coverage: how to measure it and how not to misuse it](#13-coverage-how-to-measure-it-and-how-not-to-misuse-it)
14. [Scaling test suites in real projects](#14-scaling-test-suites-in-real-projects)
15. [CI and release-confidence workflows](#15-ci-and-release-confidence-workflows)
16. [Common anti-patterns and production testing mistakes](#16-common-anti-patterns-and-production-testing-mistakes)
17. [Troubleshooting checklist](#17-troubleshooting-checklist)
18. [Fast revision checklist](#18-fast-revision-checklist)
19. [Official references](#19-official-references)

---

## 1. What production-grade testing means

Production-grade testing is not just "having tests." It means your tests help you make changes safely in a real codebase with real users, real dependencies, real failures, and real CI pipelines.

### A production-grade test suite should be:

- **Correct**: tests actually detect regressions.
- **Deterministic**: the same code and inputs produce the same results.
- **Isolated**: tests do not depend on global process state, network randomness, clock drift, or execution order.
- **Fast enough**: developers run it often.
- **Readable**: failures explain what broke.
- **Maintainable**: small refactors should not require rewriting half the suite.
- **Layered**: different test types cover different risks.
- **CI-friendly**: clean exit codes, reproducible setup, stable execution.
- **Honest**: coverage percentages and passing tests should reflect real confidence, not theater.

### Core rule

Test **behavior and contracts**, not incidental implementation details.

### What good tests usually assert

- return values
- raised exceptions
- state changes
- database writes
- published messages
- outbound calls at a meaningful seam
- logs or warnings when they are part of behavior

### What good tests usually avoid asserting

- local variable values
- exact internal call chains unless the call itself is the contract
- private helper structure unless there is no better seam
- sleep-based timing assumptions
- test order dependencies

---

## 2. Testing strategy: what kinds of tests you need

You usually need multiple layers of tests, not one magic kind.

## 2.1 Unit tests

Unit tests validate small pieces of logic in strong isolation.

Good for:

- pure functions
- validation rules
- parsing and formatting
- branching logic
- orchestration logic around a mocked or faked dependency

Characteristics:

- fastest
- most numerous
- should run on every change
- should rarely touch real I/O

## 2.2 Integration tests

Integration tests validate that your code works with real collaborators or realistic substitutes.

Good for:

- ORM queries
- repositories and transactions
- HTTP clients against test servers or sandbox APIs
- queue publishing and consumption
- file handling
- framework wiring

Characteristics:

- slower than unit tests
- higher confidence at system boundaries
- should still be deterministic and automatable

## 2.3 End-to-end tests

End-to-end tests validate real user workflows through the full system.

Good for:

- top business-critical paths
- auth flow
- checkout or payment path
- deployment smoke tests

Characteristics:

- slowest
- most brittle
- highest environment sensitivity
- should be fewer and more carefully chosen

## 2.4 Contract tests

Contract tests validate assumptions at boundaries between systems.

Good for:

- API request and response schemas
- event payloads
- consumer/provider compatibility
- serialization guarantees

These are especially valuable when multiple services evolve independently.

## 2.5 A practical production testing shape

Do not get dogmatic about the "test pyramid," but the following is a strong default:

- many fast deterministic unit tests
- a smaller set of targeted integration tests for risky boundaries
- a thin set of end-to-end or smoke tests for business-critical paths

### CI gating rule of thumb

- On every PR: run fast unit tests plus a focused integration subset.
- On merge to main: run the broader suite.
- On nightly or scheduled jobs: run the heaviest environment-dependent tests.

### Independence rules

Every test should ideally be able to run:

- alone
- in any order
- repeatedly
- in parallel

If that is not true, the suite will eventually become flaky in CI.

---

## 3. Recommended project layout and configuration

## 3.1 Recommended layout

For modern projects, a `src/` layout plus a separate `tests/` directory is a strong default.

```text
project/
├── pyproject.toml
├── src/
│   └── mypkg/
│       ├── __init__.py
│       ├── service.py
│       ├── repository.py
│       └── api.py
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_service.py
    │   └── test_utils.py
    ├── integration/
    │   ├── test_repository.py
    │   └── test_http_client.py
    ├── e2e/
    │   └── test_checkout_flow.py
    └── factories/
        └── builders.py
```

### Why this layout is strong

- app code is clearly separate from test code
- imports are less surprising
- integration and end-to-end suites can be selected cleanly
- shared fixtures live in predictable places

## 3.2 Where things should live

- `tests/conftest.py`: shared fixtures for a directory tree
- `tests/unit/`: unit tests only
- `tests/integration/`: real boundary tests
- `tests/e2e/`: sparse workflow tests
- `tests/factories/` or `tests/builders/`: data builders, factories, test helpers

### Guideline

Put a fixture in the **narrowest scope of reuse**.

- If only one module uses it, keep it in that module.
- If a whole directory uses it, move it to that directory's `conftest.py`.
- Avoid one giant global `conftest.py` with unrelated fixtures.

## 3.3 Canonical `pyproject.toml` for pytest

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
  "-ra",
  "--strict-config",
  "--strict-markers",
  "--import-mode=importlib",
]
xfail_strict = true
markers = [
  "integration: tests that exercise real infrastructure boundaries",
  "slow: tests that are slower than normal unit tests",
  "smoke: a small deployment-confidence subset",
  "e2e: end-to-end workflow tests",
]
filterwarnings = [
  "error",
]
```

### Why these options are good defaults

- `-ra`: show a useful test summary for skipped, xfailed, and other outcomes
- `--strict-config`: fail on config mistakes
- `--strict-markers`: fail on unregistered custom markers
- `--import-mode=importlib`: recommended by pytest docs for new projects using modern layouts
- `xfail_strict = true`: unexpected passes should fail the build
- `filterwarnings = ["error"]`: unexpected warnings become visible instead of silently accumulating

### Practical warning policy

Treat warnings as errors by default, then add narrow exceptions for known third-party noise if absolutely necessary.

## 3.4 Canonical coverage config

```toml
[tool.coverage.run]
branch = true
source = ["src/mypkg"]

[tool.coverage.report]
show_missing = true
skip_covered = true
fail_under = 90
exclude_also = [
  "if TYPE_CHECKING:",
  "if __name__ == .__main__.:",
]

[tool.coverage.html]
show_contexts = true
```

### Important notes

- Branch coverage is usually more informative than line coverage alone.
- A threshold like `90` is a policy decision, not a law.
- `fail_under = 100` is often a vanity metric unless your codebase is small and disciplined.
- `coverage.py` can also measure tests; some teams gate only application packages, while others measure both for visibility.

## 3.5 Async config when your project is asyncio-only

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Use `auto` when your suite uses asyncio as its only async model. If your codebase mixes async ecosystems, `strict` is safer.

---

## 4. Core pytest mental model

Pytest is powerful because it keeps the core test syntax simple:

- write normal Python functions
- use plain `assert`
- request fixtures by name
- add parametrization and markers only when needed

## 4.1 Test discovery basics

By default, pytest discovers:

- files named `test_*.py` or `*_test.py`
- functions named `test_*`
- methods named `test_*` inside classes named `Test*`

### Important class rule

Pytest test classes should **not** define `__init__`.

## 4.2 A canonical pure unit test

```python
def add(a: int, b: int) -> int:
    return a + b


def test_add_returns_sum() -> None:
    assert add(2, 3) == 5
```

## 4.3 Why plain `assert` is preferred

Pytest rewrites assertions so failures are informative:

```python
def test_total():
    assert 2 + 2 == 5
```

You get rich introspection instead of only `AssertionError`.

## 4.4 Arrange, act, assert

A strong default structure is:

1. arrange inputs and collaborators
2. act by calling the behavior under test
3. assert outcomes

Example:

```python
def test_discount_applied_for_premium_user():
    user = User(is_premium=True)

    total = calculate_total(user=user, subtotal=100)

    assert total == 90
```

## 4.5 Test naming

Prefer names that describe business behavior:

- `test_returns_404_for_unknown_order`
- `test_retries_once_on_transient_timeout`
- `test_does_not_publish_event_when_validation_fails`

Avoid vague names:

- `test_1`
- `test_happy_path`
- `test_service`

## 4.6 Good test design defaults

- one test should check one behavior, not one line
- multiple related assertions are fine if they describe one outcome
- prefer smaller focused tests over giant "everything" tests
- use helper functions or fixtures to remove setup noise, not to hide the behavior being tested

---

## 5. Daily pytest command-line workflow

These commands matter a lot in real teams.

## 5.1 Basic runs

```bash
pytest
pytest tests/unit
pytest tests/unit/test_service.py
pytest tests/unit/test_service.py::test_retries_once_on_timeout
```

## 5.2 Select tests by name or marker

```bash
pytest -k "retry and not slow"
pytest -m "integration"
pytest -m "not slow and not e2e"
pytest --markers
```

### `-k` vs `-m`

- `-k` filters by substring expression over names and keywords
- `-m` filters by registered markers

Use markers for stable suites like `integration`, `slow`, or `smoke`.

## 5.3 Rerun what matters

```bash
pytest --lf
pytest --ff
pytest --cache-show
pytest --cache-clear
```

### Meaning

- `--lf` / `--last-failed`: rerun only last failures
- `--ff` / `--failed-first`: run all tests, but previous failures first
- `--cache-clear`: useful in CI or when cache state is suspicious

## 5.4 Stop early when debugging

```bash
pytest -x
pytest --maxfail=1
pytest --stepwise
```

## 5.5 Useful output and debugging flags

```bash
pytest -q
pytest -vv
pytest -s
pytest --tb=short
pytest --showlocals
pytest --pdb
pytest --trace
pytest --collect-only
pytest --fixtures
pytest --fixtures-per-test
pytest --setup-plan
pytest --durations=10
```

### What they are for

- `-q`: quieter output
- `-vv`: more detail
- `-s`: disable capture
- `--tb=short`: shorter tracebacks
- `--showlocals`: show locals in tracebacks
- `--pdb`: drop into debugger on failure
- `--trace`: break at test start
- `--collect-only`: inspect collection
- `--fixtures`: list fixtures
- `--setup-plan`: preview fixture setup and teardown plan
- `--durations=10`: show the slowest tests

### Production tip

If CI says "test not found" or "marker not applied," `pytest --collect-only` is often the fastest truth source.

## 5.6 Good local development loop

A realistic local loop is:

1. run the narrowest test you can
2. use `--lf` while debugging
3. run the relevant marker subset
4. run the full fast suite before pushing

---

## 6. Assertions, exceptions, warnings, logs, and output

## 6.1 Assertion style

Prefer direct, specific assertions:

```python
def test_slugify_normalizes_case():
    assert slugify("Hello World") == "hello-world"
```

Avoid weak assertions:

```python
def test_slugify():
    assert slugify("Hello World")
```

The weak assertion only checks truthiness, not correctness.

## 6.2 Comparing floating-point values with `pytest.approx`

Floating-point equality is often unsafe with plain `==`.

```python
import pytest


def test_total_with_tax():
    assert calculate_total(0.1, 0.2) == pytest.approx(0.3)
```

Use `pytest.approx` when the value is expected to be numerically close rather than bit-for-bit identical.

## 6.3 Asserting exceptions with `pytest.raises`

```python
import pytest


def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b


def test_divide_rejects_zero_divisor() -> None:
    with pytest.raises(ValueError, match="must not be zero"):
        divide(10, 0)
```

### Best practice

- assert the exception type
- use `match=` for meaningful error text when the message is part of the contract

## 6.4 Asserting warnings with `pytest.warns`

```python
import pytest


def old_api() -> None:
    import warnings
    warnings.warn("use new_api instead", DeprecationWarning)


def test_old_api_emits_deprecation_warning() -> None:
    with pytest.warns(DeprecationWarning, match="use new_api instead"):
        old_api()
```

Use `pytest.deprecated_call()` when the intent is specifically deprecation behavior.

## 6.5 Capturing stdout and stderr with `capsys`

```python
def greet() -> None:
    print("hello")


def test_greet_prints_hello(capsys) -> None:
    greet()
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == ""
```

Use `capfd` when file-descriptor-level capture matters, such as subprocess output.

## 6.6 Asserting logs with `caplog`

```python
import logging


logger = logging.getLogger(__name__)


def save_user() -> None:
    logger.warning("user record missing optional email")


def test_save_user_logs_warning(caplog) -> None:
    caplog.set_level(logging.WARNING)

    save_user()

    assert "missing optional email" in caplog.text
```

### When log assertions are justified

- audit or compliance behavior
- operational observability behavior
- warnings that should be emitted for bad inputs or degraded mode

Do not assert logs for every function just because logs exist.

## 6.7 Warning policy in production suites

Unexpected warnings should not quietly pile up.

Strong default:

- `filterwarnings = ["error"]` in config
- add targeted ignores for known external noise
- assert warnings explicitly where behavior matters

---

## 7. Fixtures: the most important pytest concept

Fixtures are one of the main reasons pytest scales better than hand-written setup code.

They provide:

- reusable setup
- explicit dependency injection
- scoped lifecycle management
- reliable teardown

## 7.1 Basic fixture example

```python
import pytest


@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Ada"}


def test_user_name(sample_user):
    assert sample_user["name"] == "Ada"
```

Pytest injects fixtures by name.

## 7.2 Fixtures can depend on fixtures

```python
import pytest


@pytest.fixture
def db_url():
    return "sqlite://"


@pytest.fixture
def repository(db_url):
    return UserRepository(db_url=db_url)
```

This explicit dependency graph is one of pytest's biggest strengths.

## 7.3 Fixture scopes

Common scopes:

- `function`
- `class`
- `module`
- `package`
- `session`

### Rule of thumb

Use the **smallest scope** that keeps the suite fast enough.

- `function`: safest default
- `session`: powerful, but easiest way to accidentally leak state

## 7.4 Teardown with `yield`

This is the canonical modern pattern:

```python
import os
import pytest


@pytest.fixture
def temp_workdir(tmp_path):
    original = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original)
```

Everything after `yield` is teardown.

### Why `yield` fixtures are preferred

- setup and teardown stay together
- ordering is easier to reason about
- safer than scattered cleanup code

## 7.5 Using `request`

The `request` fixture is useful for advanced cases:

- accessing `request.param` in parametrized fixtures
- reading node or config metadata
- registering finalizers when `yield` is not practical

Example:

```python
import pytest


@pytest.fixture
def config_value(request):
    return request.config.getoption("--my-flag")
```

Use `request` when needed, but do not build magical fixtures that hide too much.

## 7.6 Factory fixtures

Factory fixtures are great when tests need multiple objects with small variations.

```python
import pytest


@pytest.fixture
def make_user():
    def _make_user(**overrides):
        user = {
            "name": "Ada",
            "is_admin": False,
        }
        user.update(overrides)
        return user
    return _make_user


def test_admin_flag(make_user):
    user = make_user(is_admin=True)
    assert user["is_admin"] is True
```

This is often better than huge static fixtures.

## 7.7 Autouse fixtures

Autouse fixtures run without being explicitly requested.

```python
import pytest


@pytest.fixture(autouse=True)
def default_app_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
```

### Use autouse carefully

Good uses:

- preventing real network globally
- resetting global singleton state
- setting consistent environment defaults

Bad uses:

- hidden business setup that tests do not visibly declare
- broad fixtures that make test behavior hard to trace

## 7.8 `conftest.py`

Use `conftest.py` for shared fixtures, hooks, and local test support code.

### Good pattern

- keep fixtures close to where they are used
- one directory tree, one focused `conftest.py`

### Bad pattern

- one giant root `conftest.py` that every test in the repo implicitly depends on

## 7.9 Built-in fixtures you should know

### `tmp_path`

- per-test temporary directory
- returns `pathlib.Path`
- ideal for filesystem tests

### `tmp_path_factory`

- session-scoped temp directory factory
- useful for expensive assets created once per session

### `monkeypatch`

- patch attributes
- patch environment variables
- patch mappings
- patch `sys.path`
- automatically undo changes after the test

### `caplog`

- inspect logs

### `capsys` and `capfd`

- inspect output

### `cache`

- store and retrieve values across runs
- useful in advanced scenarios, but avoid depending on cache for correctness

## 7.10 Example: fixture with teardown

```python
import pytest


class FakeConnection:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def connection():
    conn = FakeConnection()
    yield conn
    conn.close()


def test_connection_is_open_during_test(connection):
    assert connection.closed is False
```

## 7.11 Fixture mistakes to avoid

- returning mutable shared state from broad scopes without resetting it
- using session fixtures for data that tests mutate
- hiding essential business setup in autouse fixtures
- creating fixtures that perform too many unrelated responsibilities
- reading from the real environment when a fixture should supply the value

---

## 8. Parametrization

Parametrization lets you run the same test logic over many cases.

## 8.1 Basic parametrization

```python
import pytest


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Hello World", "hello-world"),
        (" already trimmed ", "already-trimmed"),
        ("API_v2", "api-v2"),
    ],
)
def test_slugify(raw, expected):
    assert slugify(raw) == expected
```

## 8.2 Add readable IDs

Readable IDs make failure output much better:

```python
import pytest


@pytest.mark.parametrize(
    "subtotal,is_premium,expected",
    [
        pytest.param(100, False, 100, id="regular-user"),
        pytest.param(100, True, 90, id="premium-user"),
    ],
)
def test_calculate_total(subtotal, is_premium, expected):
    assert calculate_total(subtotal, is_premium) == expected
```

## 8.3 Mark individual cases

```python
import pytest


@pytest.mark.parametrize(
    "value",
    [
        1,
        2,
        pytest.param(3, marks=pytest.mark.xfail(reason="known bug")),
    ],
)
def test_example(value):
    assert transform(value) > 0
```

## 8.4 Parametrized fixtures

```python
import pytest


@pytest.fixture(params=["sqlite", "postgres"])
def backend(request):
    return request.param


def test_repository_round_trip(backend):
    assert save_and_load(backend=backend) == "ok"
```

Use this when the **setup** varies by parameter, not just the final assertion inputs.

## 8.5 Indirect parametrization

Indirect parametrization is useful when fixture setup should happen at runtime instead of collection time.

```python
import pytest


@pytest.fixture
def user(request):
    return {"role": request.param}


@pytest.mark.parametrize("user", ["reader", "admin"], indirect=True)
def test_permissions(user):
    assert "role" in user
```

## 8.6 Stacked parametrization

```python
import pytest


@pytest.mark.parametrize("currency", ["USD", "EUR"])
@pytest.mark.parametrize("country", ["US", "DE"])
def test_tax_rules(country, currency):
    ...
```

This creates the Cartesian product.

### Warning

Parametrization grows fast. A few stacked decorators can explode the suite size.

## 8.7 When parametrization becomes unreadable

Stop and refactor if:

- the argument list is too wide
- each row needs comments to explain itself
- setup logic differs heavily between cases
- one test hides many unrelated behaviors

Possible replacements:

- separate tests
- factory fixtures
- dedicated helper functions
- small targeted parametrized groups

## 8.8 Advanced hook: `pytest_generate_tests`

This hook can drive custom parametrization schemes, usually from CLI flags or generated data.

Use it sparingly.

Good use:

- optional broad test matrices behind a flag

Bad use:

- hiding core test data generation in meta-programming

---

## 9. Markers, skip, and xfail

Markers attach metadata to tests and are often used for selection and control.

## 9.1 Built-in markers you should know

- `parametrize`
- `skip`
- `skipif`
- `xfail`
- `usefixtures`
- `filterwarnings`

## 9.2 Custom markers

Define custom markers in config and use them consistently:

- `integration`
- `slow`
- `smoke`
- `e2e`

Then select with:

```bash
pytest -m "integration and not slow"
```

## 9.3 `skip`

Use `skip` when the test **cannot or should not run** in the current environment.

Examples:

- optional dependency missing
- OS-specific behavior
- required service unavailable in a known environment

Useful helper:

```python
import pytest


numpy = pytest.importorskip("numpy")
```

## 9.4 `xfail`

Use `xfail` when the test **documents a known bug or missing behavior**.

```python
import pytest


@pytest.mark.xfail(reason="bug #1234", strict=True)
def test_legacy_rounding_behavior():
    assert round_total(2.675) == 2.68
```

### Key rule

An `xfail` is **not** a substitute for fixing the problem.

### Why `strict=True` matters

If the test unexpectedly passes, the suite should tell you. Otherwise old `xfail`s silently rot forever.

## 9.5 `xfail(run=False)`

Useful when a test currently crashes the interpreter or is too dangerous to execute, but you still want the expected-failure bookkeeping.

## 9.6 Skip vs xfail vs fail

- `skip`: not applicable now
- `xfail`: known broken behavior, intentionally tracked
- plain failure: unexpected regression, should fail the build

### Common mistake

Using `xfail` to keep the suite green under deadline pressure and never revisiting it.

---

## 10. Mocking, monkeypatching, and test doubles

Mocking is useful, but over-mocking is one of the fastest ways to build brittle tests.

## 10.1 Main kinds of test doubles

- **dummy**: unused placeholder
- **stub**: returns canned data
- **fake**: lightweight working implementation
- **spy**: records calls
- **mock**: object used for behavior assertions

### Practical recommendation

Prefer:

- real pure objects when cheap
- fakes when behavior matters
- mocks when interaction itself is the contract

## 10.2 `unittest.mock` basics

Core objects:

- `Mock`
- `MagicMock`
- `AsyncMock`
- `patch`
- `patch.object`
- `patch.dict`
- `create_autospec`
- `ANY`
- `call`

## 10.3 Why `autospec` matters

Without autospec, mocks can accept invalid calls that real code would reject.

Strong default:

- `patch(..., autospec=True)`
- or `create_autospec(...)`

This makes the mock enforce the real call signature.

## 10.4 Canonical patch rule: patch where the object is looked up

This is one of the most important testing rules in Python.

Suppose:

```python
# clients.py
class PaymentClient:
    def charge(self, amount: int) -> str:
        return "tx-real"
```

```python
# service.py
from clients import PaymentClient


def checkout(amount: int) -> str:
    client = PaymentClient()
    return client.charge(amount)
```

Correct test:

```python
from service import checkout
from unittest.mock import patch


@patch("service.PaymentClient", autospec=True)
def test_checkout_uses_payment_client(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.charge.return_value = "tx-123"

    result = checkout(100)

    assert result == "tx-123"
    mock_client.charge.assert_called_once_with(100)
```

### Why this is correct

`checkout()` looks up `PaymentClient` in `service`, not in `clients`, because `service` imported it into its own namespace.

### Wrong patch target

```python
@patch("clients.PaymentClient")
```

That often patches the wrong place and leaves the real object in use.

## 10.5 `monkeypatch` vs `mock.patch`

Use `monkeypatch` when:

- patching environment variables
- patching dictionaries
- patching simple attributes in pytest style
- patching process-global state that should auto-revert

Use `mock.patch` when:

- you want mock-specific assertions
- you want `autospec`
- you are patching callables or classes and asserting interactions

## 10.6 Common `monkeypatch` uses

```python
def test_reads_env(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert load_mode() == "test"
```

```python
def test_missing_env(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)
    assert load_mode(default="dev") == "dev"
```

```python
def test_patch_constant(monkeypatch):
    monkeypatch.setattr(settings, "DEFAULT_TIMEOUT", 1)
    assert make_timeout() == 1
```

## 10.7 Call assertions you should know

- `assert_called_once_with(...)`
- `assert_called_with(...)`
- `assert_any_call(...)`
- `assert_has_calls([...])`
- `call_args`
- `call_args_list`
- `mock_calls`
- `reset_mock()`

For async:

- `assert_awaited()`
- `assert_awaited_once()`
- `assert_any_await(...)`
- `assert_has_awaits([...])`

## 10.8 `AsyncMock`

Use `AsyncMock` for async callables and async collaborators.

```python
from unittest.mock import AsyncMock


async def test_async_dependency():
    dependency = AsyncMock()
    dependency.fetch.return_value = {"ok": True}

    result = await use_dependency(dependency)

    assert result == {"ok": True}
    dependency.fetch.assert_awaited_once()
```

## 10.9 `create=True` is dangerous

`patch(..., create=True)` can make tests pass against attributes that do not actually exist.

Use it only when you truly need runtime-created attributes and understand the tradeoff.

## 10.10 Prefer fakes over deep mock trees

This:

```python
mock_client.session.transport.send.return_value = ...
```

is often a smell.

Prefer:

- inject a simpler seam
- create a fake collaborator
- test the behavior through a narrower abstraction

## 10.11 When to use a fake

Fakes are excellent for:

- repositories
- caches
- in-memory event buses
- object stores
- message publishers

They usually produce tests that are:

- more realistic than mocks
- less coupled to implementation
- easier to refactor

---

## 11. Testing real-world boundaries

The hardest test problems usually happen at system boundaries.

## 11.1 Filesystem

Prefer `tmp_path`:

```python
def write_report(path, content):
    path.write_text(content, encoding="utf-8")


def test_write_report(tmp_path):
    report = tmp_path / "report.txt"

    write_report(report, "ok")

    assert report.read_text(encoding="utf-8") == "ok"
```

### Best practices

- never depend on existing files in your home directory
- use explicit encodings
- keep tests path-agnostic

## 11.2 Environment variables

Use `monkeypatch.setenv` and `monkeypatch.delenv`, never the real environment directly.

### Good pattern

```python
def test_reads_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    assert get_api_key() == "secret"
```

## 11.3 Time

Time is a classic source of flaky tests.

Prefer:

- injecting a clock function
- passing `now` explicitly
- using a thin wrapper around time retrieval

Avoid:

- asserting exact wall-clock timing with sleeps
- directly relying on `datetime.now()` in logic-heavy code

### Strong design pattern

```python
from datetime import datetime, UTC


def build_expiry(now: datetime) -> datetime:
    return now.replace(tzinfo=UTC)
```

Then tests pass a fixed value instead of patching global time everywhere.

## 11.4 Randomness

Prefer:

- injecting a `random.Random` instance
- seeding test randomness explicitly
- testing invariants, not one lucky output

Avoid:

- tests that occasionally fail because the random branch did not happen

## 11.5 Network calls

Unit tests should almost never hit the real network.

Preferred patterns:

- patch the outbound client seam
- use a fake transport
- use a local test server in integration tests
- reserve real external calls for very limited contract or smoke checks

### Production rule

Make real network use an explicit test category, not the default.

## 11.6 Databases

### Unit tests

Use:

- repository fakes
- narrow mocks
- pure logic extracted away from ORM calls

### Integration tests

Use:

- the real database engine when behavior matters
- real migrations
- transaction rollback or clean setup/teardown

### Critical warning

Do not assume SQLite proves behavior for PostgreSQL or MySQL if your production semantics depend on:

- transactions
- JSON behavior
- SQL dialect
- locking
- constraints
- case sensitivity

## 11.7 Queues and background jobs

Test at two layers:

- unit tests against a fake publisher or worker boundary
- integration tests with the real broker or worker runtime for key flows

Assert:

- message contents
- retry policy behavior
- idempotency
- dead-letter or failure behavior where relevant

## 11.8 External APIs

Strong pattern:

- unit tests against your HTTP client seam
- contract tests against request and response shape
- targeted integration tests against sandbox or test endpoints

Assert:

- timeout handling
- retry behavior
- auth/header formation
- schema validation
- error mapping

Avoid:

- broad end-to-end tests that call unstable third-party systems on every PR

## 11.9 Side effects worth testing directly

Depending on the code, it may be correct to assert:

- file created
- email queued
- event published
- DB row written
- audit log emitted
- metric incremented
- retry scheduled

That is often more meaningful than asserting internal helper calls.

---

## 12. Async testing with pytest-asyncio

Async code adds extra failure modes:

- un-awaited coroutines
- dangling tasks
- event loop leakage
- timeout races
- cancellation bugs

## 12.1 Basic async test

```python
import asyncio
import pytest


async def fetch_value():
    await asyncio.sleep(0)
    return 42


@pytest.mark.asyncio
async def test_fetch_value():
    assert await fetch_value() == 42
```

If `pytest-asyncio` is configured in `auto` mode, the marker can be omitted for async test functions.

## 12.2 Discovery modes

`pytest-asyncio` supports:

- `strict`
- `auto`

If no mode is specified, the current docs say the default is `strict`.

### Use `strict` when

- your project mixes multiple async frameworks
- you want explicit ownership of async tests and fixtures

### Use `auto` when

- your codebase is asyncio-only
- you want the simplest pytest setup

## 12.3 Async fixtures

```python
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client():
    client = await make_client()
    yield client
    await client.aclose()
```

## 12.4 Event loop scope

Modern `pytest-asyncio` docs recommend being deliberate about event loop scope.

Strong default:

- keep neighboring tests on the same loop scope
- do not casually mix loop scopes in the same module or class
- keep the default test loop scope at `function` unless you have a clear reason to widen it

Relevant config knobs:

- `asyncio_default_test_loop_scope`
- `asyncio_default_fixture_loop_scope`
- `asyncio_debug`

If you need a shared loop:

```python
import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_uses_shared_module_loop():
    ...
```

## 12.5 Timeouts and cancellation

Async tests should exercise:

- normal completion
- timeout path
- cancellation path
- cleanup after cancellation

### Good practice

If your code spawns background tasks, make teardown explicitly cancel and await them.

## 12.6 Background task cleanup

Never let tests exit with orphaned tasks still running.

Common strategies:

- keep task handles and cancel them in teardown
- await shutdown hooks
- design components with explicit `start()` and `stop()` APIs

## 12.7 Async mocking

Use `AsyncMock` for async callables:

```python
from unittest.mock import AsyncMock
import pytest


class Service:
    async def fetch(self):
        raise NotImplementedError


async def run(service: Service):
    return await service.fetch()


@pytest.mark.asyncio
async def test_run_awaits_fetch():
    service = AsyncMock(spec=Service)
    service.fetch.return_value = {"ok": True}

    result = await run(service)

    assert result == {"ok": True}
    service.fetch.assert_awaited_once()
```

## 12.8 Async pitfalls to avoid

- mixing sync and async fixtures incorrectly
- using real sleeps instead of explicit coordination
- leaking event loop state between tests
- forgetting to await mocks
- asserting timing too tightly in CI

---

## 13. Coverage: how to measure it and how not to misuse it

Coverage is a diagnostic tool, not a proof of correctness.

## 13.1 What coverage tells you

Coverage tells you which lines and branches executed.

It does **not** tell you:

- whether assertions were meaningful
- whether edge cases were tested well
- whether the right behavior was validated

## 13.2 Statement coverage vs branch coverage

- **statement coverage**: was the line executed?
- **branch coverage**: were both decision paths exercised?

Branch coverage is usually more informative for logic-heavy code.

## 13.3 Canonical commands

Using `pytest-cov`:

```bash
pytest --cov=src/mypkg --cov-report=term-missing --cov-report=html
```

With branch coverage:

```bash
pytest --cov=src/mypkg --cov-branch --cov-report=term-missing
```

Using `coverage.py` directly:

```bash
coverage run -m pytest
coverage report -m
coverage html
```

## 13.4 `pytest-cov` practical notes

`pytest-cov` adds:

- easy integration with pytest
- coverage reporting during test runs
- xdist support
- per-test coverage contexts via `--cov-context=test`

Important config caveat from the docs:

- `--cov=<value>` overrides coverage's configured `source`
- `--cov-branch` overrides coverage's configured `branch`
- pytest-cov also overrides coverage's `parallel` option

If your coverage config file is the source of truth, it is often cleaner to use bare `--cov` rather than repeating package paths on the command line.

Example:

```bash
pytest --cov --cov-context=test --cov-report=html
```

## 13.5 Coverage thresholds

Thresholds are useful, but they should be sane.

Good uses:

- preventing obvious backsliding
- making coverage debt visible
- maintaining standards on critical packages

Bad uses:

- forcing meaningless tests for trivial getters
- rewarding broad but shallow tests
- treating 100% as automatically high quality

### Practical policy

- enforce a floor
- inspect missed lines
- review critical paths manually

## 13.6 Interpreting missed lines responsibly

Ask:

- is the missed code dead?
- is it error handling?
- is it a rare branch that needs an explicit test?
- is it defensive code that should exist but may not justify the same threshold?

The right response is often **write one meaningful test**, not "raise the global target."

## 13.7 Exclusions

Coverage exclusions should be rare and honest.

Examples commonly excluded:

- `if TYPE_CHECKING:`
- `if __name__ == "__main__":`
- truly unreachable debug-only scaffolding

### Warning

`# pragma: no cover` is easy to abuse. Exclude code because it is genuinely outside the tested runtime contract, not because writing the test is annoying.

## 13.8 Contexts

Coverage contexts help answer "which test covered this line?"

Useful for:

- debugging overlapping tests
- finding orphaned lines only covered by broad integration suites
- understanding setup vs run vs teardown execution

## 13.9 What high-value coverage usually looks like

- core business logic has strong branch coverage
- error handling is exercised
- boundary adapters are integration-tested
- critical workflows are covered at more than one layer

---

## 14. Scaling test suites in real projects

## 14.1 Parallel execution with `pytest-xdist`

Basic usage:

```bash
pytest -n auto
```

This distributes tests across worker processes.

### Benefits

- faster wall-clock time
- earlier feedback

### Risks it reveals

- hidden shared state
- order dependencies
- unsafe temp file usage
- tests that assume single-process execution

### Important limitation

`pytest-xdist` docs note that `-s` / `--capture=no` does not work the same way under xdist as in normal single-process runs.

They also note that debugger workflows such as `--pdb` do not work in distributed mode.

## 14.2 xdist design implications

Workers do their own collection, so inconsistent collection behavior across workers is a problem.

This means tests should avoid:

- collection-time randomness
- dynamic imports that depend on unstable environment state
- inconsistent generation of test cases

If a test truly needs worker-specific resources, xdist provides a `worker_id` fixture and related worker environment variables.

## 14.3 Grouping and fixture-aware parallelism

If tests must stay together because of expensive setup or shared state, use xdist distribution strategies intentionally rather than hoping random scheduling behaves.

But the better long-term fix is usually:

- remove hidden shared state
- make setup deterministic
- tighten fixture scope

## 14.4 Data builders and factories

As suites grow, hard-coded dictionaries become painful.

Useful patterns:

- builder functions
- fixture factories
- object mothers for legacy code

Good builder traits:

- sensible defaults
- easy overrides
- minimal magic
- obvious relationship to real domain data

Example:

```python
def build_order(**overrides):
    order = {
        "id": "ord-123",
        "currency": "USD",
        "subtotal": 100,
        "items": [{"sku": "abc", "qty": 1}],
    }
    order.update(overrides)
    return order
```

## 14.5 Property-based testing with Hypothesis

Hypothesis generates many inputs and shrinks failures to small reproductions.

It is especially useful for:

- parsers
- serializers
- math and normalization logic
- idempotency properties
- invariants over broad input spaces

### Simple Hypothesis example

```python
from hypothesis import given, strategies as st


def reverse_twice(text: str) -> str:
    return text[::-1][::-1]


@given(st.text())
def test_reverse_twice_is_identity(text):
    assert reverse_twice(text) == text
```

### Good properties are about invariants

Examples:

- sorting preserves elements and ordering relation
- encoding then decoding returns the original value
- a normalization function is idempotent
- creating then deleting a record leaves no residual state

## 14.6 Stateful testing

When the bug depends on a **sequence** of operations rather than one input, stateful testing becomes valuable.

This is advanced, but worth knowing for:

- caches
- queue consumers
- transactional workflows
- mutable domain objects

## 14.7 Useful pytest ecosystem choices

Practical stack for many teams:

- `pytest`
- `pytest-cov`
- `pytest-asyncio` if using asyncio
- `pytest-xdist` for scale
- Hypothesis for property-based testing

Adopt tools because they solve a real problem, not because every plugin looks attractive.

---

## 15. CI and release-confidence workflows

A production-grade suite is designed for CI from the start.

## 15.1 Strong CI defaults

- install dependencies from a clean environment
- avoid relying on local machine secrets or files
- run deterministic test categories by default
- fail on unexpected warnings
- produce machine-readable coverage output when useful

## 15.2 Example PR command

```bash
pytest -m "not slow and not e2e" \
  --cov=src/mypkg \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml
```

## 15.3 Example broader merge or nightly command

```bash
pytest -m "not e2e" -n auto --cov=src/mypkg --cov-branch
pytest -m "e2e or smoke"
```

## 15.4 What should gate merges

Usually:

- fast deterministic unit tests
- targeted integration tests for critical boundaries
- a sensible coverage threshold
- maybe a smoke subset if it is stable enough

Usually not:

- every slow environment-heavy end-to-end test on every commit

## 15.5 Flaky test policy

A flaky test is a production problem in your engineering system.

Treat it seriously:

- investigate root cause
- quarantine temporarily only with explicit tracking
- do not leave flaky tests silently rerunning forever

## 15.6 Stable test data in CI

Prefer:

- ephemeral databases
- isolated temp directories
- explicit environment injection
- fixed seeds when randomness is involved

Avoid:

- shared mutable test environments
- unbounded retries masking real failures

---

## 16. Common anti-patterns and production testing mistakes

## 16.1 Over-mocking

Symptom:

- tests assert internal call choreography instead of behavior

Better:

- assert outputs and side effects
- replace deep mocks with fakes or narrower seams

## 16.2 Testing implementation details instead of contracts

Symptom:

- harmless refactor breaks many tests

Better:

- test the public behavior or external contract

## 16.3 Giant fixtures with hidden setup

Symptom:

- hard to tell why a test passes

Better:

- smaller explicit fixtures
- local builders

## 16.4 Session-scoped mutable state

Symptom:

- tests pass alone and fail in suite or in parallel

Better:

- function scope by default
- explicit reset between tests if broader scope is truly needed

## 16.5 Sleep-based timing tests

Symptom:

- tests are slow and flaky in CI

Better:

- inject clocks
- await explicit signals
- use timeouts and deterministic coordination

## 16.6 Hitting the real network in unit tests

Symptom:

- slow, brittle, environment-sensitive unit suite

Better:

- fake or patch the client seam
- put real network checks in an explicit integration category

## 16.7 Using `xfail` as bug storage

Symptom:

- suite is green but broken behavior is normalized

Better:

- use strict `xfail`
- link to the bug
- remove it promptly when fixed

## 16.8 Chasing 100% coverage with low-value tests

Symptom:

- lots of trivial tests, little confidence

Better:

- target risky logic and important branches
- inspect uncovered critical paths manually

## 16.9 Huge parametrized matrices

Symptom:

- test runtime explodes
- failures are hard to interpret

Better:

- reduce combinations
- test equivalence classes
- move rare combinations to targeted tests

## 16.10 One global `conftest.py` that knows everything

Symptom:

- tests depend on invisible global magic

Better:

- localize fixtures by directory and concern

---

## 17. Troubleshooting checklist

When a test suite starts behaving badly, check these first.

## 17.1 "Passes locally, fails in CI"

Common causes:

- timezone or locale differences
- real network dependence
- implicit file paths
- environment variables not set
- ordering or parallelism issues
- warnings treated differently

## 17.2 "Passes alone, fails in suite"

Common causes:

- leaked global state
- mutated shared fixture data
- monkeypatch not applied where expected
- session fixture contamination

## 17.3 "Fails only under xdist"

Common causes:

- shared filesystem paths
- DB data collisions
- test-order assumptions
- non-unique ports
- collection-time nondeterminism

One especially easy xdist trap is parametrizing from unordered iterables such as `set`, because workers must collect the same tests in the same order.

## 17.4 "Coverage looks high, bugs still ship"

Common causes:

- shallow assertions
- line coverage without branch coverage
- missing integration tests at boundaries
- critical failure paths untested

## 17.5 "Mocks keep breaking on refactor"

Common causes:

- patching internal structure instead of a stable seam
- no autospec
- asserting every internal call

## 17.6 "Async tests leak tasks or hang"

Common causes:

- background tasks not cancelled
- incorrect fixture teardown
- real sleeps instead of explicit synchronization
- multiple loop scopes used carelessly

---

## 18. Fast revision checklist

Use this as a last-minute revision sheet.

- `pytest` discovers `test_*.py` and `*_test.py`, plus `test_*` functions and methods.
- Prefer plain `assert` for rich assertion introspection.
- Use `pytest.raises(..., match=...)` for exceptions.
- Use `pytest.warns(...)` and treat unexpected warnings seriously.
- Use `capsys` or `capfd` for output and `caplog` for logs.
- Learn fixtures deeply: dependency injection, scopes, `yield` teardown, `conftest.py`.
- Default fixture scope should usually be `function`.
- Use `tmp_path` for filesystem tests.
- Use `monkeypatch` for env vars, globals, mappings, and simple attribute patching.
- Use parametrization for repeated behavior checks, but stop before readability collapses.
- Register custom markers and use `--strict-markers`.
- Know the difference between `skip`, `xfail`, and real failure.
- Set `xfail_strict = true`.
- Patch where the object is looked up, not where it was originally defined.
- Prefer `autospec=True` or `create_autospec()` with mocks.
- Use `AsyncMock` for async collaborators.
- Avoid hitting real network or real wall-clock time in unit tests.
- Use real integration tests for databases and other meaningful boundaries.
- For asyncio projects, understand `strict` vs `auto` mode in `pytest-asyncio`.
- Test cancellation, cleanup, and background-task shutdown in async code.
- Use branch coverage, not just line coverage.
- Treat coverage as a diagnostic, not a quality proof.
- Use `pytest --lf`, `--ff`, `-k`, `-m`, `--collect-only`, and `--pdb` fluently.
- Use `pytest-xdist` intentionally and expect it to expose shared-state bugs.
- Use builders, fixture factories, and Hypothesis where they make tests clearer and stronger.
- Keep CI deterministic, isolated, and explicit about categories and gates.

---

## 19. Official references

Primary documentation used to cross-check this guide:

- `pytest` stable docs: <https://docs.pytest.org/en/stable/>
- `pytest` good practices: <https://docs.pytest.org/en/latest/goodpractices.html>
- `pytest` fixtures: <https://docs.pytest.org/en/stable/fixture.html>
- `pytest` fixtures reference: <https://docs.pytest.org/en/stable/reference/fixtures.html>
- `pytest` parametrization: <https://docs.pytest.org/en/stable/how-to/parametrize.html>
- `pytest` monkeypatch: <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>
- `pytest` tmp_path: <https://docs.pytest.org/en/stable/how-to/tmp_path.html>
- `pytest` logging and `caplog`: <https://docs.pytest.org/en/stable/how-to/logging.html>
- `pytest` warnings: <https://docs.pytest.org/en/stable/how-to/capture-warnings.html>
- `pytest` skip and xfail: <https://docs.pytest.org/en/stable/how-to/skipping.html>
- `pytest` markers: <https://docs.pytest.org/en/stable/how-to/mark.html>
- `pytest` cache / last-failed / stepwise: <https://docs.pytest.org/en/stable/how-to/cache.html>
- `pytest` output and debugging flags: <https://docs.pytest.org/en/stable/how-to/output.html>
- Python `unittest.mock`: <https://docs.python.org/3/library/unittest.mock.html>
- Python `unittest.mock` examples: <https://docs.python.org/3/library/unittest.mock-examples.html>
- `pytest-asyncio`: <https://pytest-asyncio.readthedocs.io/en/stable/>
- `coverage.py`: <https://coverage.readthedocs.io/en/latest/>
- `pytest-cov`: <https://pytest-cov.readthedocs.io/en/stable/>
- `pytest-xdist`: <https://pytest-xdist.readthedocs.io/en/stable/>
- Hypothesis: <https://hypothesis.readthedocs.io/en/latest/>

---

## Final takeaway

If you remember only a few things, remember these:

- keep tests deterministic
- test behavior, not internals
- use fixtures and parametrization deliberately
- patch where objects are looked up
- prefer branch coverage over vanity metrics
- use integration tests for real boundaries
- treat flaky tests as real defects
- optimize for suites that developers trust enough to run constantly
