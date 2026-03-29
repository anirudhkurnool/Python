# Production-Grade Logging in Python and in Software Systems Generally

This guide is a **comprehensive reference** for designing, implementing, operating, and reviewing logging in production systems, with a strong focus on **Python**. It covers both the **general concepts** that apply in any language/runtime and the **Python-specific mechanics** you need for real services, CLIs, workers, schedulers, APIs, and libraries.

---

## 1. What logging is, and what it is not

### Logging is
Logging is the recording of **time-ordered events** about system behavior. In production, logs are used for:

- debugging and incident response
- operational visibility
- security monitoring and forensics
- auditability and compliance
- business-event visibility
- cross-service correlation
- postmortem analysis

### Logging is not
Logging is **not** a substitute for:

- **metrics**: aggregated numeric signals such as request rate, latency, queue depth, error rate
- **traces**: end-to-end request or workflow causality across services
- **profiling**: CPU, memory, allocation, lock, and hot-path analysis
- **auditing**: although some audit events are logged, audit trails have stricter integrity and retention requirements

### The right mental model
Treat logs as **event streams**, not as application-owned text files. In modern production systems, applications typically emit log events to stdout/stderr or to a transport/collector, and a platform-level pipeline ships, enriches, stores, indexes, and retains them.

---

## 2. Core principles of production-grade logging

A production-grade logging design should satisfy all of these:

1. **Useful to humans**
   - clear messages
   - consistent severity
   - enough context to explain what happened

2. **Useful to machines**
   - structured fields
   - stable field names
   - queryable attributes
   - predictable severity mapping

3. **Low operational risk**
   - does not block critical request paths
   - degrades gracefully under backpressure
   - does not crash the process when log sinks fail

4. **Safe**
   - avoids secrets and sensitive data
   - resists log injection and parser confusion
   - protects integrity, confidentiality, and availability

5. **Correlatable**
   - ties together request IDs, trace IDs, user/session identifiers, tenant IDs, job IDs, resource identifiers, and deployment metadata

6. **Configurable**
   - verbosity can be raised or lowered safely
   - debug logging can be enabled intentionally and temporarily
   - configuration is centralized and reviewable

7. **Economical**
   - log volume is controlled
   - high-cardinality payloads are avoided
   - retention and indexing are planned, not accidental

---

## 3. The key distinction: logs, metrics, traces, and events

A mature observability practice uses all three primary signals:

### Logs
Best for:
- exact event details
- exception stack traces
- rich contextual debugging
- security and audit-relevant events
- rare edge-case reconstruction

### Metrics
Best for:
- dashboards
- alerting on rate/error/latency/saturation
- cheap long-term trend analysis

### Traces
Best for:
- end-to-end request flow
- latency decomposition
- service dependency analysis
- distributed root-cause analysis

### Rule of thumb
- If you need to **count**, **alert**, or **graph**, use a metric.
- If you need to understand **causality across services**, use traces.
- If you need the **exact record of what happened**, use logs.

A single important occurrence often produces:
- a trace/span,
- one or more logs,
- and one or more metrics.

---

## 4. What should be logged

You should log events that are:

### Operationally important
- service startup and shutdown
- configuration summary at boot (sanitized)
- dependency connection state changes
- retries, failovers, circuit-breaker state changes
- slow operations
- degraded mode activation
- background job starts/completions/failures
- queue consumer lag or processing anomalies
- schema migration start/end/failure

### Request/workflow important
- request received and completed
- request outcome and latency
- upstream/downstream call failures
- idempotency conflicts
- validation failures
- rate limits
- cache misses only if they matter operationally
- retries and retry exhaustion
- state transitions in domain workflows

### Security important
- authentication attempts and outcomes
- authorization denials
- account lockouts
- MFA events
- suspicious input or abuse patterns
- privilege changes
- token/session lifecycle events where allowed
- security control failures
- administrative actions

### Audit important
- create/update/delete of critical entities
- permission or role changes
- approval/rejection decisions
- money movement / booking / order state transitions
- data export or bulk download
- compliance-sensitive access

### Usually not worth logging
- every loop iteration
- every function entry/exit
- every successful low-value DB call
- every cache hit
- full request/response bodies by default
- giant ORM objects
- repeated noise that belongs in metrics instead

---

## 5. What every useful log entry should contain

A good log event answers **when, where, who, what, and outcome**.

A practical canonical schema usually includes:

### Temporal
- `timestamp`
- optionally `observed_timestamp` or ingestion time at collector

### Severity
- `level` (or severity text)
- optionally severity number if you map to a standard model

### Identity of source
- `service.name`
- `service.version`
- `service.namespace` or product domain
- environment: `dev`, `staging`, `prod`
- region / availability zone / cluster
- host / pod / container / process / thread
- logger name or instrumentation scope

### Correlation
- `trace_id`
- `span_id`
- `request_id`
- `correlation_id`
- `session_id` when allowed
- `job_id`, `task_id`, `workflow_id`
- `tenant_id`, `customer_id`, `account_id` where appropriate

### Subject / actor
- `user_id` or pseudonymous equivalent
- principal type / role
- API key ID or client ID
- auth method

### Event classification
- stable `event_name`
- subsystem / component
- operation / action
- category such as `security`, `http`, `db`, `billing`, `queue`

### Outcome
- status or result: `success`, `failure`, `timeout`, `retrying`, `denied`
- error type / code
- HTTP status / RPC status / DB error code
- latency / duration

### Message body
- a concise human-readable message

### Structured details
- a bounded set of extra fields with stable names and documented semantics

---

## 6. Severity levels: use them consistently

Different stacks vary slightly, but this policy works well in most systems:

### DEBUG
Detailed diagnostics useful during development or temporary incident debugging.

Use for:
- branch decisions
- intermediate state summaries
- retry attempt detail
- non-default code-path explanation

Do **not** leave high-volume DEBUG enabled broadly in prod for long periods.

### INFO
Normal, noteworthy business or operational events.

Use for:
- service start
- request completion summary
- job completion
- state transition
- periodic checkpoints
- important config mode selection

### WARNING
Something unexpected happened, but the system is still functioning.

Use for:
- retryable failures
- degraded mode
- partial results
- suspicious but not confirmed abuse
- fallback path activation
- unexpectedly slow operations crossing a threshold

### ERROR
A specific operation failed.

Use for:
- request failed
- task failed
- dependency operation failed after retry budget
- data write failed
- user-facing operation could not complete

### CRITICAL / FATAL
The service or a critical subsystem is not viable.

Use for:
- process cannot start
- unrecoverable configuration error
- data corruption detected
- repeated fatal dependency unavailability such that service must exit
- catastrophic invariant violation

### Important severity discipline
- Do not log expected 4xx user mistakes at `ERROR` unless they indicate platform malfunction.
- Do not log the same failure as `ERROR` at every layer. Pick one layer to emit the primary error, and let lower layers log at `DEBUG` or `INFO` only when useful.
- A noisy severity policy destroys alert quality and operator trust.

---

## 7. Message design: write events, not prose dumps

### Prefer stable event names
Use a field like:

```json
{
  "event_name": "payment.authorize.failed"
}
```

This is better than relying only on free-form English text.

### Write human-readable messages, but keep them compact
Good:
- `payment authorization failed`
- `request completed`
- `retrying upstream call after timeout`

Bad:
- `some weird thing happened`
- `error!!!`
- huge interpolated blobs

### Separate the stable text from the variable data
Good:
```python
logger.info("request completed", extra={"status_code": 200, "duration_ms": 38})
```

Not ideal:
```python
logger.info(f"request completed with status 200 in 38 ms for user {user_id} on endpoint {path}")
```

Why:
- structured fields are queryable
- they avoid fragile parsing
- they reduce message churn
- they support better dashboards and alerts

---

## 8. Structured logging

### Why structured logs matter
Plain text logs are fine for humans but poor for automation. Production systems benefit from structured logs because they support:

- filtering by fields
- grouping and aggregation
- joins with traces/metrics
- stable parsing
- schema evolution

### Recommended format
Use **JSON** or another structured event representation.

### Keep field names stable
Choose a schema and document it. Avoid ad hoc keys drifting across teams:
- prefer `request_id` over `reqId`, `rid`, `requestId`
- prefer `duration_ms` over `latency`, `time_ms`, `elapsed`

### Beware cardinality explosion
Some fields are dangerous in indexes or aggregations:
- raw user email
- arbitrary URL with IDs embedded
- stack traces as labels
- request body fragments
- search queries
- UUID-like fields in metrics labels

These can be present in logs when justified, but do not blindly index everything.

### A practical event shape
```json
{
  "timestamp": "2026-03-28T10:15:04.123Z",
  "level": "INFO",
  "service.name": "billing-api",
  "service.version": "2026.03.28-1",
  "environment": "prod",
  "event_name": "http.request.completed",
  "message": "request completed",
  "trace_id": "6db1d7c4d3f24a14bf6f2d2b669d4c5b",
  "span_id": "5d2f6e4b32ac9fa1",
  "request_id": "0f856c5f-2ec7-4ed8-8a17-938f7594d1a3",
  "method": "GET",
  "route": "/v1/invoices/{invoice_id}",
  "status_code": 200,
  "duration_ms": 38
}
```

---

## 9. Correlation and context propagation

This is one of the highest-value logging concepts in production.

### Correlation IDs
A correlation ID ties together all logs emitted while handling one request, job, or workflow.

Common identifiers:
- `request_id`
- `trace_id`
- `span_id`
- `job_id`
- `workflow_id`
- `message_id`
- `tenant_id`

### In distributed systems
If you use distributed tracing, propagate context across service boundaries and ensure logs carry:
- `trace_id`
- `span_id`

That allows a log entry to be opened from a trace and a trace to be opened from a log query.

### Context propagation rules
- generate request context at the edge if absent
- propagate it through HTTP, gRPC, queue headers, and job metadata
- attach it automatically in every log record
- never rely on developers to manually pass every field at every callsite

### In Python
Use `contextvars` for request/task-local context in modern code, especially if you use threads and `asyncio`.

---

## 10. Time and timestamps

Time handling mistakes ruin logs.

### Always log an absolute timestamp
Prefer:
- UTC
- ISO 8601 / RFC 3339 style strings
- or an epoch timestamp plus consistent renderer

Example:
- `2026-03-28T10:15:04.123Z`

### Also consider duration and monotonic timing
Wall-clock time is for ordering across systems.  
Monotonic clocks are for measuring duration accurately.

Log:
- `duration_ms`
- timeout thresholds crossed
- retry backoff intervals

### Distinguish event time vs observation time
A collector may observe a log later than the source emitted it. Mature data models include both:
- event time
- observed / ingested time

This distinction matters for:
- delayed shippers
- offline/mobile buffering
- asynchronous ingestion
- out-of-order pipelines

---

## 11. Privacy, secrets, and compliance

This is non-negotiable in production.

### Never log secrets
Do not log:
- passwords
- API keys
- private tokens
- refresh tokens
- session cookies
- private keys
- unredacted Authorization headers
- raw credentials in URLs

### Treat PII carefully
Avoid logging or heavily restrict:
- full names
- full email addresses
- phone numbers
- street addresses
- government IDs
- payment card data
- healthcare data
- exact user content unless the product requires it and policy allows it

### Prefer safe alternatives
- pseudonymous IDs
- hashes or irreversible digests where appropriate
- token fingerprints, not tokens
- masked values:
  - `user_email_domain="example.com"`
  - `card_last4="4242"`

### Redaction strategy
Implement redaction in more than one layer:
1. **at source** where values enter logging calls
2. **in logging filters/formatters**
3. **in collectors/processors**
4. **in storage/query policy**

### Log injection protection
Sanitize attacker-controlled input to avoid:
- newline injection
- delimiter confusion
- terminal escape sequences
- parser breakage

### Retention policy
Retention must be intentional:
- enough for incident investigation
- not longer than policy, law, or contract allows
- separate policies for security logs, audit logs, app logs, and temporary debug logs

### Access control
Production logs may contain sensitive operational intelligence. Restrict:
- who can read them
- who can export them
- who can delete them
- who can change retention

---

## 12. Reliability, backpressure, and performance

Logs are part of the production data path. Treat them like one.

### The main failure modes
- synchronous network logging blocks request threads
- file I/O stalls request handling
- sink outage causes memory growth
- queue fills up
- repeated error logs amplify an outage
- logging too much increases CPU, bandwidth, storage cost, and index pressure

### Strategies
#### Prefer non-blocking / decoupled pipelines
- in-process queue + background listener
- stdout/stderr + external collection agent
- local collector sidecar/daemon

#### Decide on a backpressure policy
When the sink is slow, what happens?
- block the app
- drop low-priority logs
- sample noisy logs
- spill to local disk
- apply bounded buffering

There is no universal answer. Decide deliberately.

#### Sample noise, not signal
Good candidates for sampling:
- repeated identical warnings
- high-volume success logs
- repeated dependency timeout errors during a major incident

Do **not** sample:
- security/audit-critical events
- irrecoverable failures
- rare invariant violations
- compliance-relevant actions

#### Aggregate repeated events where useful
Instead of logging 100,000 identical lines:
- count them
- emit periodic summaries
- use rate-limited warnings

### Logging should not crash the service
In production, sink failures should not take down the application unless the system is explicitly designed to be audit-fail-closed.

---

## 13. Transport and architecture patterns

### Common architectures

#### Pattern A: app -> stdout/stderr -> platform collector
Best for:
- containers
- Kubernetes
- serverless
- modern PaaS

Pros:
- simple
- twelve-factor aligned
- app does not own file rotation
- easy platform aggregation

#### Pattern B: app -> local queue/handler -> background thread/process -> sink
Best for:
- long-running services where format/enrichment must happen in-process
- local file or network sinks with decoupling

Pros:
- isolates request path from slow sink

#### Pattern C: app -> local collector/agent -> backend
Best for:
- heterogeneous polyglot estates
- advanced enrichment, retries, batching, filtering, routing

Pros:
- vendor-neutral architecture
- easier to change destinations
- central place for retries, batching, and sensitive-data filtering

### Files in modern production
File logging still exists, but in many modern environments you should avoid making the app own:
- rotation
- retention
- shipping
- indexing

In containers especially, stdout/stderr is usually the simplest and safest default.

---

## 14. Rotation, retention, and disposal

### Rotation
If you write files:
- rotate by size or time
- compress old files if appropriate
- ensure rotation cannot corrupt or split lines unexpectedly
- ensure the collector follows rotated files correctly

### Retention
Define:
- online searchable retention
- warm archive retention
- cold archive retention
- deletion policy
- legal hold process where relevant

### Disposal
Delete logs when retention expires.  
Do not keep temporary debug dumps forever.

### Audit and security logs may need stronger guarantees
- immutability or append-only storage
- tamper-evidence
- access monitoring
- explicit retention schedules

---

## 15. Alerting and monitoring from logs

Logs are not just for searching after an incident.

### Common alert patterns from logs
- error rate spikes by event type
- auth failure anomalies
- repeated `CRITICAL` boot failures
- circuit-breaker open
- data corruption indicator
- dead-letter queue growth or poison-message pattern

### Avoid raw-text alerts
Prefer alerts based on:
- structured fields
- event names
- severity
- stable error codes

### Use metrics derived from logs sparingly
If a condition is important enough to page on continuously, consider emitting a direct metric too.

---

## 16. General anti-patterns

Avoid these:

- logging only free-form strings and no structured fields
- logging secrets
- using inconsistent field names across services
- treating every failure as `ERROR`
- logging the same exception at every layer
- dumping whole objects / ORM rows / request bodies
- file logging directly from many worker processes to one file
- creating a logger for every request or object instance
- relying on ad hoc regex parsing of human prose
- enabling verbose debug forever in production
- changing log schema without coordination
- using logs as the primary data store for analytics
- letting ingestion outages crash the service unintentionally

---

# Python-specific logging

---

## 17. Python logging architecture: the moving parts

Python’s standard library `logging` package is flexible enough for production use when configured correctly.

### The main objects

#### Logger
The object application code calls:
```python
logger = logging.getLogger(__name__)
logger.info("hello")
```

#### Handler
Sends a record to a destination:
- stream
- file
- socket
- queue
- syslog
- SMTP
- etc.

#### Formatter
Turns a `LogRecord` into output text.

#### Filter
Allows or rejects records, and can also enrich them.

#### LogRecord
The event object created for each logging call.

#### Logger hierarchy
Logger names are hierarchical:
- `app`
- `app.api`
- `app.api.users`

Child loggers propagate to ancestors unless `propagate = False`.

### The default hierarchy rule
The idiomatic pattern in Python is:
```python
logger = logging.getLogger(__name__)
```

This gives you module-level hierarchy and lets top-level config control behavior.

---

## 18. Root logger, propagation, and duplicate logs

This is one of the most common sources of confusion.

### Propagation
If propagation is enabled on `A.B.C`, records flow to handlers on:
- `A.B.C`
- then `A.B`
- then `A`
- then root

### Duplicate logs happen when
You attach handlers to both:
- a child logger
- and an ancestor/root logger

and leave propagation enabled.

### Production rule
Usually do one of these:

#### Option 1: configure handlers only on root
Recommended for most applications.

#### Option 2: configure handlers on a specific application logger and set:
```python
logger.propagate = False
```

Do not mix these patterns casually.

---

## 19. `basicConfig()` vs real configuration

### `basicConfig()`
Useful for:
- tiny scripts
- demos
- very small internal tools

Not enough by itself for most production systems.

### Use `dictConfig()` for production
It is more explicit, composable, and reviewable.

### Important gotcha: `disable_existing_loggers`
In Python config APIs, `disable_existing_loggers` defaults in a way that often surprises people.  
For most real applications, set it explicitly to:

```python
"disable_existing_loggers": False
```

Otherwise, existing non-root loggers may be disabled unless explicitly named.

---

## 20. Application code vs library code in Python

### If you are writing an application
Your application is responsible for:
- configuring handlers
- formatters
- filters
- levels
- sinks
- propagation policy

### If you are writing a reusable library
Your library should:
- create named loggers
- **not** configure global logging
- **not** add real handlers
- attach only `NullHandler` if needed

Example:
```python
# mylib/__init__.py
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
```

Why:
- applications, not libraries, own logging policy
- libraries should not unexpectedly emit to stderr or files

---

## 21. Recommended production Python baseline

For most Python services:

- use the stdlib `logging` package
- create module-level loggers with `getLogger(__name__)`
- configure logging centrally at process startup with `dictConfig()`
- send output to stdout in containers
- prefer structured JSON output
- use `contextvars` for request/task context
- add correlation fields automatically
- use a queue-based handler/listener if formatting or sink I/O might block
- use `logger.exception(...)` only in `except` blocks
- avoid logging the same exception multiple times
- use `stacklevel` in wrappers/helpers
- test logging behavior

---

## 22. A production-grade Python JSON logging setup

Below is a self-contained stdlib-based example.

### Features
- centralized `dictConfig`
- stdout output
- JSON formatter
- UTC timestamps
- `contextvars`-based request context
- safe enrichment filter
- structured `extra` fields
- works well in containers

```python
import contextvars
import json
import logging
import logging.config
import sys
from datetime import datetime, timezone

# Request/task-local context
request_id_var = contextvars.ContextVar("request_id", default=None)
trace_id_var = contextvars.ContextVar("trace_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)

class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        record.request_id = request_id_var.get()
        record.trace_id = trace_id_var.get()
        record.user_id = user_id_var.get()
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
            "process": record.process,
            "thread": record.thread,
            "request_id": getattr(record, "request_id", None),
            "trace_id": getattr(record, "trace_id", None),
            "user_id": getattr(record, "user_id", None),
            "service.name": "billing-api",
            "service.version": "2026.03.28-1",
            "environment": "prod",
        }

        # Pick up structured fields passed via extra=...
        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "asctime"
            }:
                continue
            payload.setdefault(key, value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "context": {
            "()": ContextFilter,
        }
    },
    "formatters": {
        "json": {
            "()": JsonFormatter,
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["context"],
            "formatter": "json",
            "level": "INFO",
        }
    },
    "root": {
        "handlers": ["stdout"],
        "level": "INFO",
    },
}

def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)

logger = logging.getLogger(__name__)

def main() -> None:
    configure_logging()

    request_id_var.set("req-123")
    trace_id_var.set("9b1deb4d3b7d4bad9bdd2b0d7b3dcb6d")
    user_id_var.set("user-42")

    logger.info(
        "request completed",
        extra={
            "event_name": "http.request.completed",
            "method": "GET",
            "route": "/v1/invoices/{invoice_id}",
            "status_code": 200,
            "duration_ms": 38,
        },
    )

if __name__ == "__main__":
    main()
```

### Why this is good
- context is automatic
- output is structured
- handlers are configured once
- code at call sites stays concise
- fields are queryable

---

## 23. Use `%`-style interpolation correctly in logging calls

Python logging defers message formatting until needed. That is why these are preferred:

```python
logger.info("user %s created invoice %s", user_id, invoice_id)
logger.warning("retrying after %s seconds", backoff)
```

Prefer that to eager interpolation such as:
```python
logger.info(f"user {user_id} created invoice {invoice_id}")
```

Why:
- formatting work is skipped if the message level is disabled
- it matches the stdlib logging contract
- it reduces unnecessary CPU work in hot paths

### When to use `extra`
Use `extra` for queryable structured fields:
```python
logger.info(
    "invoice created",
    extra={"event_name": "invoice.created", "invoice_id": invoice_id}
)
```

A good pattern is:
- short stable human message in `msg`
- structured details in `extra`

---

## 24. Contextual logging in Python

There are several ways to inject context.

### Option A: `extra=...`
Good for one-off fields.

```python
logger.info("job finished", extra={"job_id": job_id, "duration_ms": 512})
```

### Option B: `LoggerAdapter`
Good when you want a logger that always carries some context.

```python
import logging

base_logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(base_logger, {"component": "reconciler"})

logger.info("cycle started")
```

### Option C: `Filter`
Good for injecting context globally into records.

```python
class TenantFilter(logging.Filter):
    def filter(self, record):
        record.tenant_id = current_tenant()
        return True
```

### Option D: `contextvars`
Best for request/task-local context in modern Python.

```python
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default=None)
```

### Option E: `LogRecordFactory`
Advanced hook for record creation-time enrichment.

```python
import logging

old_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.service_name = "billing-api"
    return record

logging.setLogRecordFactory(record_factory)
```

### Which one should you choose?
- one-off event fields -> `extra`
- wrapper logger with stable context -> `LoggerAdapter`
- broad enrichment and gating -> `Filter`
- request/task context -> `contextvars` + filter/factory
- framework-wide attribute injection -> `LogRecordFactory`

---

## 25. `stacklevel`, helper functions, and correct caller location

If you wrap logging in helper functions, caller metadata can become misleading.

Bad:
```python
def log_retry(logger, delay):
    logger.warning("retrying after %s seconds", delay)
```

This records the helper as the caller.

Better:
```python
def log_retry(logger, delay):
    logger.warning("retrying after %s seconds", delay, stacklevel=2)
```

Now the line number and function name point to the helper’s caller, which is usually what you want.

---

## 26. Exception logging in Python

### Use `logger.exception(...)` inside `except`
```python
try:
    charge_card()
except PaymentGatewayError:
    logger.exception(
        "payment authorization failed",
        extra={"event_name": "payment.authorize.failed"}
    )
```

This automatically includes exception information.

### Or use `exc_info=True`
```python
try:
    run_job()
except Exception:
    logger.error("job failed", exc_info=True)
```

### Do not log and re-log the same exception everywhere
Choose a boundary.

Example policy:
- leaf function raises
- service layer wraps or annotates if needed
- request boundary logs once with full context
- upstream caller does not log the same stack trace again unless adding genuinely new information

### Include error classification
Pair stack traces with:
- `error_type`
- `error_code`
- `operation`
- `dependency`
- `retryable`
- `outcome`

Example:
```python
except TimeoutError:
    logger.warning(
        "upstream request timed out",
        extra={
            "event_name": "upstream.timeout",
            "dependency": "inventory-api",
            "retryable": True,
        },
        exc_info=True,
    )
```

### Use `stack_info=True` when needed
This shows the current call stack even if there is no active exception.

---

## 27. Queue-based logging for lower request latency

If handlers do slow work, decouple the request path.

### When this is useful
- JSON serialization is heavy
- network sink can block
- file I/O can stall
- SMTP/syslog/socket handlers are used
- high-throughput APIs need low tail latency

### Stdlib example: `QueueHandler` + `QueueListener`

```python
import atexit
import json
import logging
import logging.handlers
import queue
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)

log_queue = queue.SimpleQueue()

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(JsonFormatter())
stream_handler.setLevel(logging.INFO)

listener = logging.handlers.QueueListener(
    log_queue,
    stream_handler,
    respect_handler_level=True,
)
listener.start()
atexit.register(listener.stop)

root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers.clear()
root.addHandler(logging.handlers.QueueHandler(log_queue))

logger = logging.getLogger(__name__)
logger.info("service started", extra={"event_name": "service.started"})
```

### Design notes
- request thread enqueues quickly
- listener thread formats and emits
- if you need bounded queues, decide whether to block, drop, or sample when full
- test shutdown/flush behavior

---

## 28. Multi-threading, asyncio, and multiprocessing in Python

### Threads
The stdlib logging module is thread-safe.

### `asyncio`
The stdlib module is not an async-native API, but it can be used safely from async code.  
What matters most is avoiding blocking handlers in the event loop path.

Use:
- stdout + platform collection
- or queue-based handlers
- and `contextvars` for task-local context

### Multiple processes
This is where many systems get it wrong.

#### Important rule
Do **not** have multiple worker processes write directly to the same file with normal file handlers.

Instead use:
- stdout/stderr collected by the runtime
- a socket listener
- a queue/listener process
- or a collector/agent

### Web workers (Gunicorn/uWSGI style)
In multi-process web servers, avoid direct file handlers in each worker process. Prefer:
- stdout/stderr
- or a separate listener / collector process

---

## 29. File handlers in Python: when they are appropriate

Python provides:
- `FileHandler`
- `RotatingFileHandler`
- `TimedRotatingFileHandler`
- `WatchedFileHandler`

### These are appropriate when
- you truly own the host
- file-based ops is intentional
- stdout collection is not the chosen platform model
- a local sidecar/agent tails files safely

### Be careful with
- multiple processes
- symlinked paths pointing to same file
- rotation race conditions
- delayed flush visibility
- disk-full conditions
- retention policy drift

### In containerized systems
Prefer stdout/stderr unless you have a strong reason not to.

---

## 30. Filters are more powerful than many teams realize

Filters can:
- accept/reject records
- enrich records
- count records
- redact fields
- implement temporary rate limiting
- change records before a handler emits them

In Python 3.12+, filters can even return a replacement `LogRecord` rather than mutating in place.

### Example: simple redaction filter
```python
import logging
import re

SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization:\s*bearer\s+)[^\s]+"),
    re.compile(r"(?i)(api[_-]?key=)[^&\s]+"),
]

class RedactionFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        for pattern in SECRET_PATTERNS:
            message = pattern.sub(r"\1[REDACTED]", message)

        # Replace record.msg/args so formatters use the sanitized version.
        record.msg = message
        record.args = ()
        return True
```

### Example: very simple rate-limited warning filter
```python
import logging
import time

class EveryNSecondsFilter(logging.Filter):
    def __init__(self, min_interval_seconds: float):
        super().__init__()
        self.min_interval_seconds = min_interval_seconds
        self._next_allowed = 0.0

    def filter(self, record):
        now = time.monotonic()
        if now >= self._next_allowed:
            self._next_allowed = now + self.min_interval_seconds
            return True
        return False
```

Use these carefully. Filters should stay deterministic, bounded, and easy to reason about.

---

## 31. Capturing warnings

Python can route `warnings` output into logging.

```python
import logging

logging.captureWarnings(True)
```

This sends warnings to a logger named `py.warnings` at warning severity.

Use it when you want:
- one pipeline for warnings and logs
- searchable deprecation warnings
- uniform formatting/transport

---

## 32. Logging configuration patterns that scale in Python

### Centralize configuration
Have one place at process startup that configures logging.

Good:
- `logging_setup.py`
- app bootstrap module
- framework startup hook

Bad:
- random modules calling `basicConfig()`
- ad hoc handler creation throughout the codebase

### Use environment to choose policy, not ad hoc code
Example decisions by environment:
- dev -> console pretty text, level DEBUG
- prod -> JSON to stdout, level INFO
- incident mode -> specific logger elevated to DEBUG temporarily

### Keep logger names stable
Usually module names are enough:
```python
logging.getLogger(__name__)
```

You can add top-level application namespaces if useful:
- `myapp.api.orders`
- `myapp.workers.reconcile`

---

## 33. Testing logging in Python

Logging behavior is part of system behavior. Test it.

### Things to test
- important events are emitted
- context fields are present
- secrets are redacted
- severity is correct
- duplicate logging does not occur
- failure paths include exception info
- noisy paths are rate-limited/sampled as intended

### `unittest` example with `assertLogs`
```python
import logging
import unittest

logger = logging.getLogger("payments")

def pay():
    logger.error("payment failed", extra={"event_name": "payment.failed"})

class LoggingTests(unittest.TestCase):
    def test_logs_failure(self):
        with self.assertLogs("payments", level="ERROR") as cm:
            pay()

        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].levelname, "ERROR")
        self.assertEqual(cm.records[0].event_name, "payment.failed")
```

### Also test negative behavior
- no secret leakage
- no logs above threshold when disabled
- no duplicate outputs with propagation rules

---

## 34. A practical Python text formatter for local development

Structured JSON is great in prod, but developers often prefer readable text locally.

```python
import logging
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "dev": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s [request_id=%(request_id)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "filters": {
        "context": {
            "()": "myapp.logging_setup.ContextFilter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "dev",
            "filters": ["context"],
            "level": "DEBUG",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
```

A common production approach is:
- text formatter in development
- JSON formatter in production
- same logical fields in both

---

## 35. Recommended schema conventions for Python services

A practical field set for Python APIs and workers:

### Global fields
- `timestamp`
- `level`
- `message`
- `event_name`
- `logger`
- `service.name`
- `service.version`
- `environment`
- `host`
- `process`
- `thread`

### HTTP/API fields
- `request_id`
- `trace_id`
- `span_id`
- `method`
- `route`
- `status_code`
- `duration_ms`
- `client_ip` (policy permitting)
- `user_id` or pseudonymous equivalent
- `tenant_id`

### Queue/job fields
- `job_id`
- `task_id`
- `attempt`
- `queue_name`
- `message_id`
- `duration_ms`
- `outcome`

### Dependency fields
- `dependency`
- `operation`
- `timeout_ms`
- `retryable`
- `attempt`
- `error_code`

### Exception fields
- `error_type`
- `error_code`
- `exception`
- `stack`
- `retryable`

---

## 36. OpenTelemetry-aligned thinking

Even if you do not emit native OpenTelemetry logs directly, you should think in a way that maps cleanly to modern telemetry systems.

### Helpful concepts
- `service.name` as a stable identity for the service
- `trace_id` / `span_id` for correlation
- structured `attributes`
- severity text and severity number
- separate resource metadata from event fields

### Why this matters
It keeps your logs portable across:
- vendors
- languages
- storage backends
- collectors
- future migrations

### Collector-based architectures
A collector can:
- batch
- retry
- enrich
- transform
- filter sensitive data
- route to multiple destinations

That keeps applications simpler and less coupled to vendors.

---

## 37. Operational playbook patterns

### Raise verbosity surgically
Do not set everything to DEBUG. Prefer:
- one logger namespace
- one service instance
- one incident window
- one route or component if your tooling supports it

### Log summaries at boundaries
Good boundaries:
- request complete
- background job complete
- sync cycle complete
- batch ingestion complete

These are high-value INFO logs.

### Emit one primary error per failed operation
A typical pattern:
- DEBUG from deep internals if needed
- one WARNING for retry
- one ERROR when the operation ultimately fails

### Use event names for recurring problems
Example:
- `db.connection.retrying`
- `db.connection.failed`
- `queue.message.poisoned`
- `auth.token.invalid`
- `cache.fallback.activated`

This dramatically improves queryability.

---

## 38. Production checklist for Python services

Use this as a review checklist.

### Configuration
- [ ] logging is configured exactly once at startup
- [ ] `disable_existing_loggers` is set intentionally
- [ ] propagation is understood and tested
- [ ] handlers are not attached redundantly

### Output format
- [ ] logs are structured in production
- [ ] timestamps are UTC and precise enough
- [ ] event names are stable
- [ ] important fields have consistent names

### Context
- [ ] request/job correlation is automatic
- [ ] trace IDs and span IDs are present where applicable
- [ ] service/environment/version metadata is present

### Safety
- [ ] secrets are redacted
- [ ] PII policy is documented and enforced
- [ ] untrusted input is sanitized against log injection
- [ ] log access is restricted

### Performance
- [ ] slow sinks do not block hot paths unnecessarily
- [ ] queue/buffering behavior is understood
- [ ] noisy events are sampled or rate-limited where appropriate
- [ ] log volume is budgeted

### Reliability
- [ ] shutdown flushes handlers/listeners
- [ ] multiprocess logging strategy is safe
- [ ] rotation/retention is intentional if using files
- [ ] sink outages do not accidentally take down the service

### Developer experience
- [ ] local dev format is readable
- [ ] production format is machine-parseable
- [ ] wrapper functions use `stacklevel` where needed
- [ ] tests verify critical logging behavior

---

## 39. Common Python mistakes and the correct fix

### Mistake: calling `basicConfig()` in library code
**Fix:** only applications configure logging; libraries use named loggers and optionally `NullHandler`.

### Mistake: attaching handlers to both module logger and root
**Fix:** attach to one place only, or set `propagate = False` intentionally.

### Mistake: using f-strings for all log messages
**Fix:** use lazy `%`-style args for normal logging calls; keep structured fields in `extra`.

### Mistake: writing from many processes to one file
**Fix:** use stdout, a queue, a socket listener, or a collector.

### Mistake: logging the same exception three times
**Fix:** log once at the boundary that has the best context and owns the failure outcome.

### Mistake: logging secrets in exception messages
**Fix:** sanitize messages and use redaction filters.

### Mistake: inventing ad hoc field names everywhere
**Fix:** document a schema and review new fields.

### Mistake: enabling DEBUG globally during incidents
**Fix:** scope verbosity increases to specific logger namespaces and time windows.

### Mistake: using log lines as the only source for alerts
**Fix:** use metrics for stable alerts; use logs for detail and investigation.

---

## 40. A minimal “good enough” production recipe

If you want a default answer for a modern Python service, use this:

1. `logging.getLogger(__name__)` in every module
2. one central `dictConfig()` at startup
3. `disable_existing_loggers=False`
4. JSON logs to stdout in production
5. text logs in development if preferred
6. `contextvars` for request/task metadata
7. automatic inclusion of `request_id`, `trace_id`, `span_id`, `service.name`, `service.version`, `environment`
8. `logger.exception(...)` in exception boundaries
9. queue-based emission if sink/formatting can block
10. no secrets, no raw PII, no redundant stack traces
11. stdout/collector architecture in containers
12. tests for schema, severity, and redaction

That baseline is already far better than what many systems run in production.

---

## 41. Short reference examples

### Module-level logger
```python
import logging
logger = logging.getLogger(__name__)
```

### Correct lazy formatting
```python
logger.info("processed %s records", count)
```

### Structured details
```python
logger.info(
    "batch completed",
    extra={"event_name": "batch.completed", "count": count, "duration_ms": 912}
)
```

### Exception boundary
```python
try:
    run_batch()
except Exception:
    logger.exception("batch failed", extra={"event_name": "batch.failed"})
    raise
```

### Library `NullHandler`
```python
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
```

### Capture warnings
```python
import logging
logging.captureWarnings(True)
```

### Logging helper with caller preservation
```python
def log_validation_error(logger, field):
    logger.warning("validation failed for field %s", field, stacklevel=2)
```

---

## 42. Final guidance

Production-grade logging is not mainly about calling `logger.info()`.  
It is about designing an **event model**, a **schema**, a **severity policy**, a **context propagation strategy**, a **safe transport pipeline**, and a **governance model** for privacy, retention, and reliability.

For Python specifically, the standard library logging stack is fully capable of production use when you understand:
- hierarchy and propagation
- centralized configuration
- handlers and formatters
- filters and adapters
- `contextvars`
- queue-based decoupling
- library vs application responsibilities

If your logs are:
- structured,
- correlated,
- safe,
- bounded in cost,
- and easy to query,

then they are doing real production work rather than merely printing text.

---

## 43. References and authoritative docs

These are the primary references to keep handy:

- Python `logging` reference: <https://docs.python.org/3/library/logging.html>
- Python Logging HOWTO: <https://docs.python.org/3/howto/logging.html>
- Python Logging Cookbook: <https://docs.python.org/3/howto/logging-cookbook.html>
- Python `logging.config`: <https://docs.python.org/3/library/logging.config.html>
- Python `logging.handlers`: <https://docs.python.org/3/library/logging.handlers.html>
- Python `unittest` (for `assertLogs`): <https://docs.python.org/3/library/unittest.html>
- OpenTelemetry logs concept docs: <https://opentelemetry.io/docs/concepts/signals/logs/>
- OpenTelemetry logs specification: <https://opentelemetry.io/docs/specs/otel/logs/>
- OpenTelemetry logs data model: <https://opentelemetry.io/docs/specs/otel/logs/data-model/>
- OpenTelemetry context propagation: <https://opentelemetry.io/docs/concepts/context-propagation/>
- OpenTelemetry resource semantic conventions: <https://opentelemetry.io/docs/specs/semconv/resource/>
- OpenTelemetry service semantic conventions: <https://opentelemetry.io/docs/specs/semconv/resource/service/>
- OpenTelemetry Collector: <https://opentelemetry.io/docs/collector/>
- OpenTelemetry SDK environment variables: <https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/>
- OWASP Logging Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html>
- Twelve-Factor App, logs: <https://12factor.net/logs>
