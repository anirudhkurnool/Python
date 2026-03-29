# NumPy (Python) — Comprehensive Revision Notes

> **Scope**
>
> This file is a **comprehensive revision guide** for practical NumPy. It covers the important ideas, patterns, APIs, and gotchas you should know to use NumPy well.  
> It is **not** a line-by-line catalog of every single function in the library, but it is designed so you do **not miss the important concepts**.

---

## 1) What NumPy is

**NumPy** is the core array-computing library in Python.

It provides:

- the **`ndarray`**: a fast, homogeneous, N-dimensional array
- efficient **vectorized operations**
- **broadcasting**
- numerical routines for:
  - linear algebra
  - random sampling
  - statistics
  - sorting/searching/set operations
  - FFT
  - basic file I/O
  - dtype-aware computation

### Why NumPy is fast

NumPy is usually faster than pure Python loops because:

- data is stored in compact, typed memory blocks
- operations are implemented in optimized compiled code
- many operations work on entire arrays at once

### Standard import

```python
import numpy as np
```

---

## 2) The core object: `ndarray`

An `ndarray` is:

- **N-dimensional**
- **homogeneous**: all elements share one dtype
- described by metadata like:
  - `shape`
  - `dtype`
  - `ndim`
  - `size`
  - `itemsize`
  - `strides`

### Important attributes

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

a.ndim       # number of axes -> 2
a.shape      # tuple of axis lengths -> (2, 3)
a.size       # total number of elements -> 6
a.dtype      # element type
a.itemsize   # bytes per element
a.nbytes     # total bytes used by data buffer
a.T          # transpose view when possible
```

### Mental model

- A scalar array can be **0-D**
- A vector is usually **1-D**
- A matrix is **2-D**
- Anything beyond that is still just an ndarray with more axes

Examples:

```python
np.array(5).shape                 # ()
np.array([1, 2, 3]).shape         # (3,)
np.array([[1, 2], [3, 4]]).shape  # (2, 2)
```

---

## 3) Array creation

## 3.1 From Python objects

```python
np.array([1, 2, 3])
np.array([[1, 2], [3, 4]])
np.asarray([1, 2, 3])   # avoid copy when possible
```

### `np.array()` vs `np.asarray()`

- `np.array(x)` usually creates a NumPy array and may copy by default
- `np.asarray(x)` converts to an array **without copying if possible**

Use `asarray` when you want "treat this as an array if it already is one".

---

## 3.2 Creation routines by pattern

### Filled with values

```python
np.zeros((2, 3))
np.ones((2, 3))
np.full((2, 3), 7)
np.empty((2, 3))   # uninitialized values
```

### Ranges

```python
np.arange(0, 10, 2)       # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)      # 5 evenly spaced points including endpoints
np.logspace(1, 3, 3)      # [10, 100, 1000]
```

**Rule:**
- use `arange` for integer-like stepping
- use `linspace` for a fixed number of points over an interval

### Identity / diagonal / triangular

```python
np.eye(3)
np.identity(3)
np.diag([1, 2, 3])
np.triu(np.ones((3, 3)))
np.tril(np.ones((3, 3)))
```

### From shape of another array

```python
a = np.array([[1, 2], [3, 4]])
np.zeros_like(a)
np.ones_like(a)
np.full_like(a, 9)
```

### Coordinate-based creation

```python
np.fromfunction(lambda i, j: i + j, (3, 4), dtype=int)
```

### Random arrays

```python
rng = np.random.default_rng(42)
rng.random((2, 3))
rng.integers(0, 10, size=(2, 3))
```

---

## 4) Data types (`dtype`)

A NumPy array has a single dtype.

Examples:

```python
np.array([1, 2, 3], dtype=np.int32)
np.array([1, 2, 3], dtype=np.float64)
np.array([True, False], dtype=np.bool_)
np.array([1+2j], dtype=np.complex128)
```

## 4.1 Common dtype families

### Integers
- signed: `int8`, `int16`, `int32`, `int64`
- unsigned: `uint8`, `uint16`, `uint32`, `uint64`

### Floating point
- `float16`, `float32`, `float64`

### Complex
- `complex64`, `complex128`

### Boolean
- `bool_`

### Strings / bytes
- fixed-width Unicode / bytes
- newer string support also exists through `StringDType`

### Object
- `dtype=object` stores arbitrary Python objects  
- flexible, but much slower and loses most NumPy speed advantages

---

## 4.2 Inspecting and converting dtypes

```python
a = np.array([1, 2, 3], dtype=np.int32)
a.dtype

b = a.astype(np.float64)   # returns a new array
```

### Important dtype ideas

- dtype controls:
  - memory size
  - precision
  - overflow behavior
  - casting behavior
- integer arrays cannot store decimals without casting
- smaller dtypes save memory but can overflow sooner

Example:

```python
np.array([1, 2, 3], dtype=np.int8) + 100
```

This may overflow if you exceed the dtype range.

---

## 4.3 Type promotion

When arrays of different dtypes interact, NumPy chooses a common result dtype.

Examples:

```python
np.int8(4) + np.int64(8)      # promotes to int64
np.float32(3) + np.float16(3) # promotes to float32
```

### Practical rule

Mixed operations usually promote to a dtype that can represent the result more safely, but you should still be careful with:
- integer overflow
- float precision
- unexpected upcasting

---

## 4.4 Special values in floating arrays

```python
np.nan   # not-a-number
np.inf   # positive infinity
-np.inf
```

Useful checks:

```python
np.isnan(a)
np.isinf(a)
np.isfinite(a)
```

---

## 5) Shape, axes, and dimensions

Understanding **shape** and **axis** is one of the most important NumPy concepts.

Given:

```python
a = np.array([[1, 2, 3],
              [4, 5, 6]])
```

Then:

- `a.shape == (2, 3)`
- axis `0` = rows dimension
- axis `1` = columns dimension

### Reduction along an axis

```python
a.sum(axis=0)   # column-wise sum -> shape (3,)
a.sum(axis=1)   # row-wise sum -> shape (2,)
```

### `keepdims=True`

```python
a.sum(axis=1, keepdims=True)
```

Keeps reduced axes as size-1 dimensions, which is very useful for broadcasting.

---

## 6) Indexing and slicing

This is a very important topic.

## 6.1 Basic indexing

```python
a = np.array([10, 20, 30, 40])

a[0]     # 10
a[-1]    # 40
```

For 2-D:

```python
b = np.array([[1, 2, 3],
              [4, 5, 6]])

b[0, 1]   # 2
b[1, 2]   # 6
```

---

## 6.2 Basic slicing

```python
a[1:4]
a[:3]
a[::2]
a[::-1]
```

For 2-D:

```python
b[:, 1]      # second column
b[0, :]      # first row
b[:2, 1:]    # submatrix
```

### Very important rule

**Basic slicing usually returns a view, not a copy.**

```python
a = np.array([1, 2, 3, 4])
v = a[1:3]
v[0] = 99
# a is now [1, 99, 3, 4]
```

---

## 6.3 Fancy indexing (advanced indexing)

Using integer arrays/lists:

```python
a = np.array([10, 20, 30, 40, 50])
a[[0, 2, 4]]      # [10, 30, 50]
```

2-D example:

```python
b = np.array([[1, 2],
              [3, 4],
              [5, 6]])

b[[0, 2]]         # rows 0 and 2
```

### Important rule

**Fancy indexing returns a copy**, not a view.

---

## 6.4 Boolean indexing

```python
a = np.array([1, 2, 3, 4, 5])
mask = a % 2 == 0
a[mask]            # [2, 4]
a[a > 3]           # [4, 5]
```

Very useful for filtering.

### Assignment with masks

```python
a[a % 2 == 0] = -1
```

---

## 6.5 Combining slicing and indexing

Examples:

```python
b[:, [0, 2]]
b[b > 2]
```

Be careful: once advanced indexing is involved, copy behavior and result shape can be non-obvious.

---

## 6.6 `...` and `np.newaxis`

### Ellipsis `...`

Useful when you do not want to write all axes:

```python
x[..., 0]
```

### Add a dimension

```python
a = np.array([1, 2, 3])

a[:, np.newaxis].shape   # (3, 1)
a[np.newaxis, :].shape   # (1, 3)
```

`np.newaxis` is the same as `None` in indexing.

---

## 6.7 Common indexing helpers

```python
np.where(a > 0)
np.nonzero(a)
np.argwhere(a > 0)
np.take(a, [0, 2, 4])
np.put(a, [1, 3], [99, 88])
```

---

## 7) Reshaping and dimension manipulation

## 7.1 `reshape`

```python
a = np.arange(12)
a.reshape(3, 4)
a.reshape(2, 2, 3)
a.reshape(-1, 4)   # infer one dimension
```

### Important rule

A reshape returns a view **when possible**, otherwise it may copy.

---

## 7.2 Flattening

```python
a.ravel()      # view if possible
a.flatten()    # always copy
```

---

## 7.3 Transpose and axis permutation

```python
a.T
np.transpose(a)
np.swapaxes(a, 0, 1)
np.moveaxis(a, 0, -1)
```

For higher-dimensional arrays, `transpose` can reorder axes:

```python
x.transpose(2, 0, 1)
```

---

## 7.4 Expanding and squeezing dimensions

```python
np.expand_dims(a, axis=0)
np.expand_dims(a, axis=1)

np.squeeze(x)
np.squeeze(x, axis=0)
```

---

## 7.5 Ensuring minimum dimensionality

```python
np.atleast_1d(5)
np.atleast_2d([1, 2, 3])
np.atleast_3d([1, 2, 3])
```

---

## 8) Broadcasting

Broadcasting is one of the most powerful NumPy ideas.

It allows NumPy to perform operations on arrays with different shapes, as long as their shapes are compatible.

## 8.1 Broadcasting rule

Compare shapes from the **rightmost dimension** to the left.

Two dimensions are compatible if they are:
- equal, or
- one of them is `1`

Example:

```python
a.shape == (3, 4)
b.shape == (4,)
```

`b` behaves like `(1, 4)` and broadcasts across rows.

```python
a + b
```

Another example:

```python
x = np.arange(3).reshape(3, 1)   # (3, 1)
y = np.arange(4).reshape(1, 4)   # (1, 4)
x + y                            # (3, 4)
```

## 8.2 Why broadcasting matters

It lets you avoid Python loops:

```python
a - a.mean(axis=0)
```

or

```python
dist2 = ((points - center) ** 2).sum(axis=1)
```

## 8.3 Common broadcasting tools

```python
a[:, None]
a[None, :]
np.broadcast_to(a, (3, 4))
```

## 8.4 Common broadcasting mistakes

- mismatched trailing dimensions
- forgetting to add singleton axes
- accidentally creating huge temporary arrays

---

## 9) Vectorization and universal functions (ufuncs)

A **ufunc** is a function that works element-by-element on arrays.

Examples:

```python
np.abs(a)
np.sqrt(a)
np.exp(a)
np.log(a)
np.sin(a)
np.maximum(a, b)
```

## 9.1 Why ufuncs matter

They provide:

- vectorized computation
- broadcasting support
- dtype-aware behavior
- optional output placement via `out=`
- optional masking via `where=`

Example:

```python
np.sqrt(a, out=result, where=a >= 0)
```

## 9.2 Arithmetic operators are vectorized

```python
a + b
a - b
a * b
a / b
a // b
a % b
a ** 2
```

## 9.3 Comparison and logical operations

```python
a > 0
a == b
np.logical_and(a > 0, a < 10)
np.logical_or(a < 0, a > 10)
np.logical_not(mask)
```

Use `&`, `|`, `~` carefully with parentheses:

```python
(a > 0) & (a < 10)
```

Do **not** write:

```python
a > 0 & a < 10
```

That is wrong because of operator precedence.

## 9.4 Reductions on ufuncs

Many ufuncs support operations like:

```python
np.add.reduce(a)
np.multiply.accumulate(a)
```

You usually use the more common high-level forms like:

```python
a.sum()
a.cumsum()
a.prod()
a.cumprod()
```

## 9.5 Outer operations

```python
np.add.outer([1, 2, 3], [10, 20])
```

Very useful for pairwise computations.

---

## 10) Aggregation, reduction, and statistics

## 10.1 Basic reductions

```python
a.sum()
a.mean()
a.min()
a.max()
a.std()
a.var()
a.prod()
```

Axis-aware:

```python
a.sum(axis=0)
a.mean(axis=1)
```

## 10.2 Cumulative operations

```python
a.cumsum()
a.cumprod()
```

## 10.3 Arg reductions

```python
a.argmax()
a.argmin()
```

Along axes:

```python
a.argmax(axis=1)
```

## 10.4 Percentiles / quantiles

```python
np.percentile(a, 50)
np.quantile(a, 0.5)
np.median(a)
```

## 10.5 NaN-aware reductions

```python
np.nanmean(a)
np.nansum(a)
np.nanmin(a)
np.nanmax(a)
np.nanstd(a)
```

Use these when your float arrays contain missing values represented by `np.nan`.

---

## 11) Array manipulation

## 11.1 Concatenation and stacking

### Concatenate along an existing axis

```python
np.concatenate([a, b], axis=0)
```

### Convenience stackers

```python
np.stack([a, b], axis=0)   # creates a new axis
np.vstack([a, b])
np.hstack([a, b])
np.dstack([a, b])
np.column_stack([a, b])
```

### Difference between `concatenate` and `stack`

- `concatenate`: joins along an **existing** axis
- `stack`: joins along a **new** axis

---

## 11.2 Splitting

```python
np.split(a, 3)
np.array_split(a, 3)
np.vsplit(x, 2)
np.hsplit(x, 2)
```

---

## 11.3 Repeating and tiling

```python
np.repeat([1, 2, 3], 2)        # [1, 1, 2, 2, 3, 3]
np.tile([1, 2, 3], 2)          # [1, 2, 3, 1, 2, 3]
```

- `repeat` repeats elements
- `tile` repeats a block/pattern

---

## 11.4 Inserting, deleting, appending

```python
np.insert(a, 1, 99)
np.delete(a, [0, 2])
np.append(a, [7, 8])
```

These usually return **new arrays**.

---

## 11.5 Reordering / flipping / rolling

```python
np.sort(a)
np.argsort(a)
np.flip(a)
np.fliplr(x)
np.flipud(x)
np.roll(a, shift=2)
```

---

## 12) Sorting, searching, and set operations

## 12.1 Sorting

```python
np.sort(a)
a.sort()    # in-place method
np.argsort(a)
```

Sort by axis:

```python
np.sort(x, axis=1)
```

Stable sorting can be requested with appropriate `kind`/`stable` options depending on the function version.

## 12.2 Searching

```python
np.argmax(a)
np.argmin(a)
np.searchsorted(sorted_a, 5)
np.where(a > 0)
np.nonzero(a)
np.count_nonzero(a)
```

## 12.3 Unique and set routines

```python
np.unique(a)
np.intersect1d(a, b)
np.union1d(a, b)
np.setdiff1d(a, b)
np.setxor1d(a, b)
np.isin(a, values)
```

---

## 13) Linear algebra essentials

NumPy has basic linear algebra in `np.linalg`.

## 13.1 Matrix multiplication

```python
A @ B
np.matmul(A, B)
```

This is **not** elementwise multiplication.

### Elementwise multiplication

```python
A * B
```

### Dot products

```python
np.dot(a, b)
np.vdot(a, b)
```

### Inner / outer

```python
np.inner(a, b)
np.outer(a, b)
```

## 13.2 Common linear algebra functions

```python
np.linalg.inv(A)
np.linalg.det(A)
np.linalg.solve(A, b)
np.linalg.eig(A)
np.linalg.eigh(A)          # Hermitian / symmetric case
np.linalg.svd(A)
np.linalg.qr(A)
np.linalg.norm(A)
np.linalg.matrix_rank(A)
np.linalg.pinv(A)
```

### Practical guidance

- prefer `np.linalg.solve(A, b)` over `np.linalg.inv(A) @ b`
- `eigh` is preferred for symmetric / Hermitian matrices
- SVD is fundamental for low-rank approximations and numerical stability

---

## 14) Random number generation

Modern NumPy random usage is based on `Generator`.

## 14.1 Recommended style

```python
rng = np.random.default_rng(42)
```

This is preferred over the old global random API for new code.

## 14.2 Common methods

```python
rng.random((2, 3))
rng.integers(0, 10, size=5)
rng.normal(loc=0, scale=1, size=1000)
rng.uniform(0, 1, size=10)
rng.choice([10, 20, 30], size=5, replace=True)
rng.permutation(10)
rng.shuffle(arr)
```

## 14.3 Reproducibility

Using a seed gives repeatable pseudo-random sequences:

```python
rng = np.random.default_rng(123)
```

---

## 15) FFT basics

NumPy includes FFT support in `np.fft`.

## 15.1 Core functions

```python
np.fft.fft(x)
np.fft.ifft(X)
np.fft.fft2(x)
np.fft.ifft2(X)
np.fft.fftn(x)
np.fft.fftshift(X)
np.fft.fftfreq(n, d=1.0)
```

### Key idea

- `fft` transforms from time/space domain to frequency domain
- `ifft` transforms back

### Notes

- FFT works on complex numbers too
- power-of-2 sizes are often most efficient

---

## 16) File I/O and persistence

## 16.1 NumPy binary formats

```python
np.save("a.npy", a)
a2 = np.load("a.npy")
```

Multiple arrays:

```python
np.savez("data.npz", a=a, b=b)
np.savez_compressed("data_compressed.npz", a=a, b=b)
```

## 16.2 Text I/O

```python
np.savetxt("data.txt", a)
x = np.loadtxt("data.txt")
```

Other useful readers:

```python
np.genfromtxt(...)
np.fromfile(...)
```

`genfromtxt` is useful when text data has missing values or mixed parsing needs.

## 16.3 Memory mapping

For large arrays:

```python
m = np.memmap("big.dat", dtype=np.float32, mode="r", shape=(1000, 1000))
```

or through NumPy format helpers:

```python
from numpy.lib.format import open_memmap
```

Memory mapping lets you work with large arrays on disk without loading everything into RAM at once.

## 16.4 Security / portability note

When loading `.npy/.npz`, prefer:

```python
np.load(path, allow_pickle=False)
```

unless you intentionally need object arrays that require pickling.

---

## 17) Copies, views, and memory model

This is one of the most important NumPy topics.

## 17.1 View

A **view** shares the same underlying data buffer.

Changing the view changes the original data.

```python
a = np.arange(6)
v = a[1:4]
v[0] = 99
```

## 17.2 Copy

A **copy** has separate memory.

```python
c = a.copy()
```

## 17.3 Common operations and copy behavior

### Usually views
- basic slicing
- transpose / `T` (often)
- `reshape` (when possible)
- `ravel` (when possible)

### Usually copies
- fancy indexing
- boolean indexing
- `flatten`
- explicit `.copy()`
- many operations that require reorganization of memory

## 17.4 `base` attribute

```python
b.base
```

If not `None`, the array may be viewing another object’s memory.

## 17.5 Why this matters

- correctness: editing one array may unexpectedly change another
- memory: views are cheap; copies can be expensive
- performance: avoiding unnecessary copies matters a lot

---

## 18) Memory layout, contiguity, and strides

NumPy arrays map multidimensional indices to linear memory.

## 18.1 Contiguous layouts

- **C-order**: row-major
- **F-order**: column-major

Many arrays are C-contiguous; some are Fortran-contiguous.

```python
a.flags
```

Useful fields include contiguity and writeability flags.

## 18.2 Strides

`strides` tell you how many bytes to move in memory when stepping along each axis.

You usually do not manipulate strides directly in normal NumPy work, but they explain why:
- slicing can be a view
- transpose can be cheap
- some operations become non-contiguous and slower

## 18.3 Performance implication

Operations on contiguous arrays are often faster than on heavily strided arrays.

---

## 19) Iteration

Vectorization is preferred, but iteration tools still matter.

## 19.1 Plain iteration

```python
for row in a:
    ...
```

1-D iteration yields elements; higher-dimensional iteration yields subarrays along axis 0.

## 19.2 Flat iteration

```python
for x in a.flat:
    ...
```

## 19.3 Index-aware iteration

```python
for idx, value in np.ndenumerate(a):
    ...
```

## 19.4 Multi-array iteration with `nditer`

```python
for x in np.nditer(a):
    ...
```

Useful for advanced controlled iteration, buffering, and multi-array coordination, but most everyday NumPy code should prefer vectorized expressions.

---

## 20) Boolean logic, masking, and conditional computation

## 20.1 Boolean arrays

Comparisons create boolean arrays:

```python
mask = a > 0
```

## 20.2 Conditional selection

```python
np.where(a > 0, a, 0)
```

This means:
- keep `a` where condition is true
- otherwise use `0`

## 20.3 Filtering invalid float data with NaNs

```python
valid = np.isfinite(a)
a[valid]
```

## 20.4 Masked arrays (`numpy.ma`)

Masked arrays represent data plus a mask for invalid / missing entries.

```python
import numpy.ma as ma

x = np.array([1, 2, 3, -1, 5])
mx = ma.masked_array(x, mask=[0, 0, 0, 1, 0])
mx.mean()
```

Important idea:
- masked entries are excluded from many computations

### Common masked-array helpers

```python
ma.masked_array(data, mask=...)
ma.masked_invalid(a)
ma.filled(mx, fill_value=0)
```

### When to use what

- use `np.nan` for missing numeric values in floating arrays
- use `numpy.ma` when you need an explicit mask model

---

## 21) Strings, bytes, and text-like arrays

NumPy is mainly numerical, but it also supports string-like data.

## 21.1 Fixed-width strings / bytes

Examples:
- Unicode strings
- bytestrings

```python
np.array(["cat", "dog"], dtype="U3")
np.array([b"a", b"bb"], dtype="S2")
```

### Important caveat

Fixed-width string dtypes can truncate values that are longer than the declared width.

## 21.2 Variable-width strings

Modern NumPy also provides `StringDType` for variable-width string data.

### Practical note

For heavy text processing, Python strings, pandas, or other text tools are often a better fit. NumPy string arrays are mostly useful when array semantics matter.

---

## 22) Structured arrays and record-like data

Structured arrays allow each element to have named fields with possibly different dtypes.

```python
dt = np.dtype([("name", "U10"), ("age", np.int32), ("weight", np.float64)])
people = np.array(
    [("Ana", 25, 55.2), ("Ben", 31, 72.5)],
    dtype=dt
)

people["age"]
people["name"]
```

## 22.1 When they are useful

- binary / structured file formats
- record-like scientific data
- interoperating with legacy systems

## 22.2 Caveat

Structured arrays are powerful, but for table-like analytics, **pandas** is often more convenient.

---

## 23) Mathematical building blocks you should know

These are core NumPy function families.

## 23.1 Elementwise math

```python
np.abs(a)
np.sign(a)
np.sqrt(a)
np.square(a)
np.power(a, 3)
np.exp(a)
np.log(a)
np.log10(a)
```

## 23.2 Trigonometric

```python
np.sin(a)
np.cos(a)
np.tan(a)
np.arcsin(a)
np.arccos(a)
np.arctan(a)
```

## 23.3 Rounding

```python
np.round(a)
np.floor(a)
np.ceil(a)
np.trunc(a)
```

## 23.4 Clipping

```python
np.clip(a, 0, 1)
```

## 23.5 Differences and integration-like accumulations

```python
np.diff(a)
np.cumsum(a)
np.trapezoid(y, x)
```

`np.trapezoid` is the modern NumPy trapezoidal-integration helper.

---

## 24) Array comparison and testing

## 24.1 Exact equality

```python
np.array_equal(a, b)
```

## 24.2 Approximate equality for floats

```python
np.allclose(a, b)
np.isclose(a, b)
```

Use approximate checks for floating-point results.

---

## 25) Advanced but very useful concepts

## 25.1 `einsum`

Einstein summation notation can express many tensor operations compactly.

```python
np.einsum("ij,jk->ik", A, B)   # matrix multiplication
np.einsum("i,i->", a, b)       # dot product
```

This is powerful for:
- tensor contractions
- batched linear algebra
- avoiding awkward reshape/transposes

## 25.2 `where=` and `out=` parameters

Many ufuncs support:

```python
np.divide(a, b, out=np.zeros_like(a, dtype=float), where=b != 0)
```

This helps:
- avoid invalid operations
- avoid temporary arrays
- improve performance

## 25.3 Broadcasting with singleton axes

A huge amount of advanced NumPy boils down to:
- reshape
- add singleton axes
- let broadcasting do the work

## 25.4 `meshgrid`

Useful for coordinate grids:

```python
x = np.linspace(-1, 1, 5)
y = np.linspace(-1, 1, 4)
X, Y = np.meshgrid(x, y)
```

## 25.5 `ogrid` / `mgrid`

Convenient grid-generation helpers:

```python
np.ogrid[0:3, 0:4]
np.mgrid[0:3, 0:4]
```

---

## 26) Interoperability and ecosystem context

NumPy is the foundation for much of the scientific Python stack.

It interoperates with:
- pandas
- SciPy
- scikit-learn
- matplotlib
- PyTorch / JAX / CuPy (with differing levels of compatibility and conversion tools)

### Important interfaces

- buffer protocol
- array interface
- `__array__`
- `__array_function__`
- `__array_ufunc__`

As a user, the most common practical point is that many libraries accept or return NumPy arrays directly.

---

## 27) Typing with NumPy

Static typing support exists through `numpy.typing`.

```python
import numpy.typing as npt

def normalize(x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    return x / np.linalg.norm(x)
```

### Practical note

Typing can express dtype reasonably well, but exact shape typing is still more limited in normal everyday use than dtype typing.

---

## 28) Common performance rules

## 28.1 Prefer vectorization over Python loops

Good:

```python
y = x * 2 + 1
```

Less efficient:

```python
y = np.empty_like(x)
for i in range(len(x)):
    y[i] = x[i] * 2 + 1
```

## 28.2 Avoid unnecessary copies

Watch out for:
- fancy indexing
- boolean indexing
- repeated concatenation in loops
- accidental dtype conversions

## 28.3 Preallocate when possible

Better:

```python
out = np.empty((n, m))
```

and fill it, instead of repeatedly growing arrays.

## 28.4 Use the right dtype

- smaller dtype -> less memory
- but do not sacrifice required precision

## 28.5 Be careful with large temporaries

Expression like:

```python
((A - B) ** 2).sum(axis=1)
```

is often fine, but for very large arrays it may create temporary arrays. In advanced performance-sensitive code, use:
- `out=`
- in-place ops when safe
- chunking
- specialized routines

---

## 29) Common mistakes and gotchas

## 29.1 Confusing `*` with matrix multiplication

- `*` = elementwise multiply
- `@` = matrix multiply

## 29.2 Forgetting view vs copy

Basic slicing can modify original data.

## 29.3 Using Python `and` / `or` with arrays

Wrong:

```python
(a > 0) and (a < 10)
```

Right:

```python
(a > 0) & (a < 10)
```

## 29.4 Comparing floats exactly

Use `np.allclose`, not `==`, for most computed float results.

## 29.5 Integer division / dtype surprises

```python
np.array([1, 2, 3]) / 2
```

returns floating results, but other operations may keep integer dtype depending on function and context.

## 29.6 Shape mismatch in broadcasting

Always inspect `shape`.

## 29.7 Using object dtype accidentally

```python
np.array([1, "a"])
```

creates a non-numeric array, often not what you want.

## 29.8 Repeated `np.append` in loops

This is inefficient because arrays are fixed-size blocks; repeated appends create repeated new arrays.

## 29.9 Assuming `reshape` always copies or always views

It can do either. Treat result-sharing carefully.

## 29.10 Ignoring NaNs

Regular reductions like `np.mean` do **not** ignore NaNs. Use `np.nanmean` when needed.

---

## 30) Very important conceptual distinctions

## 30.1 Array scalar vs Python scalar

```python
x = np.array([1, 2, 3])
type(x[0])     # often a NumPy scalar type
```

This is not always the same as a plain Python `int` or `float`.

## 30.2 Shape `(n,)` vs `(n, 1)` vs `(1, n)`

These are different:

- `(n,)` = 1-D array
- `(n, 1)` = column-like 2-D array
- `(1, n)` = row-like 2-D array

This distinction matters a lot in broadcasting and matrix multiplication.

## 30.3 In-place vs out-of-place operations

```python
a += 1      # in-place when possible
a = a + 1   # creates a new array
```

Behavior may differ with dtype casting rules.

---

## 31) Tiny revision cheat sheet

## Create
```python
np.array(...)
np.asarray(...)
np.zeros(shape)
np.ones(shape)
np.full(shape, value)
np.empty(shape)
np.arange(start, stop, step)
np.linspace(start, stop, num)
```

## Inspect
```python
a.shape
a.ndim
a.size
a.dtype
a.itemsize
a.nbytes
```

## Reshape
```python
a.reshape(...)
a.ravel()
a.flatten()
a.T
np.transpose(a)
np.expand_dims(a, axis)
np.squeeze(a)
```

## Select
```python
a[i]
a[i:j:k]
a[:, 1]
a[a > 0]
a[[0, 2, 4]]
np.where(cond, x, y)
```

## Compute
```python
a + b
a * b
a @ b
np.sqrt(a)
np.exp(a)
np.log(a)
np.maximum(a, b)
```

## Reduce
```python
a.sum(axis=...)
a.mean(axis=...)
a.max(axis=...)
a.argmax(axis=...)
np.nanmean(a)
```

## Manipulate
```python
np.concatenate(...)
np.stack(...)
np.split(...)
np.repeat(...)
np.tile(...)
np.sort(...)
np.argsort(...)
np.unique(...)
```

## Linear algebra
```python
np.linalg.solve(A, b)
np.linalg.inv(A)
np.linalg.svd(A)
np.linalg.eig(A)
np.linalg.norm(A)
```

## Random
```python
rng = np.random.default_rng(seed)
rng.random(...)
rng.integers(...)
rng.normal(...)
rng.choice(...)
```

## I/O
```python
np.save(...)
np.load(...)
np.savez(...)
np.savetxt(...)
np.loadtxt(...)
```

---

## 32) How to study NumPy efficiently

A strong study order is:

1. `ndarray` basics  
2. shape / axis / reshape  
3. indexing and slicing  
4. broadcasting  
5. ufuncs and vectorization  
6. reductions / statistics  
7. stacking / splitting / sorting / set ops  
8. dtype / casting / NaN handling  
9. linear algebra and random  
10. copies vs views and performance

If you truly understand:
- shape
- axis
- broadcasting
- dtype
- indexing
- view vs copy

then most of NumPy becomes much easier.

---

## 33) Final summary

The **most important NumPy concepts** are:

- `ndarray` as a homogeneous N-dimensional array
- shape / axis / ndim
- dtype and casting
- indexing: basic, fancy, boolean
- reshape / transpose / dimension manipulation
- broadcasting
- ufuncs and vectorization
- reductions and statistics
- copies vs views
- memory layout and performance
- linear algebra, random generation, FFT, and I/O
- special array kinds: strings, structured arrays, masked arrays

If you master those, you can read and write most real NumPy code confidently.

---

## 34) References used for accuracy

These notes were checked against the official NumPy documentation (stable manual, current as of NumPy 2.4 docs):

- NumPy User Guide: https://numpy.org/doc/stable/user/
- NumPy fundamentals: https://numpy.org/doc/stable/user/basics.html
- Array creation: https://numpy.org/doc/stable/user/basics.creation.html
- Indexing on ndarrays: https://numpy.org/doc/stable/user/basics.indexing.html
- Data types: https://numpy.org/doc/stable/user/basics.types.html
- Broadcasting: https://numpy.org/doc/stable/user/basics.broadcasting.html
- Copies and views: https://numpy.org/doc/stable/user/basics.copies.html
- Strings and bytes: https://numpy.org/doc/stable/user/basics.strings.html
- Structured arrays: https://numpy.org/doc/stable/user/basics.rec.html
- Ufunc basics: https://numpy.org/doc/stable/user/basics.ufuncs.html
- Reading and writing files: https://numpy.org/doc/stable/user/how-to-io.html
- Random Generator: https://numpy.org/doc/stable/reference/random/generator.html
- Masked arrays: https://numpy.org/doc/stable/reference/maskedarray.generic.html
- NumPy module structure: https://numpy.org/doc/stable/reference/module_structure.html
- FFT reference: https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html
- Type promotion: https://numpy.org/doc/stable/reference/arrays.promotion.html