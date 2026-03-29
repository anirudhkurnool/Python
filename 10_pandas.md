
# Pandas (Python) — Complete Revision Notes

**Purpose:** This file is a comprehensive revision guide for the *important concepts* of pandas, organized from basics to advanced usage.  
**Scope:** It covers the conceptual model, core objects, indexing, data types, missing values, grouping, joins, reshaping, time series, I/O, performance, and major modern pandas behavior you should know for pandas 3.x.  
**Version note:** Written to match the official pandas 3.0.1 documentation era, so it reflects current Copy-on-Write behavior and the modern string-dtype direction.

---

## Table of Contents

1. [What pandas is](#1-what-pandas-is)
2. [Core data structures](#2-core-data-structures)
3. [Creating pandas objects](#3-creating-pandas-objects)
4. [Inspecting data](#4-inspecting-data)
5. [Indexing, selection, and assignment](#5-indexing-selection-and-assignment)
6. [Index objects and alignment](#6-index-objects-and-alignment)
7. [Copy-on-Write and mutation rules](#7-copy-on-write-and-mutation-rules)
8. [Data types in pandas](#8-data-types-in-pandas)
9. [Missing data](#9-missing-data)
10. [Core vectorized operations](#10-core-vectorized-operations)
11. [Descriptive statistics and summaries](#11-descriptive-statistics-and-summaries)
12. [Sorting, ranking, and ordering](#12-sorting-ranking-and-ordering)
13. [Working with text data](#13-working-with-text-data)
14. [Categorical data](#14-categorical-data)
15. [Date, time, timedelta, and time series](#15-date-time-timedelta-and-time-series)
16. [GroupBy: split-apply-combine](#16-groupby-split-apply-combine)
17. [Window operations](#17-window-operations)
18. [Combine, merge, join, concatenate, compare](#18-combine-merge-join-concatenate-compare)
19. [Reshaping and pivoting](#19-reshaping-and-pivoting)
20. [Apply, map, transform, agg, and UDFs](#20-apply-map-transform-agg-and-udfs)
21. [Expressions, query, eval, and pipe](#21-expressions-query-eval-and-pipe)
22. [Input / output (I/O)](#22-input--output-io)
23. [Visualization and styling](#23-visualization-and-styling)
24. [Nullable dtypes and Arrow / PyArrow](#24-nullable-dtypes-and-arrow--pyarrow)
25. [Duplicate labels](#25-duplicate-labels)
26. [Sparse data](#26-sparse-data)
27. [Performance and scaling](#27-performance-and-scaling)
28. [Common pitfalls and best practices](#28-common-pitfalls-and-best-practices)
29. [High-value methods to remember](#29-high-value-methods-to-remember)
30. [Typical pandas workflow](#30-typical-pandas-workflow)
31. [One-page mental model](#31-one-page-mental-model)

---

## 1. What pandas is

pandas is Python’s high-level library for **tabular**, **labeled**, and **time-series** data.

It is best thought of as:

- a layer above NumPy for labeled data
- a table-processing library similar in spirit to SQL, spreadsheets, and R data frames
- a time-series toolkit
- a data cleaning and transformation toolkit

### What pandas is good at

- reading tabular data from files and databases
- cleaning messy data
- selecting, filtering, and transforming columns/rows
- joining tables
- aggregating and summarizing
- handling dates and time series
- preparing data for modeling and visualization

### Core ideas

The most important ideas in pandas are:

- **labeled axes** (rows and columns have labels)
- **automatic alignment** by labels
- **vectorized operations** over entire columns/Series
- **rich missing-data handling**
- **split-apply-combine** through GroupBy
- **reshape / join / time-series** operations
- **dtype-aware behavior** (especially with nullable, categorical, datetime, and Arrow-backed types)

---

## 2. Core data structures

## `Series`

A `Series` is a **1-dimensional labeled array**.

- values + index
- similar to one column of a table
- supports arithmetic, indexing, aggregation, string methods, datetime methods, etc.

Example:

```python
import pandas as pd

s = pd.Series([10, 20, 30], index=["a", "b", "c"], name="score")
```

Key properties:

- `s.index`
- `s.values` or better `s.to_numpy()`
- `s.dtype`
- `s.name`
- `s.shape`, `s.size`

---

## `DataFrame`

A `DataFrame` is a **2-dimensional labeled tabular structure**.

- rows have an index
- columns have labels
- columns can have different dtypes

Example:

```python
df = pd.DataFrame({
    "name": ["A", "B", "C"],
    "age": [20, 21, 19],
    "score": [88.5, 91.0, 79.5]
})
```

Key properties:

- `df.index`
- `df.columns`
- `df.dtypes`
- `df.shape`
- `df.size`
- `df.ndim`
- `df.axes`

---

## `Index`

An `Index` stores axis labels.

Important facts:

- labels identify rows/columns
- many operations align by index labels automatically
- indexes are conceptually immutable
- labels can be strings, numbers, datetimes, tuples, etc.
- duplicate labels are allowed by default, but can be dangerous

Common index types:

- `RangeIndex`
- `Index`
- `DatetimeIndex`
- `TimedeltaIndex`
- `PeriodIndex`
- `CategoricalIndex`
- `MultiIndex`

---

## `MultiIndex`

A `MultiIndex` is a **hierarchical index**: multiple levels on one axis.

Useful when data naturally has nested labels, such as:

- country → city
- year → month
- category → subcategory

Example:

```python
df = df.set_index(["country", "city"])
```

It allows high-dimensional style operations on 1D/2D structures.

Common MultiIndex operations:

```python
df.xs("India", level="country")
df.swaplevel()
df.reorder_levels([1, 0])
df.sort_index()
```

With hierarchical indexes, sorting often matters for efficient slicing and predictable behavior.

---

## 3. Creating pandas objects

### From Python objects

```python
pd.Series([1, 2, 3])
pd.Series({"a": 1, "b": 2})

pd.DataFrame({"A": [1, 2], "B": [3, 4]})
pd.DataFrame([[1, 3], [2, 4]], columns=["A", "B"])
pd.DataFrame.from_dict({"A": [1, 2], "B": [3, 4]})
pd.DataFrame.from_records([{"A": 1, "B": 3}, {"A": 2, "B": 4}])
```

### From NumPy arrays

```python
import numpy as np
pd.Series(np.array([1, 2, 3]))
pd.DataFrame(np.arange(6).reshape(3, 2), columns=["A", "B"])
```

### From existing pandas objects

```python
pd.Series(existing_series)
pd.DataFrame(existing_dataframe)
```

### Important constructor arguments

- `index=`
- `columns=`
- `dtype=`
- `copy=`

### Useful constructor-related ideas

- when building a `DataFrame` from a dict of `Series`, pandas aligns them by index
- when building from a list of dicts, keys become columns
- constructor choices affect inferred dtypes, especially for strings, missing values, and integers

### Common object creation helpers

- `pd.Index(...)`
- `pd.date_range(...)`
- `pd.period_range(...)`
- `pd.timedelta_range(...)`
- `pd.Categorical(...)`
- `pd.array(...)`

---

## 4. Inspecting data

First things you do with a DataFrame:

```python
df.head()
df.tail()
df.sample(5)
df.shape
df.columns
df.index
df.dtypes
df.info()
df.describe()
```

### Important inspection methods

- `head()`, `tail()`, `sample()`
- `info()` → columns, non-null counts, memory, dtypes
- `describe()` → summary stats
- `value_counts()` → frequencies
- `nunique()` → distinct counts
- `unique()` → unique values
- `memory_usage()` → memory per column
- `isna().sum()` → missing values count

### `describe()`

Numeric columns by default:

```python
df.describe()
```

Include all columns:

```python
df.describe(include="all")
```

Select dtypes first:

```python
df.select_dtypes(include="number").describe()
```

---

## 5. Indexing, selection, and assignment

This is one of the most important parts of pandas.

## Column selection

```python
df["col"]         # Series
df[["col1", "col2"]]   # DataFrame
```

### Attribute access

```python
df.col
```

Possible, but **not recommended** as a general rule, because:

- fails if column name has spaces or conflicts with method names
- is less explicit
- can be fragile

Prefer:

```python
df["col"]
```

---

## Row selection by label: `loc`

`loc` is **label-based**.

```python
df.loc[5]
df.loc["row_label"]
df.loc["a":"d"]                # label slice is inclusive
df.loc[df["score"] > 80]
df.loc[df["score"] > 80, ["name", "score"]]
```

Use `loc` for:

- selecting rows by index labels
- selecting rows and columns together
- boolean filtering with explicit column selection
- assignment

Example:

```python
df.loc[df["age"] >= 18, "adult"] = True
```

---

## Row/column selection by integer position: `iloc`

`iloc` is **position-based**.

```python
df.iloc[0]
df.iloc[0:5]
df.iloc[:, 0]
df.iloc[0:3, 1:4]
```

Important: slicing uses Python’s normal half-open semantics (`stop` excluded).

---

## Fast scalar access: `at` and `iat`

- `at` → label-based scalar access
- `iat` → integer-position scalar access

```python
df.at[2, "score"]
df.iat[2, 1]
```

Use them when you need a single value.

---

## Boolean indexing

```python
df[df["score"] > 80]
df[(df["score"] > 80) & (df["age"] >= 18)]
df[(df["city"] == "Delhi") | (df["city"] == "Mumbai")]
```

Rules:

- use `&`, `|`, `~` instead of `and`, `or`, `not`
- wrap each condition in parentheses

Wrong:

```python
df[df["a"] > 0 and df["b"] < 5]
```

Right:

```python
df[(df["a"] > 0) & (df["b"] < 5)]
```

---

## Membership-based filtering: `isin`

```python
df[df["city"].isin(["Delhi", "Mumbai"])]
```

Negation:

```python
df[~df["city"].isin(["Delhi", "Mumbai"])]
```

---

## Missing-aware filtering

```python
df[df["x"].isna()]
df[df["x"].notna()]
```

---

## Conditional replacement: `where` and `mask`

- `where(cond, other)` keeps values where condition is `True`, replaces where `False`
- `mask(cond, other)` replaces values where condition is `True`

```python
df["x"].where(df["x"] >= 0, 0)
df["x"].mask(df["x"] < 0, 0)
```

---

## Setting values

### Single column assignment

```python
df["new"] = df["a"] + df["b"]
```

### Multiple columns

```python
df[["x", "y"]] = some_2d_value
```

### `loc` assignment

```python
df.loc[df["score"] < 50, "status"] = "fail"
```

### `assign`

Useful in pipelines because it returns a new DataFrame:

```python
df = df.assign(total=df["a"] + df["b"])
```

You can also reference newly created columns in the same `assign` call using callables:

```python
df = df.assign(
    total=lambda x: x["a"] + x["b"],
    ratio=lambda x: x["a"] / x["b"]
)
```

In newer pandas, `pd.col()` can also be used to build column expressions in some contexts.

---

## Dropping rows/columns

```python
df.drop(columns=["A", "B"])
df.drop(index=[0, 1])
```

Remember:

- `axis=0` means rows
- `axis=1` means columns
- but `index=` and `columns=` are clearer than `axis=`

---

## Renaming

```python
df.rename(columns={"old": "new"})
df.rename(index={0: "zero"})
df.set_axis(["A", "B", "C"], axis=1)
```

---

## Reindexing

`reindex` conforms data to a new set of labels.

```python
df.reindex([0, 1, 2, 3, 4])
df.reindex(columns=["A", "B", "C"])
```

This is useful for alignment and inserting missing labels.

---

## Resetting / setting index

```python
df.reset_index()
df.reset_index(drop=True)
df.set_index("id")
df.set_index(["country", "city"])
```

---

## 6. Index objects and alignment

One of pandas’ defining features is **automatic alignment**.

### Alignment in arithmetic

```python
s1 = pd.Series([1, 2], index=["a", "b"])
s2 = pd.Series([10, 20], index=["b", "c"])

s1 + s2
```

Result:

- `"a"` has no match → missing
- `"b"` matches
- `"c"` has no match → missing

This is extremely useful, but also a common source of unexpected `NaN`s.

### Alignment in DataFrames

Operations align on:

- row index
- column labels

### Managing alignment explicitly

- `align()`
- `reindex()`
- `add()`, `sub()`, `mul()`, etc. with `fill_value=`
- `combine_first()`

Example:

```python
s1.add(s2, fill_value=0)
```

---

## 7. Copy-on-Write and mutation rules

This is **very important in modern pandas (3.x)**.

### The big idea

In pandas 3.x, subsets and derived objects **behave as copies from the user’s perspective**.  
You should assume that:

- selecting part of a DataFrame gives you an object that does **not** mutate the original
- to modify the original DataFrame, assign directly into the original object

### Good pattern

```python
df.loc[df["x"] < 0, "x"] = 0
```

### Bad / obsolete pattern

```python
df[df["x"] < 0]["x"] = 0
```

That is chained assignment and should be avoided.

### Why this matters

Older pandas behavior around views vs copies was confusing. Modern pandas makes the rule more predictable:

- indexing results act like copies
- chained assignment does not modify the original
- defensive `.copy()` calls to silence old warnings are often no longer needed for that reason alone

### Best practice

- always use `loc`/`iloc` on the original object for mutation
- avoid chained indexing when assigning
- use `.copy()` only when you semantically want an explicit independent copy

---

## 8. Data types in pandas

Understanding dtypes is essential.

### Major dtype families

#### NumPy dtypes
- `int64`, `float64`, `bool`
- `object`
- fixed-width numeric types (`int32`, `float32`, etc.)

#### pandas extension dtypes
- `Int64`, `Int32`, ... (nullable integers)
- `boolean` (nullable boolean)
- `string` / `str`-related string dtypes
- `category`
- Arrow-backed dtypes
- sparse dtypes

#### time-related dtypes
- `datetime64[ns]`
- `datetime64[ns, tz]`
- `timedelta64[ns]`
- period-related objects/indexes

---

## `object` dtype

Historically, many text columns were stored as `object`.  
But `object` can store **any Python object**, not just strings.

This can be:

- ambiguous
- slower
- less memory-efficient
- harder to reason about

Use proper dtypes where possible.

---

## Modern string dtype

In pandas 3.x, string inference changed significantly.

Conceptually:

- pandas now has dedicated string dtypes
- string data should be treated as string dtype, not generic `object`, whenever possible
- pyarrow may be used under the hood when available

Practical guidance:

```python
s = pd.Series(["a", "b", None], dtype="string")  # nullable string
s2 = pd.Series(["a", "b", None], dtype="str")    # new default string dtype style
```

### `astype`

```python
df["age"] = df["age"].astype("Int64")
df["flag"] = df["flag"].astype("boolean")
df["name"] = df["name"].astype("string")
```

### `convert_dtypes`

One of the most useful cleanup methods:

```python
df = df.convert_dtypes()
```

It tries to convert columns to better nullable dtypes that support missing data well.

### Type conversion helpers

- `pd.to_numeric(...)`
- `pd.to_datetime(...)`
- `pd.to_timedelta(...)`

Examples:

```python
pd.to_numeric(s, errors="coerce")
pd.to_datetime(s, errors="coerce")
pd.to_timedelta(s, errors="coerce")
```

### Selecting by dtype

```python
df.select_dtypes(include="number")
df.select_dtypes(include=["string", "object"])
df.select_dtypes(exclude=["datetime"])
```

---

## 9. Missing data

Missing data handling is central in pandas.

### Main missing markers

- `np.nan` for many numeric contexts
- `pd.NA` for newer nullable dtypes
- `NaT` for datetime-like missing values

### Detecting missing values

```python
df.isna()
df.notna()
df["x"].isna().sum()
```

Aliases:

- `isnull()` ~ `isna()`
- `notnull()` ~ `notna()`

Prefer `isna()` / `notna()`.

### Dropping missing data

```python
df.dropna()
df.dropna(axis=1)
df.dropna(subset=["A", "B"])
df.dropna(how="all")
df.dropna(thresh=3)
```

### Filling missing data

```python
df.fillna(0)
df.fillna({"A": 0, "B": "unknown"})
df.ffill()
df.bfill()
```

### Interpolation

Useful especially for numeric/time-series data:

```python
df["x"].interpolate()
```

### Calculations and missing data

Many reductions skip missing values by default:

```python
df["x"].sum()
df["x"].mean()
```

You can control this with `skipna=` in many methods.

### Missing data with nullable dtypes

Prefer nullable dtypes (`Int64`, `boolean`, `string`, etc.) when missing values are expected and the semantic dtype matters.

Bad:

```python
pd.Series([1, None])   # often becomes float
```

Better:

```python
pd.Series([1, None], dtype="Int64")
```

---

## 10. Core vectorized operations

pandas is designed for **column-wise, vectorized operations**.

### Arithmetic

```python
df["a"] + df["b"]
df["a"] - 5
df["a"] * 100
df["a"] / df["b"]
```

### Comparison

```python
df["a"] > 0
df["city"] == "Delhi"
```

### Arithmetic methods

These are useful because they support options like `fill_value=`:

- `add`
- `sub`
- `mul`
- `div`
- `floordiv`
- `mod`
- `pow`

Example:

```python
s1.add(s2, fill_value=0)
```

### Other high-value vectorized methods

- `clip()`
- `abs()`
- `round()`
- `between()`
- `isin()`
- `replace()`
- `map()` (Series)
- `where()`, `mask()`
- `combine_first()`
- `update()`

### Broadcasting

Scalar operations broadcast naturally:

```python
df["x"] + 1
df + 100
```

### Element-wise vs axis-wise thinking

pandas operations may apply:

- element-wise
- column-wise
- row-wise
- group-wise
- window-wise

Always be clear about the intended axis and shape of the result.

---

## 11. Descriptive statistics and summaries

### Basic reductions

For Series/DataFrame:

- `sum()`
- `mean()`
- `median()`
- `min()`
- `max()`
- `std()`
- `var()`
- `count()`
- `prod()`
- `quantile()`

### Cumulative methods

- `cumsum()`
- `cumprod()`
- `cummax()`
- `cummin()`

### Position / ranking style

- `idxmax()`
- `idxmin()`
- `rank()`
- `nlargest()`
- `nsmallest()`

### Frequency summaries

- `value_counts()`
- `unique()`
- `nunique()`
- `mode()`

Examples:

```python
df["city"].value_counts()
df["city"].value_counts(normalize=True)
df["city"].value_counts(dropna=False)
```

### Relationship summaries

- `corr()`
- `cov()`
- `corrwith()`

### Difference / change over rows

- `diff()`
- `pct_change()`
- `shift()`

These are especially important in time series.

---

## 12. Sorting, ranking, and ordering

### Sorting by labels

```python
df.sort_index()
df.sort_index(axis=1)
```

### Sorting by values

```python
df.sort_values("score")
df.sort_values(["city", "score"], ascending=[True, False])
df.sort_values("score", na_position="last")
```

### Ranking

```python
df["rank"] = df["score"].rank(ascending=False)
```

### Stable ordering concepts

- sorting affects presentation and some algorithms
- many time-series operations require sorted time indexes
- MultiIndex operations often require sorting for fast slicing and predictable behavior

---

## 13. Working with text data

The `.str` accessor provides vectorized string operations.

```python
s.str.lower()
s.str.upper()
s.str.strip()
s.str.len()
s.str.contains("abc", na=False)
s.str.startswith("A")
s.str.endswith(".csv")
s.str.replace("old", "new", regex=False)
s.str.split(",")
s.str.extract(r"(\d+)")
s.str.slice(0, 3)
```

### Common uses

- cleaning whitespace
- case normalization
- pattern matching
- token extraction
- splitting columns
- validating formats

### Regex-related methods

- `contains`
- `extract`
- `extractall`
- `replace`
- `match`
- `fullmatch`

### Important note

String methods behave somewhat differently depending on the string dtype and missing value representation.  
For robust string pipelines, dedicated string dtypes are better than raw `object` columns.

---

## 14. Categorical data

`category` dtype is useful when a column has a limited set of repeated values.

Examples:

- country
- grade
- department
- product category

### Why use categorical?

- lower memory usage
- sometimes faster operations
- explicit category ordering
- useful for modeling and reporting

### Create category dtype

```python
df["grade"] = df["grade"].astype("category")
```

Or define ordered categories:

```python
from pandas.api.types import CategoricalDtype

grade_type = CategoricalDtype(
    categories=["low", "medium", "high"],
    ordered=True
)
df["grade"] = df["grade"].astype(grade_type)
```

### Useful categorical operations

```python
df["grade"].cat.categories
df["grade"].cat.codes
df["grade"].cat.add_categories(["very high"])
df["grade"].cat.remove_unused_categories()
df["grade"].cat.reorder_categories(["low", "medium", "high"], ordered=True)
```

### Binning continuous data into categories

```python
pd.cut(df["age"], bins=[0, 18, 35, 60, 100])
pd.qcut(df["income"], q=4)
```

- `cut` uses explicit bin edges
- `qcut` uses quantiles so bins have roughly equal counts

### Important ideas

- categories may exist even if not currently present in the data
- ordered categoricals affect sorting and comparisons
- categoricals are excellent for repeated low-cardinality text values

---

## 15. Date, time, timedelta, and time series

This is a major pandas strength.

### Convert strings to datetime

```python
df["date"] = pd.to_datetime(df["date"])
```

Common options:

- `errors="coerce"`
- `format=...`
- `utc=True`

### Generate date ranges

```python
pd.date_range("2026-01-01", periods=5, freq="D")
```

### Important datetime-related objects

- `Timestamp`
- `DatetimeIndex`
- `Timedelta`
- `TimedeltaIndex`
- `Period`
- `PeriodIndex`
- `DateOffset`

### Date/time components

Once a Series is datetime-like:

```python
s.dt.year
s.dt.month
s.dt.day
s.dt.day_name()
s.dt.hour
s.dt.minute
s.dt.quarter
s.dt.is_month_end
```

### Time zone handling

```python
s.dt.tz_localize("Asia/Kolkata")
s.dt.tz_convert("UTC")
```

Conceptual difference:

- `tz_localize` attaches a timezone to naive timestamps
- `tz_convert` converts between timezones for tz-aware timestamps

### Timedeltas

```python
td = pd.to_timedelta(df["duration"])
```

Useful methods:

```python
td.dt.days
td.dt.seconds
```

### Set datetime index

Many time-series features work best with a datetime index:

```python
df = df.set_index("date")
```

For intraday data you may also see clock-time selectors such as `at_time` and `between_time`.

### Partial string indexing

With a sorted `DatetimeIndex`:

```python
df.loc["2026"]
df.loc["2026-03"]
df.loc["2026-03-15":"2026-03-20"]
```

### Shifting and lagging

```python
df["sales_lag1"] = df["sales"].shift(1)
```

### Resampling

Resampling changes frequency and aggregates or fills values.

```python
df.resample("D").sum()
df.resample("M").mean()
df.resample("H").ffill()
```

Common frequencies:

- `D` day
- `W` week
- `M` month end
- `MS` month start
- `Q` quarter end
- `Y` year end
- `H` hour
- `min` minute
- `s` second

### `asfreq`

Changes frequency without aggregation:

```python
df.asfreq("D")
```

### Rolling time windows

```python
df.rolling("7D").mean()
```

### Periods

Useful for spans such as months/quarters instead of instants:

```python
p = pd.period_range("2025Q1", periods=4, freq="Q")
```

---

## 16. GroupBy: split-apply-combine

GroupBy is a core pandas concept.

### Mental model

1. **split** data into groups
2. **apply** a function per group
3. **combine** results

### Create groups

```python
g = df.groupby("department")
g = df.groupby(["department", "gender"])
```

### Common aggregations

```python
df.groupby("department")["salary"].mean()
df.groupby("department").agg({"salary": ["mean", "max"], "age": "median"})
```

### Named aggregation

Very useful and readable:

```python
df.groupby("department").agg(
    avg_salary=("salary", "mean"),
    max_salary=("salary", "max"),
    n=("salary", "size")
)
```

### `size` vs `count`

- `size()` counts rows
- `count()` counts non-missing values per column

### `agg`, `transform`, `filter`, `apply`

These are conceptually different:

#### `agg`
Returns reduced summaries.

```python
df.groupby("dept")["salary"].agg(["mean", "max"])
```

#### `transform`
Returns output aligned to the original rows.

```python
df["dept_mean"] = df.groupby("dept")["salary"].transform("mean")
```

Use `transform` when you want group statistics back on each row.

#### `filter`
Keeps/removes whole groups based on a condition.

```python
df.groupby("dept").filter(lambda g: len(g) >= 5)
```

#### `apply`
Most flexible, often slowest, and easiest to misuse.

```python
df.groupby("dept").apply(custom_func)
```

Prefer `agg`, `transform`, or built-in methods when possible.

### Useful groupby options

- `as_index=`
- `sort=`
- `dropna=`
- `observed=` for categorical groupers

### Grouping with time

```python
df.groupby(pd.Grouper(key="date", freq="M")).sum()
```

### Common grouped operations

- grouped totals
- per-group normalization
- within-group ranking
- z-scores within group
- first/last record per group
- cumulative stats within group

Examples:

```python
df["rank_in_group"] = df.groupby("dept")["salary"].rank(ascending=False)
df["cum_sales"] = df.groupby("store")["sales"].cumsum()
```

---

## 17. Window operations

Window functions compute statistics over a moving or accumulating window.

The main window types are:

- `rolling`
- `expanding`
- `ewm` (exponentially weighted)
- weighted windows in some contexts

### Rolling window

```python
s.rolling(window=3).mean()
s.rolling(window=3).sum()
s.rolling(window=3).apply(custom_func)
```

### Time-based rolling

```python
df.rolling("7D").mean()
```

### Expanding window

Accumulates from the start:

```python
s.expanding().mean()
```

### Exponentially weighted window

Gives more weight to recent values:

```python
s.ewm(span=10).mean()
```

### Common parameters

- `window`
- `min_periods`
- `center`
- `closed`
- `on=` for DataFrame time-based windows

### Chaining with groupby

```python
df.groupby("id")["value"].rolling(3).mean()
```

Window methods are crucial in finance, forecasting, signal processing, and time-series smoothing.

---

## 18. Combine, merge, join, concatenate, compare

This is one of the highest-value areas in real work.

## `concat`

Stack objects along rows or columns.

```python
pd.concat([df1, df2], axis=0)
pd.concat([df1, df2], axis=1)
```

Use for:

- appending tables vertically
- stitching aligned tables horizontally

Key parameters:

- `axis`
- `ignore_index`
- `keys`
- `join`
- `verify_integrity`

---

## `merge`

SQL-style join on columns or indexes.

```python
df1.merge(df2, on="id")
df1.merge(df2, how="left", on="id")
df1.merge(df2, how="inner", on="id")
df1.merge(df2, how="outer", on="id")
df1.merge(df2, how="right", on="id")
```

### Join types

- `inner` → intersection of keys
- `left` → all keys from left
- `right` → all keys from right
- `outer` → union of keys
- `cross` → Cartesian product

### Important merge parameters

- `on`
- `left_on`, `right_on`
- `left_index`, `right_index`
- `how`
- `suffixes`
- `indicator`
- `validate`

### `validate` is very important

Use it to catch merge mistakes:

```python
df1.merge(df2, on="id", validate="one_to_one")
```

Possible validations:

- `"one_to_one"`
- `"one_to_many"`
- `"many_to_one"`
- `"many_to_many"`

### `indicator=True`

Useful for debugging joins:

```python
df1.merge(df2, on="id", how="outer", indicator=True)
```

Gives a `_merge` column indicating source membership.

---

## `join`

Convenient join primarily by index.

```python
df1.join(df2, how="left")
```

Often useful when keys are already indexes.

---

## Ordered / asof merges

### `merge_ordered`

Useful for ordered data.

### `merge_asof`

Useful for nearest-key joins, especially in time-series data.

Example concept:

- join each trade to the nearest previous quote

---

## `compare`

Shows differences between two aligned objects.

```python
df_old.compare(df_new)
```

---

## 19. Reshaping and pivoting

Reshaping changes data layout.

## `pivot`

Reshape long → wide without aggregation.

```python
df.pivot(index="id", columns="variable", values="value")
```

Requires unique `(index, columns)` pairs.

## `pivot_table`

Like `pivot`, but supports aggregation.

```python
df.pivot_table(
    index="dept",
    columns="gender",
    values="salary",
    aggfunc="mean"
)
```

Common parameters:

- `aggfunc`
- `fill_value`
- `margins`
- `dropna`

## `melt`

Wide → long.

```python
df.melt(id_vars="id", var_name="metric", value_name="value")
```

## `stack` and `unstack`

Move levels between rows and columns.

```python
df.stack()
s.unstack()
```

Important with `MultiIndex`.

## `wide_to_long`

Useful for regular column naming patterns such as `score_2024`, `score_2025`.

## `explode`

Turns list-like entries into multiple rows.

```python
df.explode("tags")
```

## `crosstab`

Frequency table:

```python
pd.crosstab(df["dept"], df["gender"])
```

Can normalize to proportions:

```python
pd.crosstab(df["dept"], df["gender"], normalize=True)
```

## Dummies / one-hot encoding

```python
pd.get_dummies(df["city"])
pd.from_dummies(dummy_df)
```

---

## 20. Apply, map, transform, agg, and UDFs

This is where many users become inefficient, so conceptual clarity matters.

## `map`

Mostly for Series element-wise mapping.

```python
s.map({"A": 1, "B": 2})
s.map(lambda x: x * 2)
```

## `apply`

Flexible but often overused.

### Series `apply`

Applies a function to each element (or in a value-wise fashion).

```python
s.apply(func)
```

### DataFrame `apply`

Applies along an axis.

```python
df.apply(func, axis=0)   # per column
df.apply(func, axis=1)   # per row
```

Row-wise `apply(axis=1)` is often slow.

## `agg` / `aggregate`

For reductions or combinations of reductions.

```python
df.agg({"a": "sum", "b": "mean"})
```

## `transform`

Returns output with same shape/alignment as input.

```python
df.groupby("dept")["salary"].transform("mean")
```

## `applymap` / elementwise DataFrame mapping

Historically used for element-wise DataFrame operations. In modern code, prefer the current recommended element-wise APIs for your pandas version and built-ins when possible. In general, vectorized operations are preferable to element-wise Python functions.

## UDFs (User-Defined Functions)

UDFs are custom Python functions you pass into pandas methods. Use them when built-ins do not cover the logic.

But first ask:

1. Can I do this with vectorized operations?
2. Can I use built-in string/datetime/groupby/window methods?
3. Can I restructure with `where`, `np.select`, `map`, `merge`, `cut`, etc.?

Only then reach for a Python-level UDF.

---

## 21. Expressions, query, eval, and pipe

These improve readability and sometimes performance.

## `query`

Filter rows using an expression string.

```python
df.query("score > 80 and age >= 18")
```

Advantages:

- concise
- readable for complex filters
- avoids many parentheses

Be careful with:

- column names containing spaces or special characters
- local Python variables (use `@var`)

Example:

```python
threshold = 80
df.query("score > @threshold")
```

## `eval`

Evaluate expressions involving columns.

```python
df.eval("total = a + b")
```

Can be convenient and sometimes performant for large numeric expressions.

## `pipe`

Excellent for clean method chains.

```python
(
    df
    .pipe(clean_names)
    .pipe(filter_recent)
    .assign(total=lambda x: x["a"] + x["b"])
)
```

Use `pipe` to keep transformation pipelines readable.

---

## 22. Input / output (I/O)

pandas is heavily used for reading and writing data.

## Text / delimited files

### `read_csv`

One of the most important functions in pandas.

```python
df = pd.read_csv("data.csv")
```

High-value parameters:

- `usecols`
- `dtype`
- `parse_dates`
- `index_col`
- `na_values`
- `keep_default_na`
- `nrows`
- `skiprows`
- `encoding`
- `sep`
- `header`
- `names`
- `chunksize`

Examples:

```python
pd.read_csv("data.csv", usecols=["id", "date", "value"])
pd.read_csv("data.csv", parse_dates=["date"])
pd.read_csv("data.csv", dtype={"id": "Int64"})
pd.read_csv("data.csv", chunksize=100_000)
```

### Writing CSV

```python
df.to_csv("out.csv", index=False)
```

---

## Excel

```python
pd.read_excel("file.xlsx")
df.to_excel("out.xlsx", index=False)
```

High-value parameters include:

- `sheet_name`
- `usecols`
- `dtype`
- `converters`

---

## Parquet

A very important modern storage format.

```python
pd.read_parquet("data.parquet")
df.to_parquet("data.parquet")
```

Advantages:

- efficient
- typed
- compressed
- good for analytics pipelines

---

## JSON

```python
pd.read_json("data.json")
df.to_json("out.json")
```

---

## SQL

```python
pd.read_sql("SELECT * FROM table", conn)
df.to_sql("table_name", conn, index=False)
```

---

## Other common I/O methods

- `read_html`
- `read_xml`
- `read_pickle`
- `to_pickle`
- `to_json`
- `to_markdown`
- `read_clipboard`
- `to_clipboard`

---

## 23. Visualization and styling

## Plotting

Basic plotting is built in and uses plotting backends such as Matplotlib by default.

```python
df["sales"].plot()
df.plot(x="date", y="sales")
df["sales"].hist()
df.plot.scatter(x="a", y="b")
```

Useful plot kinds:

- line
- bar
- barh
- hist
- box
- kde
- area
- scatter
- pie

Plotting is convenient for quick exploration, though many users also use seaborn, matplotlib, plotly, altair, etc.

## Styling with `Styler`

For presentation tables:

```python
df.style.format("{:.2f}").highlight_max()
```

Useful Styler features:

- `format`
- `highlight_max`
- `highlight_min`
- `background_gradient`
- `set_caption`
- `set_properties`
- `set_table_styles`

Styler is mainly for display/export, not data transformation.

---

## 24. Nullable dtypes and Arrow / PyArrow

This is an important modern pandas topic.

### Nullable dtypes

Traditional NumPy integer/bool dtypes do not naturally support missing values well.  
pandas provides nullable dtypes such as:

- `Int64`
- `Int32`
- `boolean`
- `string`

Advantages:

- preserve semantic type even with missing data
- integrate better with pandas missing-value logic

### Arrow / PyArrow support

pandas can use PyArrow to improve:

- dtype support
- missing data handling across types
- I/O performance
- interoperability with Arrow-based libraries

PyArrow is especially relevant for:

- modern string handling
- parquet workflows
- Arrow-backed arrays/dtypes
- interchange with other dataframe systems

### Practical guidance

- use `convert_dtypes()` after reading messy data
- prefer Parquet over CSV when you control storage
- be aware that string dtype behavior is different in modern pandas than in old tutorials

---

## 25. Duplicate labels

pandas allows duplicate labels, but they can cause ambiguity.

Examples:

- duplicate index values
- duplicate column names

Why it matters:

- selection may return multiple rows/columns unexpectedly
- reshaping and some operations may fail or become ambiguous
- debugging becomes harder

### Detect duplicates

```python
df.index.has_duplicates
df.columns.has_duplicates
df.index.duplicated()
```

### Common cleanup

```python
df = df[~df.index.duplicated()]
df = df.loc[:, ~df.columns.duplicated()]
```

### Duplicate row detection

This is separate from duplicate labels:

```python
df.duplicated()
df.drop_duplicates()
df.drop_duplicates(subset=["id"])
```

Best practice: keep indexes and column names unique unless you have a strong reason not to.

---

## 26. Sparse data

Sparse data structures help when most values are the same fill value (often zero).

Use cases:

- one-hot matrices
- high-dimensional low-density tables
- certain scientific / recommendation / NLP data

### Sparse arrays / sparse accessors

pandas supports sparse dtypes and sparse accessors such as:

- `Series.sparse`
- `DataFrame.sparse`

Examples include:

```python
df.sparse.density
df.sparse.to_coo()
pd.DataFrame.sparse.from_spmatrix(...)
```

Sparse structures can save substantial memory for mostly-empty data.

---

## 27. Performance and scaling

A huge practical topic.

## First rule: vectorize

Prefer:

```python
df["total"] = df["a"] + df["b"]
```

Over row-by-row Python loops.

## Avoid `iterrows()` for most work

`iterrows()` is usually slow and often changes dtypes when yielding rows.

Prefer:

- vectorized operations
- `map`
- `where`
- `np.select`
- `merge`
- `groupby`
- `itertuples()` if iteration is unavoidable

## Use efficient dtypes

- convert repeated strings to `category`
- use nullable integers/bools instead of `object`
- use Arrow-backed types when helpful
- downcast numerics when appropriate

## Read less data

At load time:

- `usecols=`
- `nrows=`
- `dtype=`
- `parse_dates=`
- filtering early if possible

## Use chunking for large files

```python
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    ...
```

## Prefer Parquet for repeated analytical workflows

Compared with CSV, Parquet is usually better for:

- speed
- schema preservation
- compression
- typed data

## `eval` / expression engines

For some numeric expressions, `eval()` can help.

## Numba / Cython

For specific heavy numerical custom functions, pandas can integrate with:

- Numba
- Cython

But do this only when vectorization and algorithmic improvements are insufficient.

## Scaling boundaries

pandas is excellent, but not infinite. For very large datasets, consider:

- Arrow datasets
- DuckDB
- Polars
- Spark / Dask
- databases

Use pandas when data fits comfortably in memory and you need rich in-memory analysis.

---

## 28. Common pitfalls and best practices

## Pitfall 1: chained assignment

Bad:

```python
df[df["x"] > 0]["y"] = 1
```

Good:

```python
df.loc[df["x"] > 0, "y"] = 1
```

## Pitfall 2: forgetting alignment

You expected position-based arithmetic, but pandas aligned by labels.

Fix by:

- checking indexes
- using `.to_numpy()` only when you explicitly want raw positional arrays
- using `reset_index(drop=True)` if appropriate

## Pitfall 3: using `object` everywhere

Convert to better dtypes.

```python
df = df.convert_dtypes()
```

## Pitfall 4: row-wise `apply(axis=1)` for everything

Usually slow. Prefer vectorized logic or column-wise operations.

## Pitfall 5: merge explosions

If keys are not unique, row counts can blow up.

Use:

```python
validate=
indicator=True
```

and check key uniqueness.

## Pitfall 6: assuming `count()` counts missing values

It does not. `count()` skips missing values.

If you want row count, use:

```python
len(df)
df.shape[0]
grouped.size()
```

## Pitfall 7: not controlling dtypes when reading files

File reading often infers types imperfectly. For important columns, pass `dtype=` or convert explicitly later.

## Pitfall 8: confusing `pivot` with `pivot_table`

- `pivot` requires unique keys and does **no aggregation**
- `pivot_table` aggregates duplicates

## Pitfall 9: duplicate labels

Check `has_duplicates`.

## Pitfall 10: mixing naive and timezone-aware datetimes

Be explicit about timezones.

---

## 29. High-value methods to remember

This is the “must know” shortlist.

### Inspection
- `head`, `tail`, `sample`, `info`, `describe`, `memory_usage`

### Selection
- `loc`, `iloc`, `at`, `iat`
- boolean masks
- `isin`, `where`, `mask`

### Cleaning
- `rename`, `drop`, `drop_duplicates`
- `replace`, `fillna`, `dropna`, `interpolate`
- `astype`, `convert_dtypes`
- `to_numeric`, `to_datetime`, `to_timedelta`

### Transformation
- `assign`, `map`, `apply`, `agg`, `transform`
- `sort_values`, `sort_index`
- `rank`, `clip`, `round`
- `shift`, `diff`, `pct_change`

### Grouping
- `groupby`, `agg`, `transform`, `filter`, `apply`

### Combining
- `concat`, `merge`, `join`, `combine_first`, `update`, `compare`

### Reshaping
- `pivot`, `pivot_table`, `melt`, `stack`, `unstack`, `explode`, `crosstab`, `get_dummies`

### Time series
- `to_datetime`, `date_range`, `resample`, `asfreq`, `rolling`, `ewm`

### I/O
- `read_csv`, `to_csv`
- `read_excel`, `to_excel`
- `read_parquet`, `to_parquet`
- `read_sql`, `to_sql`

---

## 30. Typical pandas workflow

A realistic sequence:

```python
import pandas as pd

df = pd.read_csv("sales.csv")

# inspect
print(df.head())
print(df.info())

# clean dtypes
df = df.convert_dtypes()
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# clean values
df = df.dropna(subset=["customer_id", "date"])
df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0)

# filter
df = df.loc[df["sales"] >= 0]

# transform
df = df.assign(
    month=lambda x: x["date"].dt.to_period("M"),
    is_large=lambda x: x["sales"] > 1000
)

# summarize
summary = (
    df.groupby(["month", "region"])
      .agg(total_sales=("sales", "sum"),
           avg_sales=("sales", "mean"),
           orders=("sales", "size"))
      .reset_index()
)

# reshape
wide = summary.pivot(index="month", columns="region", values="total_sales")

# export
wide.to_parquet("monthly_sales.parquet")
```

This example touches the main pandas workflow:

- read
- inspect
- type-fix
- clean missing data
- filter
- transform
- group
- reshape
- export

---

## 31. One-page mental model

If you remember only one mental model, remember this:

### pandas is built around labeled arrays/tables

- `Series` = 1D labeled array
- `DataFrame` = 2D labeled table
- `Index` = label system for rows/columns

### Most work in pandas is one of these

1. **Select**
   - columns, rows, subsets
2. **Clean**
   - fix types, handle missing values, rename, deduplicate
3. **Transform**
   - create new columns, recode, sort, rank, shift
4. **Combine**
   - merge, join, concat
5. **Summarize**
   - aggregate, groupby, value counts, describe
6. **Reshape**
   - pivot, melt, stack, unstack, explode
7. **Time-series**
   - parse dates, set datetime index, resample, rolling
8. **Export**
   - write clean output

### Golden rules

- prefer vectorized operations over loops
- use `loc` for assignment
- understand alignment
- control dtypes early
- prefer nullable dtypes over `object` where possible
- use `groupby(...).transform(...)` when you need per-group values back on each row
- use `merge(..., validate=...)` for safe joins
- use `pivot_table` when duplicates exist
- use Parquet for typed analytical storage
- always inspect after reading data

---

# Final revision checklist

Use this checklist to test yourself:

- Can I explain `Series`, `DataFrame`, `Index`, `MultiIndex`?
- Can I distinguish `loc` vs `iloc` vs `at` vs `iat`?
- Do I understand index alignment?
- Do I know how assignment should be done safely under Copy-on-Write?
- Do I know when to use `astype`, `convert_dtypes`, `to_datetime`, `to_numeric`?
- Can I handle missing values with `isna`, `dropna`, `fillna`, `interpolate`?
- Do I know `groupby(...).agg(...)` vs `transform(...)` vs `apply(...)`?
- Do I know `merge` vs `join` vs `concat`?
- Do I know `pivot` vs `pivot_table` vs `melt`?
- Can I work with string, categorical, datetime, timedelta, and nullable integer/boolean columns?
- Do I know `rolling`, `expanding`, `ewm`, and `resample`?
- Do I know which I/O functions matter most?
- Do I know how to avoid slow row-wise code and dangerous chained assignment?

If the answer is “yes” to all of these, your conceptual pandas foundation is strong.

---

# Minimal cheat sheet

```python
# selection
df.loc[rows, cols]
df.iloc[rows, cols]

# filtering
df[df["x"] > 0]
df[df["city"].isin(["Delhi", "Mumbai"])]

# assignment
df.loc[df["x"] < 0, "x"] = 0
df = df.assign(total=lambda x: x["a"] + x["b"])

# missing data
df.isna().sum()
df.dropna(subset=["a"])
df.fillna({"a": 0})

# types
df = df.convert_dtypes()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# groupby
df.groupby("dept").agg(avg=("salary", "mean"), n=("salary", "size"))
df["dept_avg"] = df.groupby("dept")["salary"].transform("mean")

# joins
df1.merge(df2, on="id", how="left", validate="one_to_one")

# reshape
df.melt(id_vars="id")
df.pivot_table(index="dept", columns="gender", values="salary", aggfunc="mean")

# time series
df = df.set_index("date")
df.resample("M").sum()
df["rolling_7"] = df["sales"].rolling(7).mean()
```

---

# Closing note

This guide is intentionally **concept-first** rather than an exhaustive listing of every pandas method.  
If you master the concepts above, the API reference becomes much easier because most methods fit into one of these conceptual buckets:

- labeled selection
- dtype-aware transformation
- missing-data handling
- grouping
- combining
- reshaping
- time-series processing
- I/O
- performance-aware workflows
