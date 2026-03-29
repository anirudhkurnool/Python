# Polars (Python) — Comprehensive Revision Guide

_Last reviewed against the official Polars user guide and Python API reference on 2026-03-29._

This file is a **concept-first revision guide** for the Python Polars library. It is meant to cover the important mental models, APIs, and performance rules you should know for real work and interviews. It is intentionally broader than a cheat sheet, but it is still a guide: for parameter-level edge cases, keep the official API reference nearby.

---

## 1) What Polars is

Polars is a **columnar DataFrame library** built in Rust, with Python bindings. Its design centers on:

- **Expressions instead of row-wise Python code**
- **Strict schemas and explicit dtypes**
- **Parallel execution**
- **Lazy query planning and optimization**
- **Fast IO**, especially with columnar formats like Parquet
- **Arrow interoperability**

### Core mental model

If you understand these five objects, you understand most of Polars:

- **`Series`**: one typed column
- **`DataFrame`**: a collection of named `Series`
- **`Expr`**: a column expression; the building block of almost everything
- **`LazyFrame`**: a deferred query plan that executes when collected
- **`SQLContext`**: SQL interface over `DataFrame`/`LazyFrame`

Polars is not “pandas with different syntax”. The most important shift is:

> **Think in expressions over columns, not loops over rows.**

---

## 2) The execution model: eager vs lazy

### Eager mode

You work with a `DataFrame`, and operations execute immediately.

Typical entry points:

- `pl.DataFrame(...)`
- `pl.read_csv(...)`
- `pl.read_parquet(...)`
- `pl.read_json(...)`
- `pl.read_database(...)`

Use eager mode when:

- the data is small enough to fit comfortably in memory
- you need quick exploratory work
- the operation is only available eagerly (for example, pivot-style reshaping)

### Lazy mode

You work with a `LazyFrame`, and Polars builds a query plan first.
Execution happens only when you call something like:

- `.collect()`
- `.collect(engine="streaming")`
- `.explain()` / `.show_graph()` (inspection, not full materialization)

Typical entry points:

- `pl.scan_csv(...)`
- `pl.scan_parquet(...)`
- `pl.scan_ndjson(...)`
- `df.lazy()`

Use lazy mode when:

- data is large
- you want the optimizer to reorder / push down work
- you care about performance and memory usage
- you are reading from files or cloud storage

### The most important rule

> **Prefer `scan_*` + lazy pipelines over `read_*` + eager pipelines for analytics workloads.**

This lets Polars optimize the whole query before executing it.

---

## 3) Why lazy mode matters

When you use the lazy API, Polars can apply optimizer passes such as:

- **predicate pushdown**: move filters closer to the scan
- **projection pushdown**: load only needed columns
- **slice pushdown**: avoid scanning more rows than needed
- **common subplan elimination**: reuse repeated subtrees/scans where possible
- **expression simplification**: constant folding and similar rewrites
- **join ordering**: reduce memory pressure
- **type coercion**: adjust types so expressions can run efficiently
- **cardinality estimation**: help choose efficient aggregation strategies

### Query-plan inspection

For lazy queries, inspect plans with:

- `.explain()`
- `.show_graph()`

Get used to reading plans. This is how you verify:

- filters are pushed down
- only necessary columns are read
- expensive operations appear where you expect

### Streaming execution

Many lazy queries can run with:

```python
result = query.collect(engine="streaming")
```

This allows Polars to process data in batches instead of requiring the whole result to fit in memory at once.

Important caveats:

- not every operation is streamable
- unsupported parts can fall back to the in-memory engine
- streaming is usually relevant only in lazy mode

### Reusing `LazyFrame`s

A `LazyFrame` is a **query plan**, not a materialized cached object. If you branch from the same `LazyFrame` into multiple downstream queries, Polars may recompute work rather than cache everything automatically.

Also remember:

- operations like `group_by` do **not** preserve row order unless you ask for it
- if row order matters, use the relevant `maintain_order=True` option where supported

---

## 4) Core data structures

## `Series`

A `Series` is a 1D homogeneous array with one dtype.

```python
s = pl.Series("x", [1, 2, 3])
```

Important notes:

- all values in a series share one dtype
- dtype can be inferred or specified explicitly
- a `Series` is often used inside expressions or for standalone column operations

## `DataFrame`

A `DataFrame` is a 2D table of uniquely named series.

```python
df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
```

Important properties / metadata:

- `df.columns`
- `df.dtypes`
- `df.schema`
- `df.shape`
- `df.height`
- `df.width`

## `LazyFrame`

A `LazyFrame` represents a deferred query.

```python
lf = df.lazy()
```

or better:

```python
lf = pl.scan_parquet("data.parquet")
```

### Schema awareness

Polars wants to know schemas during lazy planning.
That has consequences:

- type errors can be caught before execution
- some operations whose output schema is unknowable in advance are not lazy-friendly
- the canonical example is **pivot**: output columns depend on data values, so pivot is usually eager-only in practice

---

## 5) Expressions: the heart of Polars

An expression is a deferred description of a column computation.

```python
(pl.col("weight") / (pl.col("height") ** 2)).alias("bmi")
```

Expressions are composable. They can be saved, reused, nested, and passed into many APIs.

### Core expression constructors

- `pl.col("name")` — select a column
- `pl.lit(value)` — literal value
- `pl.all()` — all columns
- `pl.exclude(...)` — all except some columns
- `pl.when(...).then(...).otherwise(...)` — conditional logic
- `.alias("new_name")` — rename expression output
- `.cast(dtype)` — convert dtype
- `.is_null()`, `.is_nan()`, `.is_in(...)`, etc. — predicates

### Why expressions matter

Expressions let Polars:

- optimize work globally
- parallelize independent parts
- keep computation in Rust/native code
- avoid Python loops and GIL-heavy row iteration

---

## 6) Expression contexts

The same expression can behave differently depending on where it is used.
The four most important contexts are:

- `select`
- `with_columns`
- `filter`
- `group_by(...).agg(...)`

## `select`

Used to create a new frame from expressions.

```python
df.select(
    pl.col("a"),
    (pl.col("b") * 2).alias("b2"),
)
```

Use it for:

- projection
- derived columns only
- aggregation results
- standalone expression outputs

## `with_columns`

Adds or replaces columns while keeping the frame shape.

```python
df.with_columns(
    (pl.col("a") + pl.col("b")).alias("c")
)
```

Use it for:

- feature engineering
- dtype conversion
- replacing existing columns

### Key difference between `select` and `with_columns`

- In `with_columns`, produced columns must align to the original row count.
- In `select`, expressions only need to align with each other.

## `filter`

Filters rows using boolean expressions.

```python
df.filter(pl.col("score") > 90)
```

Use `&`, `|`, and `~` for boolean logic.

## `group_by(...).agg(...)`

Aggregation context.

```python
df.group_by("team").agg(
    pl.col("points").mean().alias("avg_points"),
    pl.len().alias("n"),
)
```

In group contexts, expressions can reduce each group to:

- scalars (sum, mean, count, min, max)
- lists (collect group members)
- more complex derived values

---

## 7) Selectors and dtype-driven column selection

Polars has a powerful idea beyond `pl.col("name")`: **selectors**.
These let you target columns by schema properties instead of hardcoding names.

Typical pattern:

```python
import polars.selectors as cs

# all numeric columns
df.select(cs.numeric())
```

Why this matters:

- robust pipelines when schemas evolve
- easy “all numeric”, “all string”, “all temporal” style transformations
- cleaner code in wide tables

Common patterns:

- numeric-only transformations
- string cleanup across all string columns
- excluding identifier columns while transforming everything else

Related idea: **dtype expressions / datatype-aware operations** in lazy planning.
The big picture is that Polars can reason about types as part of the plan.

---

## 8) Data types you should know

Polars is strongly typed. This is central to both correctness and performance.

### Primitive/common dtypes

- `Int8`, `Int16`, `Int32`, `Int64`
- `UInt8`, `UInt16`, `UInt32`, `UInt64`
- `Float32`, `Float64`
- `Boolean`
- `String`
- `Binary`

### Temporal dtypes

- `Date`
- `Datetime`
- `Duration`
- `Time`

### Nested / composite dtypes

- `List`
- `Array`
- `Struct`

### Categorical dtypes

- `Categorical`
- `Enum`

### Other useful concepts

- `Null`
- decimal/fixed-precision numeric support where appropriate

### Revision rule

> In Polars, dtypes are not cosmetic. They directly affect correctness, available operations, memory use, and speed.

---

## 9) Nulls, NaNs, and missing data

This is one of the most important Polars topics.

## `null`

In Polars, **missing data is represented by `null` across all dtypes**.
This is different from pandas-style dtype-dependent missingness.

Examples:

- integer column with missing values → still conceptually missing via `null`
- string column with missing values → `null`
- date column with missing values → `null`

## `NaN`

`NaN` is **not** the same thing as `null`.
It is a valid floating-point value.

Consequences:

- `null_count()` counts `null`, not `NaN`
- `fill_null(...)` handles `null`, not `NaN`
- `fill_nan(...)` handles `NaN`
- many numeric aggregations skip `null`, but `NaN` often propagates

### Important APIs

- `is_null()` / `is_not_null()`
- `null_count()`
- `fill_null(...)`
- `interpolate()`
- `is_nan()` / `fill_nan(...)`

### Fill strategies to remember

- fill with a literal
- fill with another expression
- forward fill / backward fill
- interpolation

### Performance note

Polars tracks null metadata efficiently via a validity bitmap, so some null-related operations are cheap.

---

## 10) Basic column operations

These are the everyday expression patterns.

### Arithmetic

```python
df.select(
    (pl.col("x") + 1).alias("x_plus_1"),
    (pl.col("a") * pl.col("b")).alias("ab"),
)
```

### Comparisons

```python
pl.col("x") > 10
pl.col("name") == "alice"
pl.col("country").is_in(["IN", "US"])
```

### Boolean logic

```python
(pl.col("x") > 0) & (pl.col("y") < 5)
(pl.col("flag") | pl.col("other_flag"))
~pl.col("bad")
```

### Conditionals

```python
pl.when(pl.col("score") >= 90)
  .then(pl.lit("A"))
  .when(pl.col("score") >= 75)
  .then(pl.lit("B"))
  .otherwise(pl.lit("C"))
```

### Counting / uniqueness

Important concepts:

- row count vs non-null count vs number of groups
- `n_unique()`
- `unique()`
- distinct values inside groups

### Sorting

- `.sort(...)`
- sort by one or multiple columns
- ascending / descending
- null ordering when relevant

---

## 11) Expression expansion

Expression expansion means writing one compact expression that expands across multiple columns.

Examples of the idea:

- transform all numeric columns
- cast multiple columns at once
- suffix/prefix multiple output names
- use wildcards / selectors to broadcast logic across a set of columns

This is one of the reasons Polars code can stay short even on very wide tables.

---

## 12) Core DataFrame operations

## Selecting columns

```python
df.select("a", "b")
```

## Adding/replacing columns

```python
df.with_columns((pl.col("a") + 1).alias("a"))
```

## Dropping columns

```python
df.drop("tmp")
```

## Renaming columns

```python
df.rename({"old": "new"})
```

## Casting columns

```python
df.cast({"x": pl.Float64, "y": pl.Date})
```

## Filtering rows

```python
df.filter(pl.col("x") > 0)
```

## Slicing / limiting

- `.head(n)`
- `.tail(n)`
- `.slice(offset, length)`
- `.limit(n)`

## Uniqueness / deduplication

- `.unique(...)`
- subset-based deduplication
- keep strategy / order caveats

## Sampling

- `.sample(...)`

## Row index

Polars does **not** have a pandas-style special index by default.
If you need one, add it explicitly.

Typical pattern:

```python
df = df.with_row_index()
```

Treat this as a normal column, not as a magical axis index.

---

## 13) Grouping and aggregation

Grouping is a major Polars strength.

### Canonical pattern

```python
df.group_by("key").agg(
    pl.col("value").sum(),
    pl.col("value").mean(),
    pl.len().alias("n"),
)
```

### What to know

- groups are formed by one or more keys
- aggregation expressions run per group
- outputs can be scalar or list-like
- grouping does not imply stable row order unless you request it where supported

### Common aggregation expressions

- `sum`
- `mean`
- `median`
- `min`
- `max`
- `count` / `len`
- `first`
- `last`
- `n_unique`
- list collection patterns

### Group-wise feature engineering

You often mix:

- `group_by(...).agg(...)` for reduced outputs
- window functions (`.over(...)`) for same-row-count outputs

That distinction is critical.

---

## 14) Window functions

Window functions let you compute group-aware values **without reducing row count**.

Typical pattern:

```python
df.with_columns(
    pl.col("sales").rank(descending=True).over("store").alias("rank_in_store")
)
```

### Mental model

- `group_by(...).agg(...)` → one row per group (usually)
- `expr.over(...)` → value mapped back to original rows

### Common window patterns

- rank within group
- group mean / max attached to every row
- percent-of-group calculations
- cumulative calculations within partitions

### Important idea

Window functions are often the cleanest replacement for awkward self-joins.

---

## 15) Horizontal operations and folds

Polars is primarily column-oriented, but sometimes you need **row-wise across selected columns** logic.

Built-in horizontal helpers include ideas like:

- sum across columns
- mean across columns
- min/max across columns

For custom logic, use a **fold**.

Conceptually:

```python
pl.fold(acc=..., function=..., exprs=[...])
```

Use folds when you need:

- a custom row-wise reduction across multiple columns
- logic more general than `sum_horizontal` / `mean_horizontal`

Revision rule:

> Prefer built-in horizontal ops when available; use folds for custom row-wise reductions.

---

## 16) Strings

The `str` namespace is extensive and very important in real workloads.

Common ideas:

- lowercase / uppercase / strip
- contains / starts_with / ends_with
- replace / replace_all
- split
- regex extraction
- slicing substrings
- parsing dates from strings

Typical style:

```python
df.with_columns(
    pl.col("text").str.to_lowercase(),
    pl.col("email").str.contains("@"),
)
```

### Important mindset

String work in Polars should still be expression-based and vectorized.
Avoid Python loops and `apply`-style patterns for text cleanup when a `str` expression exists.

---

## 17) Lists and arrays

Polars has two homogeneous container dtypes that people often confuse:

- **`List`**: variable-length 1D container per row
- **`Array`**: fixed-shape container per row

### When to use `List`

Use `List` when row values can have different lengths.
Examples:

- token lists
- tags
- variable-length event sequences

### When to use `Array`

Use `Array` when shape is fixed.
Examples:

- a fixed-length embedding vector
- RGB triplets
- fixed-size coordinate tuples

### Key operations

- `explode` — turn list elements into rows
- `list.*` namespace — list operations
- `arr.*` namespace — array operations
- `list.eval(...)` — run expressions on list elements

### Revision rule

> `List` is flexible; `Array` is more structured and fixed-size.

---

## 18) Structs

`Struct` is a composite dtype containing multiple named fields inside one column.

This matters because Polars expressions operate on series and return series. A struct lets one expression carry multiple fields.

### Where structs show up

- `value_counts()` outputs a struct-like result
- dictionary-like Python inputs can become `Struct`
- multi-column logic sometimes uses `pl.struct(...)`

### Key operations

- `pl.struct(...)`
- `.struct.field("name")`
- `.unnest(...)`

### Why `Struct` matters

It is the clean native way to:

- bundle multiple columns together
- pass multiple columns into one operation
- return multiple fields from one expression result

---

## 19) Categorical data: `Enum` vs `Categorical`

This is a very important Polars-specific concept.

## `Enum`

Use when the set of categories is **known and fixed up front**.

Benefits:

- ordered categorical semantics
- validation against allowed values
- strong control over domain

## `Categorical`

Use when categories are not known ahead of time or may evolve.

### Rule of thumb

> Prefer `Enum` when you can, `Categorical` when you must.

### String cache concept

For categorical workflows across multiple columns/dataframes, the **global string cache** can matter so category encodings remain compatible.

This is especially relevant when joining or concatenating categorical columns created in different contexts.

---

## 20) Joins

Joins are a major part of Polars and broader than many quick summaries suggest.

### Equi joins (`join`)

Common `how=` values:

- `"inner"`
- `"left"`
- `"right"`
- `"full"`
- `"semi"`
- `"anti"`
- `"cross"`

### What each means

- **inner**: keep matches on both sides
- **left**: keep all left rows, fill right with nulls when unmatched
- **right**: mirror of left
- **full**: keep all rows from both sides
- **semi**: keep left rows that have a match on the right
- **anti**: keep left rows with no match on the right
- **cross**: Cartesian product

### Non-equi joins

Polars also supports **non-equi joins**, where the match condition is not equality.
This is conceptually different from normal key joins.

### Asof joins

Asof join is for nearest-key matching, usually in time-series work.
Think:

- “attach the latest known value at or before this timestamp”

### Join revision checklist

Always check:

- key column dtypes match
- key semantics are correct
- duplicate keys produce expected multiplicity
- suffixes / overlapping columns are handled intentionally
- row order assumptions are justified

---

## 21) Concatenation

Polars supports multiple concatenation strategies.

### Main ideas

- **vertical**: stack rows
- **horizontal**: combine columns side by side
- **diagonal**: union mismatched schemas, filling missing parts with nulls

Use concatenation when you are combining same-shape or compatible dataframes.
Use joins when you are matching rows by keys.

---

## 22) Reshaping: pivot, unpivot, explode, unnest

## Pivot

Wide-from-long reshaping.

Use when:

- row values should become column names
- you want spreadsheet-like cross-tab output

Important concept:

- pivot output schema depends on data values
- because of that, pivot is not naturally suited to fully lazy planning
- a common pattern is lazy pipeline → `.collect()` → `pivot(...)` → maybe `.lazy()` again

## Unpivot

Long-from-wide reshaping.

Use when:

- multiple measure columns should become rows
- you want tidy long format for grouping/plotting/model input

## Explode

Turns list-like elements into multiple rows.

## Unnest

Expands `Struct` fields into separate columns.

Revision rule:

> `explode` is for nested elements becoming rows; `unnest` is for struct fields becoming columns.

---

## 23) Time series and temporal data

Polars has strong first-class temporal support.

### Main temporal dtypes

- `Date`
- `Datetime`
- `Duration`
- `Time`

### Parsing

You will commonly use:

- `try_parse_dates=True` on CSV read
- `str.to_date(...)`
- `str.to_datetime(...)`
- casting where appropriate

### `dt` namespace

Use `.dt.*` for date/time features and operations.
Think:

- year/month/day/hour extraction
- truncation/rounding
- timezone conversion
- duration logic

### Time-based filtering

Temporal filtering works like other filters, but uses Python `date`, `datetime`, and `timedelta` objects naturally.

---

## 24) Dynamic and rolling time windows

These are crucial for serious time-series work.

## `group_by_dynamic`

Use for fixed calendar/window grouping such as:

- daily
- weekly
- monthly
- yearly
- custom durations like `"15m"`, `"1h"`, `"1d"`, etc. where appropriate

Examples of use cases:

- monthly sales totals
- annual averages
- per-hour aggregation

### Critical requirement

For dynamic time grouping, the time column generally needs to be **sorted correctly** for results to make sense.

## Rolling windows / rolling grouping

Use rolling logic when each row/group considers a moving historical window rather than fixed aligned buckets.

Think:

- trailing 7-day metrics
- rolling averages
- rolling counts by entity

### Resampling / upsampling

Polars also supports upsampling-style workflows and filling newly introduced nulls, often with forward fill or interpolation.

---

## 25) Time zones

Time zones are their own topic.

### Key rules

- a `Datetime` column can have **one timezone for the whole column**
- do not think of a single column as holding multiple independent time zones
- prefer named zones like `"Asia/Kolkata"`, `"Europe/Brussels"`, `"UTC"`
- avoid fixed offsets like `+02:00` for serious timezone handling

### Important methods

- `dt.replace_time_zone(...)` — assign/change/unset timezone interpretation
- `dt.convert_time_zone(...)` — convert actual timestamps to another zone

### Common confusion

- **replace** changes timezone assignment semantics
- **convert** changes representation to another zone while preserving the underlying instant

---

## 26) SQL interface

Polars has a SQL interface through `SQLContext`.

### Important concepts

- register `DataFrame`s / `LazyFrame`s as tables
- run SQL queries against them
- SQL is translated into Polars expressions and executed by Polars
- execution is lazy by default

### Typical workflow

```python
ctx = pl.SQLContext(df=my_df)
out = ctx.execute("SELECT ...")
```

You can then either:

- collect lazily
- request eager execution when desired

### Why this matters

SQL is not a separate engine bolted on top; it is another way to express Polars-native computation.

---

## 27) Input / output (IO)

IO is broader in Polars than many people remember.

### Core file formats

- CSV
- Parquet
- JSON
- NDJSON / newline-delimited JSON
- Excel / ODS
- Feather / IPC
- Avro

### Data sources / integrations

- databases
- cloud storage (S3 / Azure / GCS style workflows)
- hive-style partitioned layouts
- multiple files/globs
- Google BigQuery
- Hugging Face paths

### Core rule: `read_*` vs `scan_*`

- `read_*` → eager materialization
- `scan_*` → lazy scan and optimizer-friendly pipeline

### Practical storage advice

- prefer **Parquet** for analytics whenever possible
- CSV is ubiquitous but slower and less typed
- NDJSON is often better than standard JSON for line-oriented ingestion
- Excel works, but it is not a high-performance analytics format

---

## 28) Databases and external data

Polars can ingest from databases using both connection objects and URI-based approaches.

Important idea:

- when possible, keep work close to the source and keep schemas explicit
- then continue in Polars expressions/lazy pipelines

Also remember that converting external sources has cost. For example, converting a pandas object backed by NumPy can be more expensive than converting Arrow-backed data.

---

## 29) NumPy interoperability

Polars works with NumPy ufuncs and generalized ufuncs in many cases.

### What to know

- many NumPy ufuncs can be used directly on Polars expressions/series
- this can be convenient when Polars does not already provide the exact native expression

### Caveat

NumPy does not understand Polars’ null bitmap model the same way Polars does.
So generalized ufunc behavior around missing data requires care.

If you explicitly convert to NumPy:

- missing values are typically represented as `np.nan` where needed
- you leave the native Polars execution model

Revision rule:

> Use native Polars expressions first, NumPy second.

---

## 30) User-defined functions (UDFs)

Polars supports Python UDF patterns, but they should be treated as a fallback.

### Two important APIs

- `map_elements(...)` — Python function per element
- `map_batches(...)` — Python function per whole `Series` batch

### What to remember

- `map_elements` is convenient but often slow
- `map_batches` can be better when the function naturally operates on arrays/series
- native expressions are usually faster and better optimized

### Best practice

> Do not reach for Python UDFs first. Reach for expressions first.

If you truly need custom high-performance behavior, consider plugins.

---

## 31) Plugins and extending Polars

Polars can be extended with:

- **expression plugins**
- **IO plugins**

### Expression plugins

These are the preferred high-performance extension path for custom expression logic.

Why they matter:

- run near native speed
- integrate with Polars optimization and parallelism
- avoid Python/GIL bottlenecks

### IO plugins

Use when you want to register a custom data source while still benefiting from optimizer features like:

- projection pushdown
- predicate pushdown
- early stopping
- streaming support

This is advanced, but it is part of the real Polars conceptual surface area.

---

## 32) Row-wise thinking vs column-wise thinking

This is one of the most important mindset changes.

### Avoid as defaults

- Python `for` loops over rows
- `rows()` / `row()` for normal data processing
- per-row Python `apply` patterns

### Prefer instead

- expressions
- window functions
- group aggregations
- joins
- folds / horizontal native ops
- list/struct expressions for nested logic

Polars is fastest when you stay in its expression engine.

---

## 33) Common anti-patterns

### 1. Reading eagerly when you should scan lazily

Bad default:

```python
df = pl.read_csv("big.csv")
```

Better analytics default:

```python
lf = pl.scan_csv("big.csv")
```

### 2. Using Python UDFs before checking native expressions

Bad default:

- `map_elements` for simple string/date/numeric work

Better:

- use `str`, `dt`, arithmetic, conditionals, windows, list/struct ops

### 3. Iterating rows for transformations

Bad:

- converting frame to Python lists/dicts and processing manually

Better:

- expression pipelines

### 4. Confusing `null` and `NaN`

You must know which one you are dealing with.

### 5. Assuming pandas-style index semantics

Polars has no magical hidden index.
If you need one, create a normal column explicitly.

### 6. Forgetting sort requirements in temporal workflows

Dynamic grouping / asof-style logic often depends on correct sort order.

### 7. Using pivot too early in a lazy pipeline

Since pivot changes schema based on data, it is often best done after `collect()`.

### 8. Assuming a `LazyFrame` is a cache

It is a plan, not guaranteed cached materialized data.

---

## 34) Practical performance rules

Memorize these.

1. **Use lazy + scan for large workflows.**
2. **Filter early; select only columns you need.**
3. **Prefer Parquet over CSV for repeated analytics.**
4. **Prefer native expressions over Python UDFs.**
5. **Keep dtypes explicit where inference may be wrong or unstable.**
6. **Use window functions instead of self-joins when appropriate.**
7. **Be careful with row order assumptions.**
8. **Inspect plans with `explain()` / `show_graph()` when performance matters.**
9. **Use streaming collection for larger-than-memory-friendly pipelines when applicable.**
10. **Prefer `Enum` over `Categorical` when categories are known up front.**
11. **Avoid materializing to Python objects unless necessary.**
12. **Treat missing data deliberately: `null` vs `NaN`.**

---

## 35) Multiprocessing note

Polars is already multithreaded.

### What to remember

- manual Python multiprocessing often does **not** improve native Polars workloads
- on Unix-like systems, avoid `fork` with Polars
- prefer **`spawn`** (or `forkserver`) if you must use multiprocessing

Why:

- Polars is multithreaded
- `fork` and multithreaded libraries are a bad mix and can deadlock

This is a niche topic until it breaks your code; then it becomes very important.

---

## 36) Testing, config, exceptions, metadata

These are not core transformations, but they are important parts of working seriously with Polars.

### Testing

Use `polars.testing` helpers such as:

- `assert_frame_equal`
- `assert_series_equal`
- schema assertions

### Config

Polars has configurable display/formatting behavior and config context-manager patterns.
Useful for notebooks, debugging, and controlled output.

### Exceptions

Polars has a typed exception hierarchy. Learn to read these carefully, especially for:

- invalid operations due to dtype mismatch
- schema mismatches
- missing columns
- shape errors

### Metadata helpers

Useful environment/debug tools include ideas like:

- version info
- thread pool size
- build information

---

## 37) A good default workflow

Here is a strong default workflow for real projects:

1. **Scan lazily** from Parquet/CSV/database.
2. **Inspect schema** early.
3. **Cast dtypes explicitly** where needed.
4. **Filter and project early**.
5. **Engineer features with `with_columns`**.
6. **Use `group_by` / windows / joins / reshaping** as needed.
7. **Inspect the query plan** if performance matters.
8. **Collect at the end**.
9. **Persist to Parquet** for downstream steps.
10. **Write tests** around schemas and key outputs.

---

## 38) Mini concept map

If you want the shortest possible “how Polars fits together” map, it is this:

- **Data is typed** → schema matters
- **Work is expressed as expressions** → not row loops
- **Expressions run in contexts** → `select`, `with_columns`, `filter`, `group_by`
- **Lazy mode builds a query plan** → optimizer rewrites it
- **Execution happens at `collect()`**
- **Nested types are first-class** → `List`, `Array`, `Struct`
- **Time series is first-class** → dynamic windows, rolling windows, asof joins, time zones
- **IO is part of the performance story** → prefer `scan_*` and Parquet
- **Python UDFs are fallback tools** → native expressions/plugins are better

---

## 39) Final revision checklist

You should be comfortable explaining or using all of the following:

### Foundation

- [ ] `Series`, `DataFrame`, `LazyFrame`, `Expr`, `SQLContext`
- [ ] strict schema / dtype mindset
- [ ] eager vs lazy
- [ ] `read_*` vs `scan_*`

### Expressions

- [ ] `pl.col`, `pl.lit`, `pl.all`
- [ ] `select`, `with_columns`, `filter`, `group_by().agg()`
- [ ] `when/then/otherwise`
- [ ] aliasing, casting, expression composition
- [ ] selectors and schema-driven targeting

### Data types

- [ ] numeric / string / boolean
- [ ] `Date`, `Datetime`, `Duration`, `Time`
- [ ] `List`, `Array`, `Struct`
- [ ] `Enum` vs `Categorical`
- [ ] `null` vs `NaN`

### Transformations

- [ ] sorting, unique, slicing
- [ ] joins: inner/left/right/full/semi/anti/cross
- [ ] non-equi join and asof join concepts
- [ ] concat: vertical/horizontal/diagonal
- [ ] pivot vs unpivot
- [ ] explode vs unnest

### Analytics

- [ ] group aggregation
- [ ] window functions with `.over(...)`
- [ ] horizontal reductions / folds
- [ ] string namespace
- [ ] list/array/struct namespaces

### Time series

- [ ] parsing temporal data
- [ ] temporal filtering
- [ ] `group_by_dynamic`
- [ ] rolling windows
- [ ] upsampling / resampling concepts
- [ ] timezone conversion vs replacement

### Performance / production

- [ ] lazy optimizer basics
- [ ] predicate/projection pushdown
- [ ] streaming collection
- [ ] query-plan inspection
- [ ] avoid row-wise Python logic
- [ ] prefer Parquet
- [ ] multiprocessing: use `spawn`, not `fork`
- [ ] testing/config/metadata basics

---

## 40) Official source map

Primary references used to build this guide:

- Polars user guide index: https://docs.pola.rs/
- Python API reference: https://docs.pola.rs/api/python/stable/reference/
- Concepts: https://docs.pola.rs/user-guide/concepts/
- Data types and structures: https://docs.pola.rs/user-guide/concepts/data-types-and-structures/
- Expressions and contexts: https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/
- Streaming: https://docs.pola.rs/user-guide/concepts/streaming/
- Expressions section: https://docs.pola.rs/user-guide/expressions/
- Basic operations: https://docs.pola.rs/user-guide/expressions/basic-operations/
- Lists and arrays: https://docs.pola.rs/user-guide/expressions/lists-and-arrays/
- Categorical data and enums: https://docs.pola.rs/user-guide/expressions/categorical-data-and-enums/
- Structs: https://docs.pola.rs/user-guide/expressions/structs/
- Missing data: https://docs.pola.rs/user-guide/expressions/missing-data/
- Window functions: https://docs.pola.rs/user-guide/expressions/window-functions/
- Folds: https://docs.pola.rs/user-guide/expressions/folds/
- User-defined Python functions: https://docs.pola.rs/user-guide/expressions/user-defined-python-functions/
- Numpy functions: https://docs.pola.rs/user-guide/expressions/numpy-functions/
- Transformations: https://docs.pola.rs/user-guide/transformations/
- Joins: https://docs.pola.rs/user-guide/transformations/joins/
- IO: https://docs.pola.rs/user-guide/io/
- CSV: https://docs.pola.rs/user-guide/io/csv/
- Parquet: https://docs.pola.rs/user-guide/io/parquet/
- JSON: https://docs.pola.rs/user-guide/io/json/
- Excel: https://docs.pola.rs/user-guide/io/excel/
- Database: https://docs.pola.rs/user-guide/io/database/
- Cloud storage: https://docs.pola.rs/user-guide/io/cloud-storage/
- SQL intro: https://docs.pola.rs/user-guide/sql/intro/
- Lazy API: https://docs.pola.rs/user-guide/lazy/
- Optimizations: https://docs.pola.rs/user-guide/lazy/optimizations/
- Schemas: https://docs.pola.rs/user-guide/lazy/schemas/
- Query plan: https://docs.pola.rs/user-guide/lazy/query-plan/
- Query execution: https://docs.pola.rs/user-guide/lazy/execution/
- Plugins: https://docs.pola.rs/user-guide/plugins/
- Expression plugins: https://docs.pola.rs/user-guide/plugins/expr_plugins/
- IO plugins: https://docs.pola.rs/user-guide/plugins/io_plugins/
- Multiprocessing: https://docs.pola.rs/user-guide/misc/multiprocessing/

