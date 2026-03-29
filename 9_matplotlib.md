# Matplotlib (Python) — Complete Revision Guide

> A comprehensive Markdown study guide for revising the **important concepts of Matplotlib**.
>
> This guide is organized around **concepts, mental models, and common workflows** rather than trying to list every single function in the library. It covers the major ideas, APIs, plot families, styling systems, layout systems, interactivity, animation, performance, and output/export topics you are expected to know for real Matplotlib work.
>
> Built against the **stable Matplotlib documentation** available in March 2026.

---

## Table of Contents

1. [What Matplotlib is](#1-what-matplotlib-is)
2. [The core mental model](#2-the-core-mental-model)
3. [Application interfaces: pyplot vs object-oriented API](#3-application-interfaces-pyplot-vs-object-oriented-api)
4. [Creating figures and axes](#4-creating-figures-and-axes)
5. [The anatomy of a figure](#5-the-anatomy-of-a-figure)
6. [Artists: the real building blocks](#6-artists-the-real-building-blocks)
7. [Basic plotting methods and plot families](#7-basic-plotting-methods-and-plot-families)
8. [Working with data inputs](#8-working-with-data-inputs)
9. [Axis limits, autoscaling, aspect, and margins](#9-axis-limits-autoscaling-aspect-and-margins)
10. [Ticks, tick locators, and formatters](#10-ticks-tick-locators-and-formatters)
11. [Scales and transformations](#11-scales-and-transformations)
12. [Text, labels, titles, annotations, and math](#12-text-labels-titles-annotations-and-math)
13. [Legends](#13-legends)
14. [Colors, colormaps, normalization, and colorbars](#14-colors-colormaps-normalization-and-colorbars)
15. [Images, raster data, and field plots](#15-images-raster-data-and-field-plots)
16. [Patches, collections, paths, and path effects](#16-patches-collections-paths-and-path-effects)
17. [Spines, grids, reference lines, and secondary axes](#17-spines-grids-reference-lines-and-secondary-axes)
18. [Layout systems](#18-layout-systems)
19. [Styles, rcParams, and configuration](#19-styles-rcparams-and-configuration)
20. [Dates, strings, categorical data, and units](#20-dates-strings-categorical-data-and-units)
21. [Multiple axes patterns](#21-multiple-axes-patterns)
22. [Interactive plotting](#22-interactive-plotting)
23. [Event handling, picking, and widgets](#23-event-handling-picking-and-widgets)
24. [Animations](#24-animations)
25. [3D plotting and projections](#25-3d-plotting-and-projections)
26. [Backends, canvases, renderers, and GUI embedding](#26-backends-canvases-renderers-and-gui-embedding)
27. [Saving and exporting figures](#27-saving-and-exporting-figures)
28. [Performance optimization](#28-performance-optimization)
29. [Notebook and ecosystem usage](#29-notebook-and-ecosystem-usage)
30. [Common mistakes and best practices](#30-common-mistakes-and-best-practices)
31. [A compact practical checklist](#31-a-compact-practical-checklist)
32. [High-value APIs to remember](#32-high-value-apis-to-remember)
33. [Advanced topics worth knowing exist](#33-advanced-topics-worth-knowing-exist)
34. [Suggested revision order](#34-suggested-revision-order)

---

## 1. What Matplotlib is

Matplotlib is Python’s general-purpose plotting library for creating **static, animated, and interactive visualizations**.

It is especially strong when you need:

- full control over plot structure and styling
- publication-quality figures
- deep customization of axes, ticks, labels, legends, and layouts
- integration with NumPy, pandas, Jupyter, and GUI applications
- export to raster and vector formats

It can produce:

- line plots
- scatter plots
- bar charts
- histograms
- box plots and violin plots
- heatmaps and images
- contour plots
- vector-field plots (`quiver`, `streamplot`)
- pie charts
- polar plots
- simple 3D plots
- animations
- interactive figures

---

## 2. The core mental model

If you remember only one thing, remember this:

**Matplotlib draws Artists onto Axes, and Axes live inside a Figure.**

### Main objects

- **Figure**: the top-level container (entire window/page/canvas)
- **Axes**: one plotting area, usually what people casually call a “plot” or “subplot”
- **Axis**: the x-axis or y-axis object attached to an Axes; handles ticks, tick labels, scale, locators, and formatters
- **Artist**: almost every visible thing in Matplotlib
- **Canvas / Renderer / Backend**: the machinery that displays or writes the figure

### Conceptual hierarchy

```text
Figure
└── Axes
    ├── Axis (xaxis, yaxis)
    ├── Line2D / Patch / Collection / Text / Image / Legend / etc.
    └── other Artists
```

### Why this matters

Most confusion in Matplotlib comes from not distinguishing these terms:

- a **Figure** is not an **Axes**
- an **Axes** is not an **Axis**
- the things you see are usually **Artists**
- `pyplot` is just one way of managing Figures/Axes

---

## 3. Application interfaces: pyplot vs object-oriented API

Matplotlib has **two main styles of use**.

### A. The implicit `pyplot` style

`matplotlib.pyplot` keeps track of the “current” figure and axes.

```python
import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [1, 4, 9])
plt.xlabel("x")
plt.ylabel("y")
plt.show()
```

This is convenient for:

- quick exploration
- short scripts
- interactive use
- notebooks

### B. The explicit object-oriented (OO) style

You create a Figure and Axes, then call methods on them directly.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_xlabel("x")
ax.set_ylabel("y")
plt.show()
```

This is preferred for:

- anything non-trivial
- multiple subplots
- reusable code
- GUI applications
- predictable control

### Rule of thumb

Use:

- **OO API** for serious work
- `pyplot` mainly to create figures, subplots, and to show/save them

### Common `pyplot` state helpers

- `plt.gcf()` → get current figure
- `plt.gca()` → get current axes
- `plt.figure()` → create/select a figure
- `plt.subplots()` → create a figure and one or more axes
- `plt.show()` → display figures

---

## 4. Creating figures and axes

### The most common entry point: `plt.subplots()`

```python
fig, ax = plt.subplots()
```

For multiple plots:

```python
fig, axs = plt.subplots(2, 3, figsize=(10, 6), sharex=True, sharey=False)
```

### Important `subplots()` concepts

- `nrows`, `ncols`
- `figsize=(width, height)` in inches
- `sharex`, `sharey`
- `squeeze`
- `subplot_kw` for projection-specific options
- `gridspec_kw` for advanced layout control
- `width_ratios`, `height_ratios`

### Other ways to create axes

- `fig.add_subplot(...)`
- `fig.add_axes([left, bottom, width, height])`
- `fig.subplot_mosaic(...)`
- `fig.add_gridspec(...)`
- `SubFigure.subplots(...)` for nested layouts

### Figure-level options

- `figsize`
- `dpi`
- `facecolor`
- `edgecolor`
- `layout='constrained'` (modern automatic layout help)

### Example

```python
fig, ax = plt.subplots(figsize=(8, 4), dpi=120, layout="constrained")
```

---

## 5. The anatomy of a figure

A Matplotlib figure can contain many visible pieces:

- Figure background
- one or more Axes
- x-axis and y-axis
- axis labels
- title / suptitle
- tick marks and tick labels
- spines (border lines around axes)
- grid lines
- plot elements (lines, markers, patches, images, collections, text)
- legend
- colorbar
- annotations
- inset axes

### Useful Figure methods

- `fig.suptitle(...)`
- `fig.colorbar(...)`
- `fig.legend(...)`
- `fig.text(...)`
- `fig.savefig(...)`
- `fig.get_axes()`

### Useful Axes methods

- `ax.set_title(...)`
- `ax.set_xlabel(...)`
- `ax.set_ylabel(...)`
- `ax.plot(...)`
- `ax.scatter(...)`
- `ax.imshow(...)`
- `ax.legend(...)`
- `ax.grid(...)`
- `ax.set_xlim(...)`, `ax.set_ylim(...)`

---

## 6. Artists: the real building blocks

Almost everything visible is an **Artist**.

### Two broad Artist categories

1. **Primitive Artists**
   - `Line2D`
   - `Text`
   - `Patch`
   - `AxesImage`

2. **Container Artists**
   - `Figure`
   - `Axes`
   - `Axis`
   - `Legend`

### Key Artist ideas

- every artist has properties
- artists can be added, modified, removed
- artists have `zorder`
- artists can be clipped
- artists can be transformed
- artists may participate in legends
- artists can be rasterized in vector outputs

### Common Artist property types

- color / facecolor / edgecolor
- linewidth
- linestyle
- alpha
- marker
- visible
- label
- transform
- clip_on
- zorder

### Why Artists matter

When Matplotlib seems to “go beyond simple plotting”, you are usually working directly with Artists.

---

## 7. Basic plotting methods and plot families

Matplotlib has many plotting methods. Learn them by **plot family**, not by memorizing a giant flat list.

### 7.1 Lines and markers

#### `plot()`
General line plot, optionally with markers.

```python
ax.plot(x, y)
ax.plot(x, y, linestyle="--", marker="o")
```

Use for:

- time series
- curves
- trends
- multiple lines on one axes

#### Related ideas
- line style
- marker style
- linewidth
- alpha
- drawstyle
- color cycle

### 7.2 Scatter-like plots

#### `scatter()`
Marker positions with size/color mapping.

```python
ax.scatter(x, y, s=sizes, c=values, cmap="viridis")
```

Use for:
- point clouds
- relationship plots
- bubble charts

Difference from `plot(..., marker='o')`:
- `scatter()` can vary size and color per point more naturally
- `plot()` is lighter for simple markers/lines

### 7.3 Bar plots

- `bar()`
- `barh()`

Use for:
- categorical comparisons
- grouped bars
- stacked bars

Important ideas:
- bar positions and widths
- labels
- stacking via `bottom=...`
- error bars

### 7.4 Histograms and distributions

- `hist()`
- `stairs()`
- `boxplot()`
- `violinplot()`
- `eventplot()`

Use for:
- distributions
- variability
- outliers
- density shape comparison

Important concepts:
- bins
- normalization / density
- cumulative histograms
- orientation
- quartiles and whiskers

### 7.5 Area and range plots

- `fill_between()`
- `fill_betweenx()`
- `stackplot()`

Use for:
- confidence intervals
- ranges
- cumulative contribution displays

### 7.6 Error and uncertainty plots

- `errorbar()`

Use for:
- measurement uncertainty
- confidence/standard-error display
- asymmetric error bars

### 7.7 Step / stem plots

- `step()`
- `stem()`

Use for:
- piecewise constant signals
- discrete-time sequences

### 7.8 Pie plots

- `pie()`

Use with caution. Pie charts are supported, but often less effective than bars.

### 7.9 Statistical / aggregated plots

- histogram family
- box / violin
- hexbin
- error bars
- binned statistics-like visualizations

### 7.10 2D density and binning

- `hexbin()`
- histograms in 2D via `hist2d()`

Use when scatter has too many points.

### 7.11 Field / vector plots

- `quiver()`
- `barbs()`
- `streamplot()`

Use for:
- vector fields
- flow direction and magnitude

### 7.12 Contours and level sets

- `contour()`
- `contourf()`

Use for:
- level curves
- scalar fields
- topographic / scientific plots

### 7.13 Image-like and grid-based plots

- `imshow()`
- `matshow()`
- `pcolor()`
- `pcolormesh()`

Use for:
- matrices
- heatmaps
- raster grids
- image data

### 7.14 Triangle-based / irregular mesh plots

For unstructured triangular data there are `tricontour`, `tricontourf`, `tripcolor`, `triplot`, etc.

### 7.15 Specialized families you should know exist

- spectral plots
- spans (`axhspan`, `axvspan`)
- reference lines (`axhline`, `axvline`, `axline`)
- text/table overlays
- inset plots
- polar plots
- 3D plots

---

## 8. Working with data inputs

Matplotlib works with many input forms:

- Python lists
- tuples
- NumPy arrays
- pandas Series / Index / DataFrame columns
- masked arrays
- datetime objects
- strings / categories
- unit-aware objects in supported unit systems

### Basic expectation

Most plotting methods accept data convertible via `numpy.asarray(...)`.

### Labeled data with `data=`

```python
ax.plot("time", "value", data=df)
```

Useful with pandas DataFrames and dict-like objects.

### Broadcasting and shapes

Many plotting bugs come from shape mismatches.

Check:

- same length for `x` and `y`
- correct 2D array orientation
- whether a method expects centers or edges
- whether data are regular-grid or irregular-grid

### Missing values

Common approaches:

- `np.nan` breaks line segments in many line/image contexts
- masked arrays can explicitly mask data
- preprocessing with pandas/NumPy before plotting is often cleaner

---

## 9. Axis limits, autoscaling, aspect, and margins

### Limits

- `ax.set_xlim(left, right)`
- `ax.set_ylim(bottom, top)`

### Autoscaling

Matplotlib automatically chooses axis limits based on plotted data.

Useful methods:
- `ax.autoscale()`
- `ax.relim()`
- `ax.autoscale_view()`

These matter when artist data are updated after plotting.

### Margins

Add padding around data:

```python
ax.margins(x=0.05, y=0.1)
```

### Inverting axes

- `ax.invert_xaxis()`
- `ax.invert_yaxis()`

### Aspect ratio

Controls relation between x and y units on screen.

- `ax.set_aspect("auto")`
- `ax.set_aspect("equal")`

Useful for:
- maps
- geometry
- circles that should remain circles
- image displays

### `axis(...)`

Common shortcuts:

```python
ax.axis("equal")
ax.axis("off")
ax.axis("tight")
```

---

## 10. Ticks, tick locators, and formatters

Ticks are a major strength of Matplotlib.

### Manual tick control

- `ax.set_xticks(...)`
- `ax.set_yticks(...)`
- `ax.set_xticklabels(...)` (use carefully)
- `ax.tick_params(...)`

### Major vs minor ticks

Axes can have:

- major ticks
- minor ticks

Enable or customize minor ticks for finer visual structure.

### Locators

Locators decide **where** ticks go.

Examples from `matplotlib.ticker`:
- `AutoLocator`
- `MultipleLocator`
- `MaxNLocator`
- `LogLocator`
- `FixedLocator`
- `LinearLocator`
- `NullLocator`
- `AutoMinorLocator`

### Formatters

Formatters decide **how** tick labels look.

Examples:
- `ScalarFormatter`
- `FormatStrFormatter`
- `StrMethodFormatter`
- `FuncFormatter`
- `PercentFormatter`
- `LogFormatter`
- `FixedFormatter` (use carefully and usually with `FixedLocator`)

### Tick styling

```python
ax.tick_params(
    axis="both",
    which="major",
    direction="out",
    length=6,
    width=1,
    labelsize=10
)
```

### Important warning

Avoid casually calling `set_xticklabels(...)` without also fixing tick positions. Otherwise labels may drift when ticks change.

---

## 11. Scales and transformations

This is one of the most important advanced topics.

## 11.1 Scales

A **scale** is attached to an axis and transforms data before display.

### Built-in scales

- `linear` (default)
- `log`
- `symlog`
- `logit`
- custom scales

### Common methods

- `ax.set_xscale("log")`
- `ax.set_yscale("log")`
- `ax.semilogx(...)`
- `ax.semilogy(...)`
- `ax.loglog(...)`

### When to use
- `log`: exponential growth, orders of magnitude
- `symlog`: positive and negative values with log-like behavior away from zero
- `logit`: probabilities in (0, 1)

## 11.2 The transformations framework

Matplotlib uses a transformation system to move between coordinate systems.

### Coordinate systems you must know

- **data coordinates** → `ax.transData`
- **axes coordinates** → `ax.transAxes`
  - `(0, 0)` bottom-left of axes
  - `(1, 1)` top-right of axes
- **figure coordinates** → `fig.transFigure`
- **display coordinates** → final pixels/points on screen/canvas

### Why transforms matter

They let you place things:

- relative to data
- relative to axes size
- relative to the whole figure
- in screen space

### Example

```python
ax.text(0.02, 0.98, "note", transform=ax.transAxes, va="top")
```

This anchors text in the axes corner, regardless of data limits.

### Blended transforms

Used when one direction should follow data and the other should follow axes/figure space.

Very useful for:
- reference labels
- spans
- annotations aligned with axes frame

---

## 12. Text, labels, titles, annotations, and math

## 12.1 Basic text

- `ax.set_title(...)`
- `ax.set_xlabel(...)`
- `ax.set_ylabel(...)`
- `ax.text(x, y, "...")`
- `fig.text(x, y, "...")`

### Common text properties

- `fontsize`
- `fontfamily`
- `fontstyle`
- `fontweight`
- `color`
- `rotation`
- `ha` / `horizontalalignment`
- `va` / `verticalalignment`
- `bbox`

## 12.2 Title hierarchy

- axes title: `ax.set_title(...)`
- figure title: `fig.suptitle(...)`

## 12.3 Annotation

Annotations attach explanatory text to data.

```python
ax.annotate(
    "peak",
    xy=(x0, y0),
    xytext=(x1, y1),
    arrowprops={"arrowstyle": "->"}
)
```

Important annotation ideas:

- `xy`: target point
- `xytext`: text position
- `xycoords`: coordinate system for target
- `textcoords`: coordinate system for text
- `arrowprops`
- clipping behavior

## 12.4 Mathtext

Matplotlib supports TeX-like math syntax in strings using `$...$`.

```python
ax.set_title(r"$y = \sin(x)$")
```

### Mathtext vs `usetex`

- **Mathtext**: internal parser, lighter, works without a full LaTeX installation
- **`text.usetex=True`**: true LaTeX rendering, requires external LaTeX dependencies

Use `usetex` only when you really need full LaTeX behavior and have the environment configured.

## 12.5 Text boxes

```python
ax.text(
    0.05, 0.95, "info",
    transform=ax.transAxes,
    va="top",
    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8}
)
```

---

## 13. Legends

A legend explains labeled artists.

### Standard workflow

```python
ax.plot(x, y, label="signal")
ax.legend()
```

### Key legend concepts

- artists need labels
- labels starting with `_` are ignored by default
- you can pass handles and labels manually
- figure-level legends are possible with `fig.legend(...)`

### Common legend controls

- `loc`
- `title`
- `ncols`
- `frameon`
- `fontsize`
- `bbox_to_anchor`

### Manual legend creation

```python
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels)
```

### When legends get tricky

Legends can be built from:

- lines
- patches
- collections
- proxy artists

Proxy artists are useful when the plotted object itself is awkward to show directly in the legend.

---

## 14. Colors, colormaps, normalization, and colorbars

This is a major revision area.

## 14.1 Specifying colors

Matplotlib accepts many color specifications:

- named colors (`"red"`, `"tab:blue"`)
- hex strings (`"#1f77b4"`)
- grayscale strings (`"0.5"`)
- RGB / RGBA tuples
- shorthand single-letter colors (`"r"`, `"g"`, etc.; older but still supported)
- cycle colors like `"C0"`, `"C1"`

### Common color properties

- `color`
- `facecolor`
- `edgecolor`
- `markerfacecolor`
- `markeredgecolor`
- `alpha`

## 14.2 The default property cycle

If you do not specify colors, Matplotlib uses the default axes property cycle.

You can customize it with `axes.prop_cycle`.

## 14.3 Colormaps

Colormaps map scalar values to colors.

Types:
- **sequential**
- **diverging**
- **cyclic**
- **qualitative**
- **miscellaneous/specialized**

### Choosing colormaps conceptually

- sequential → ordered magnitude
- diverging → deviation around a meaningful center
- cyclic → angles / wrapped phases
- qualitative → categories

## 14.4 Normalization

Matplotlib usually maps scalar data to color in two steps:

1. **normalize** data to `[0, 1]`
2. map those normalized values through a colormap

Default normalization is linear:
- `matplotlib.colors.Normalize(vmin, vmax)`

Other important norms include:
- `LogNorm`
- `SymLogNorm`
- `TwoSlopeNorm`
- `CenteredNorm`
- `BoundaryNorm`
- `PowerNorm`

### Why norms matter

A wrong norm can distort interpretation even if the colormap is good.

## 14.5 ScalarMappable

A `ScalarMappable` conceptually connects:

- data values
- a colormap (`cmap`)
- a normalization (`norm`)

Colorbars are built from mappables.

## 14.6 Colorbars

A colorbar explains scalar-to-color mapping.

```python
im = ax.imshow(data, cmap="viridis")
fig.colorbar(im, ax=ax)
```

Important ideas:
- colorbar needs a mappable
- one colorbar can serve one or multiple axes
- ticks and labels can be customized
- standalone colorbars can be built from a dummy `ScalarMappable`

---

## 15. Images, raster data, and field plots

## 15.1 `imshow()`

Used to display regular raster/image-like data.

```python
ax.imshow(data, cmap="viridis", origin="lower")
```

### Important `imshow` concepts

- input can be:
  - 2D scalar array
  - RGB image
  - RGBA image
- `origin`
- `extent`
- `aspect`
- `interpolation`
- `cmap`, `norm`, `vmin`, `vmax`

### `origin` and `extent`

These are extremely important.

- `origin` controls where array index `[0, 0]` is displayed
- `extent` maps array bounds into data coordinates

## 15.2 `pcolor()` vs `pcolormesh()`

Both create pseudocolor plots, but `pcolormesh()` is generally preferred for performance.

Use when:
- data live on grid cells / quadrilaterals
- you need edge/corner-based plotting

### Shape awareness

For `pcolormesh`, understand whether `X`, `Y` specify:
- cell centers
- cell edges/corners

Also understand `shading`.

## 15.3 `contour()` / `contourf()`

Use for level curves and filled contour regions.

Important ideas:
- contour levels
- line vs filled contour
- labeling contours with `clabel`
- consistent coordinate registration with images when combining with `imshow`

## 15.4 Matrix displays

- `matshow()` is a convenience for matrix visualization
- `imshow()` is the more general image tool

## 15.5 Vector fields

### `quiver()`
Arrows defined by positions and vector components.

### `streamplot()`
Continuous-looking flow lines for vector fields.

---

## 16. Patches, collections, paths, and path effects

## 16.1 Patches

Patches are filled or outlined 2D shapes.

Examples:
- `Rectangle`
- `Circle`
- `Ellipse`
- `Polygon`
- `FancyArrow`
- `Wedge`

Used for:
- custom overlays
- regions of interest
- diagrams
- manual visual construction

## 16.2 Collections

Collections efficiently draw many similar objects.

Examples:
- `PathCollection` (used by scatter)
- `LineCollection`
- `PatchCollection`

Important because they are often more efficient than lots of separate artists.

## 16.3 Paths

A `Path` is the low-level geometry underlying many patches and path-rendered artists.

It consists of:
- vertices
- path codes (move, line, curve, close)

Know this if you want custom shapes or clipping paths.

## 16.4 Path effects

Path effects add multi-stage rendering effects to path-based artists.

Examples:
- outlines around text
- strokes around lines
- shadows

Used for readability on complex backgrounds.

---

## 17. Spines, grids, reference lines, and secondary axes

## 17.1 Spines

Spines are the boundary lines of an Axes.

Access via:

```python
ax.spines["top"].set_visible(False)
```

Common uses:
- remove top/right spines
- reposition spines
- style plot borders

## 17.2 Grid lines

```python
ax.grid(True)
ax.grid(which="minor", alpha=0.3)
```

Use grids to support reading values, not to decorate excessively.

## 17.3 Reference lines and spans

Useful functions:
- `ax.axhline(...)`
- `ax.axvline(...)`
- `ax.axline(...)`
- `ax.axhspan(...)`
- `ax.axvspan(...)`

Use for:
- thresholds
- targets
- regions
- background emphasis

## 17.4 Secondary axes

- `ax.secondary_xaxis(...)`
- `ax.secondary_yaxis(...)`

Useful for transformed alternate units (for example, frequency ↔ period).

## 17.5 Twin axes

- `ax.twinx()`
- `ax.twiny()`

Use carefully. They can be powerful, but they can also mislead if scales are not clearly explained.

---

## 18. Layout systems

This is one of the most practical parts of Matplotlib.

## 18.1 Basic subplot grids

```python
fig, axs = plt.subplots(2, 2)
```

## 18.2 `GridSpec`

For fine control of subplot placement and ratios.

Use when:
- some plots should span multiple rows/columns
- subplot widths/heights differ
- layout is irregular

## 18.3 `subplot_mosaic`

A high-level way to create labeled layouts.

```python
fig, axd = plt.subplot_mosaic(
    [["main", "main"],
     ["left", "right"]],
    layout="constrained"
)
```

Very good for dashboard-like arrangements.

## 18.4 SubFigure

Useful for nested figure structures.

## 18.5 Automatic layout engines

### `constrained_layout`
Modern, more capable automatic layout system.

Best default choice for many cases.

### `tight_layout`
Older, useful, but generally less capable than constrained layout.

### Practical guideline
Prefer:

```python
fig, ax = plt.subplots(layout="constrained")
```

or:

```python
fig.set_constrained_layout(True)
```

Use `tight_layout()` if needed for legacy code or simple cleanup.

## 18.6 Inset axes

Create small zoomed or supplemental plots inside another axes.

Typical tools come from `mpl_toolkits.axes_grid1.inset_locator`.

---

## 19. Styles, rcParams, and configuration

This is how you control defaults.

Matplotlib customization works at three levels:

1. runtime `rcParams`
2. style sheets
3. `matplotlibrc` file

Precedence:
- runtime `rcParams` override style sheets
- style sheets override `matplotlibrc`

## 19.1 `rcParams`

`matplotlib.rcParams` is a dict-like global settings store.

Examples:
- figure size defaults
- font defaults
- line widths
- default colormap
- DPI
- grid visibility
- property cycle

### Example

```python
import matplotlib as mpl
mpl.rcParams["figure.dpi"] = 120
mpl.rcParams["axes.grid"] = True
```

## 19.2 Style sheets

```python
plt.style.use("ggplot")
```

Good for switching coherent visual themes quickly.

### Context managers

```python
with plt.style.context("seaborn-v0_8-whitegrid"):
    ...
```

## 19.3 `matplotlibrc`

Persistent project/user-level defaults.

## 19.4 `rc_context`

Temporary rc configuration block.

```python
with mpl.rc_context({"lines.linewidth": 3}):
    ...
```

## 19.5 Property cycler

Defines default cycling through colors and potentially other properties.

Can be customized with `cycler`.

---

## 20. Dates, strings, categorical data, and units

## 20.1 Dates

Matplotlib supports plotting `datetime` objects and has date-specific locators/formatters.

### Important fact
Internally, Matplotlib represents dates as floating-point numbers measuring days from a default epoch.

### Useful date tools
From `matplotlib.dates`:
- `AutoDateLocator`
- `AutoDateFormatter`
- `ConciseDateFormatter`
- `DayLocator`
- `MonthLocator`
- `YearLocator`
- `DateFormatter`

### Typical workflow

```python
import matplotlib.dates as mdates

ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
```

## 20.2 Strings / categorical plotting

If you pass strings as positions or categories, Matplotlib can map them to categorical positions automatically.

Common with:
- bar charts
- line charts over named categories

## 20.3 Unit handling

Matplotlib has a unit conversion framework that allows plotting of certain non-plain-numeric data types through converters.

Important as a concept even if you do not implement converters yourself.

---

## 21. Multiple axes patterns

These patterns come up constantly.

### Shared axes

```python
fig, axs = plt.subplots(2, 1, sharex=True)
```

Useful for aligned comparisons.

### Twin axes
- same x, different y (`twinx`)
- same y, different x (`twiny`)

### Secondary axes
Better than twin axes when the second scale is just a mathematical transform of the first.

### Multiple figures
Use different figures when plots do not need to be visually compared side by side.

### Figure-level labels
For grouped subplot layouts, use:
- `fig.suptitle(...)`
- `fig.supxlabel(...)`
- `fig.supylabel(...)`

---

## 22. Interactive plotting

Matplotlib supports interactive figures in suitable backends.

## 22.1 Interactive mode

- `plt.ion()` → interactive mode on
- `plt.ioff()` → off

Interactive mode affects whether figures update immediately.

## 22.2 Showing figures

- `plt.show()` starts/uses the backend’s display behavior
- behavior differs slightly across environments

## 22.3 Updating plots

Common pattern:

```python
line.set_ydata(new_y)
fig.canvas.draw_idle()
fig.canvas.flush_events()
```

`draw_idle()` asks for a redraw when convenient.

## 22.4 Pausing

`plt.pause(interval)` can be useful for simple live updates, though it is not a substitute for proper GUI/event-loop design.

---

## 23. Event handling, picking, and widgets

## 23.1 Event handling

Matplotlib can react to:
- mouse press/release
- mouse movement
- key press/release
- scroll events
- draw/resize events
- pick events

### Connection pattern

```python
cid = fig.canvas.mpl_connect("button_press_event", callback)
```

### Event objects can provide
- pixel position
- data coordinates (when inside axes)
- which axes the event occurred in
- key/button info

## 23.2 Picking

Picking lets users click/select artists.

Typical steps:
- enable picking on an artist
- connect to `"pick_event"`

## 23.3 Widgets

Matplotlib includes widget classes such as:
- `Button`
- `Slider`
- `CheckButtons`
- `RadioButtons`
- `TextBox`
- `Cursor`
- selectors like rectangle/span selectors

Useful for lightweight interactive control panels inside a figure.

---

## 24. Animations

Matplotlib’s animation module produces frame sequences.

## 24.1 Main animation concepts

- a figure is updated frame by frame
- an animation object manages updates
- you can display animations interactively or save them

## 24.2 Common API

- `FuncAnimation`
- `ArtistAnimation`

### Typical `FuncAnimation` pattern

```python
from matplotlib.animation import FuncAnimation

ani = FuncAnimation(fig, update, frames=100, interval=50, blit=False)
```

### Key parameters

- `update` function
- `frames`
- `interval`
- `repeat`
- `blit`

## 24.3 Blitting

Blitting can drastically improve interactive animation performance by redrawing only the changing parts.

It is powerful but can add complexity.

## 24.4 Saving animations

You can save with available writers such as ffmpeg-based writers, depending on your environment.

---

## 25. 3D plotting and projections

## 25.1 `mplot3d`

Matplotlib ships with `mpl_toolkits.mplot3d` for simple 3D plotting.

Example:

```python
from mpl_toolkits.mplot3d import Axes3D  # old import pattern often seen
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
```

### Common 3D methods
- `plot`
- `scatter`
- `plot_surface`
- `plot_wireframe`
- `contour`
- `bar`
- text/annotation methods

### Important note
Matplotlib 3D is convenient and integrated, but it is not the fastest or most feature-rich dedicated 3D library.

## 25.2 View angles

3D viewpoint is controlled by:
- elevation
- azimuth
- roll

## 25.3 Polar plots

Use projection `"polar"` for polar coordinates.

```python
fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
```

## 25.4 Geographic projections

Matplotlib has some built-in projection support and can be paired with specialized libraries for geospatial work.

---

## 26. Backends, canvases, renderers, and GUI embedding

This is the architectural side of Matplotlib.

## 26.1 Backend

A backend is responsible for:

- displaying figures on screen
- or writing them to files
- or both

### Broad categories

- **interactive backends** (GUI / notebook display)
- **non-interactive backends** (file output)

Examples you should conceptually know:
- Agg
- PDF
- SVG
- PS
- PGF
- GUI backends like Qt/Tk/macOS variants

## 26.2 Canvas

The canvas is the drawing surface for a figure.

## 26.3 Renderer

The renderer turns artists into actual drawn output.

## 26.4 Why users should care

Backend choice affects:
- whether plots appear in a window
- interactivity
- notebook behavior
- file formats
- text rendering and output characteristics

## 26.5 GUI embedding

Matplotlib can be embedded in GUI frameworks such as:
- Qt
- Tk
- wx
- GTK

For embedding, prefer the **explicit OO API**, not procedural `pyplot` scripting style.

---

## 27. Saving and exporting figures

Use:

```python
fig.savefig("plot.png")
```

or:

```python
plt.savefig("plot.pdf")
```

Prefer `fig.savefig(...)` when working in OO style.

## 27.1 Raster vs vector output

### Raster formats
- PNG
- JPG/JPEG
- TIFF (environment/backend dependent)

Best for:
- images
- pixel-based output
- web use

### Vector formats
- PDF
- SVG
- PS
- EPS
- PGF workflows

Best for:
- publication graphics
- scaling without pixelation
- line art and text

## 27.2 Important save options

- `dpi`
- `bbox_inches="tight"`
- `facecolor`
- `transparent=True`
- `pad_inches`
- `metadata`

### Example

```python
fig.savefig("figure.png", dpi=300, bbox_inches="tight")
```

## 27.3 Practical export rules

- use **PNG** for quick sharing
- use **SVG/PDF** for scalable vector needs
- use **high DPI** for raster publication output
- verify fonts and transparency in final target medium

---

## 28. Performance optimization

Matplotlib can be slow if misused at scale.

### High-impact optimization concepts

1. **avoid plotting millions of individual artists unnecessarily**
2. prefer collections for many similar objects
3. use `pcolormesh()` rather than slower alternatives in some grid cases
4. reduce marker count or use rasterization
5. simplify paths when appropriate
6. use blitting for interactive animation
7. avoid excessive alpha blending when possible
8. reuse artists and update data instead of rebuilding the entire plot

### Common performance techniques

- downsample before plotting
- use line simplification
- use marker subsampling via `markevery`
- rasterize dense artists inside otherwise vector figures
- turn off expensive decorations where unnecessary

### Updating existing artists

Much faster than recreating them repeatedly:

```python
line.set_data(x, y)
fig.canvas.draw_idle()
```

---

## 29. Notebook and ecosystem usage

Matplotlib is often used with:

- NumPy
- pandas
- Jupyter
- SciPy
- seaborn

### In notebooks

Common patterns:
- inline display
- interactive notebook backends depending on environment
- plotting from pandas objects

### With pandas

```python
df.plot()
```

Pandas often uses Matplotlib underneath, but direct Matplotlib gives more control.

### With seaborn

Seaborn builds higher-level statistical plotting on top of Matplotlib. Understanding Matplotlib makes seaborn customization much easier.

---

## 30. Common mistakes and best practices

## Mistakes

### 1. Mixing pyplot state and OO API chaotically
Pick a style. For serious code, mostly use OO.

### 2. Confusing Figure and Axes
Very common. Most plotting methods live on `Axes`.

### 3. Using `set_xticklabels()` carelessly
It often breaks when ticks move. Prefer proper locators/formatters.

### 4. Overusing twin axes
Can mislead readers and clutter figures.

### 5. Using pie charts where bars are clearer
Supported, but often not ideal.

### 6. Ignoring layout until the end
Use `layout="constrained"` early.

### 7. Using poor colormaps for the task
Choose sequential/diverging/cyclic/qualitative appropriately.

### 8. Not understanding `origin` / `extent` in images
This causes many image/contour alignment errors.

### 9. Recreating artists repeatedly in animations/live updates
Update existing artists instead.

### 10. Exporting vector graphics with huge dense point clouds
This can create giant files. Use rasterization selectively.

## Best practices

- start with `fig, ax = plt.subplots(...)`
- use OO methods on `ax`
- use `layout="constrained"` for many figures
- label plots clearly
- control ticks intentionally
- choose sensible colormaps
- use legends only when they add value
- save outputs explicitly with tested settings
- separate data preprocessing from plotting code
- write reusable helper functions for styling

---

## 31. A compact practical checklist

Before plotting, ask:

1. What kind of data do I have?
   - continuous?
   - categorical?
   - dates?
   - images/grid?
   - vector field?

2. What plot family fits the data?
   - line, scatter, bar, histogram, image, contour, etc.

3. Do I need one axes or a layout of many?

4. Should the API be OO?  
   Usually yes.

5. Are scale choices correct?
   - linear?
   - log?
   - diverging color norm?

6. Are ticks readable and meaningful?

7. Are labels, title, units, and legend clear?

8. Will this be viewed on screen, in a notebook, or in print?

9. Which output format is appropriate?
   - PNG?
   - SVG?
   - PDF?

10. Does the figure remain readable in grayscale / colorblind-safe contexts if relevant?

---

## 32. High-value APIs to remember

### Figure / subplot creation
- `plt.figure`
- `plt.subplots`
- `fig.add_subplot`
- `fig.add_axes`
- `fig.subplot_mosaic`
- `fig.add_gridspec`

### Core Axes plotting
- `ax.plot`
- `ax.scatter`
- `ax.bar`
- `ax.barh`
- `ax.hist`
- `ax.boxplot`
- `ax.violinplot`
- `ax.errorbar`
- `ax.fill_between`
- `ax.imshow`
- `ax.pcolormesh`
- `ax.contour`
- `ax.contourf`
- `ax.hexbin`
- `ax.quiver`
- `ax.streamplot`
- `ax.pie`

### Labels and styling
- `ax.set_title`
- `ax.set_xlabel`
- `ax.set_ylabel`
- `ax.legend`
- `ax.grid`
- `ax.tick_params`

### Limits / scale
- `ax.set_xlim`
- `ax.set_ylim`
- `ax.set_xscale`
- `ax.set_yscale`
- `ax.set_aspect`

### Text and annotation
- `ax.text`
- `ax.annotate`
- `fig.suptitle`
- `fig.text`

### Layout
- `tight_layout`
- constrained layout
- `GridSpec`
- `subplot_mosaic`

### Export
- `fig.savefig`

### Interactivity / animation
- `fig.canvas.mpl_connect`
- `FuncAnimation`

---

## 33. Advanced topics worth knowing exist

You do not need to master all of these immediately, but you should know they exist:

- custom locators and formatters
- custom scales
- custom projections
- custom artists
- backend authoring
- advanced path construction
- clipping paths
- custom legend handlers
- `axes_grid1`
- `axisartist`
- `toolmanager`
- full GUI embedding patterns
- unit converter implementation
- advanced text rendering with LaTeX/PGF

---

## 34. Suggested revision order

A strong revision sequence is:

1. Figure / Axes / Axis / Artist mental model
2. `pyplot` vs OO API
3. `subplots`, figure creation, and layout
4. line / scatter / bar / hist / image / contour families
5. labels, titles, legends
6. limits, ticks, locators, formatters
7. scales and transforms
8. colors, colormaps, norms, colorbars
9. images, `imshow`, `pcolormesh`, `contour`
10. styles and `rcParams`
11. dates and units
12. annotations and path effects
13. interactivity and widgets
14. animation
15. 3D, projections, backends, export, and performance

---

# Final summary

If you want a single sentence that captures Matplotlib:

> **Matplotlib is a Figure/Axes/Artist-based visualization system where you usually create a Figure and one or more Axes, add Artists through plotting methods, control scales/ticks/layout/style explicitly, and then render or export through an appropriate backend.**

That one sentence connects almost everything else in the library.

---

# Quick mini-cheat sheet

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

x = np.linspace(0, 10, 400)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
ax.plot(x, y, label="sin(x)", color="C0", linewidth=2)
ax.set_title("Example")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)
ax.legend()
fig.savefig("example.png", dpi=150)
plt.show()
```

This tiny example already uses many central ideas:

- `pyplot` creates the figure
- the OO API controls the axes
- line artist added via `plot`
- labels/title/grid/legend added as artists/configuration
- figure exported with `savefig`
- backend displays with `show`

---

# Source basis for this revision guide

This guide is aligned to the **stable Matplotlib documentation** and its main user-guide sections on:

- quick start and APIs
- figures, axes, artists, and backends
- ticks, scales, units, and dates
- colors, colormaps, norms, and colorbars
- annotations, text, mathtext, and transforms
- images, contours, and pseudocolor plots
- styles, rcParams, layout, event handling, animation, performance, projections, and toolkits


# Official documentation links

These are the main official references this guide was aligned to:

- Quick start guide: https://matplotlib.org/stable/users/explain/quick_start.html
- Matplotlib Application Interfaces (APIs): https://matplotlib.org/stable/users/explain/figure/api_interfaces.html
- Introduction to Figures: https://matplotlib.org/stable/users/explain/figure/figure_intro.html
- Introduction to Axes: https://matplotlib.org/stable/users/explain/axes/axes_intro.html
- Artists: https://matplotlib.org/stable/users/explain/artists/index.html
- Backends: https://matplotlib.org/stable/users/explain/figure/backends.html
- Axis ticks: https://matplotlib.org/stable/users/explain/axes/axes_ticks.html
- Axis scales: https://matplotlib.org/stable/users/explain/axes/axes_scales.html
- Plotting dates and strings: https://matplotlib.org/stable/users/explain/axes/axes_units.html
- Customizing with style sheets and rcParams: https://matplotlib.org/stable/users/explain/customizing.html
- Colors and colormaps: https://matplotlib.org/stable/users/explain/colors/index.html
- Choosing colormaps: https://matplotlib.org/stable/users/explain/colors/colormaps.html
- Colormap normalization: https://matplotlib.org/stable/users/explain/colors/colormapnorms.html
- Customized colorbars: https://matplotlib.org/stable/users/explain/colors/colorbar_only.html
- Annotations: https://matplotlib.org/stable/users/explain/text/annotations.html
- Text properties and layout: https://matplotlib.org/stable/users/explain/text/text_props.html
- Transformations tutorial: https://matplotlib.org/stable/users/explain/artists/transforms_tutorial.html
- Constrained layout guide: https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html
- Tight layout guide: https://matplotlib.org/stable/users/explain/axes/tight_layout_guide.html
- Interactive figures: https://matplotlib.org/stable/users/explain/figure/interactive.html
- Event handling and picking: https://matplotlib.org/stable/users/explain/figure/event_handling.html
- Animations: https://matplotlib.org/stable/users/explain/animations/animations.html
- Blitting: https://matplotlib.org/stable/users/explain/animations/blitting.html
- Performance: https://matplotlib.org/stable/users/explain/artists/performance.html
- mplot3d toolkit: https://matplotlib.org/stable/api/toolkits/mplot3d.html
- axes_grid1 toolkit: https://matplotlib.org/stable/users/explain/toolkits/axes_grid.html
