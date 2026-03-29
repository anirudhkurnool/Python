# Python Programming Language: Complete Concept Revision Guide

This guide is a **single-file revision handbook** for the most important concepts in modern Python. It is meant to help you **revise Python end to end**, with compact explanations, practical notes, and examples you can run.

**Target baseline:** modern Python 3.x, aligned with the current stable documentation stream (Python 3.14.x at the time this guide was prepared).

---

## Table of contents

1. [What Python is](#1-what-python-is)
2. [How Python code is organized and executed](#2-how-python-code-is-organized-and-executed)
3. [Lexical structure and syntax basics](#3-lexical-structure-and-syntax-basics)
4. [Objects, names, identity, mutability, and memory model](#4-objects-names-identity-mutability-and-memory-model)
5. [Built-in data types](#5-built-in-data-types)
6. [Operators and expressions](#6-operators-and-expressions)
7. [Control flow](#7-control-flow)
8. [Functions](#8-functions)
9. [Scope, namespaces, closures, `global`, and `nonlocal`](#9-scope-namespaces-closures-global-and-nonlocal)
10. [Modules, packages, imports, and `__name__`](#10-modules-packages-imports-and-__name__)
11. [Object-oriented programming](#11-object-oriented-programming)
12. [Python data model and special methods](#12-python-data-model-and-special-methods)
13. [Iterables, iterators, generators, and comprehensions](#13-iterables-iterators-generators-and-comprehensions)
14. [Exceptions and error handling](#14-exceptions-and-error-handling)
15. [Files, I/O, serialization, and context managers](#15-files-io-serialization-and-context-managers)
16. [Decorators](#16-decorators)
17. [Typing and annotations](#17-typing-and-annotations)
18. [Asynchronous programming](#18-asynchronous-programming)
19. [Useful standard-library concepts every Python programmer should know](#19-useful-standard-library-concepts-every-python-programmer-should-know)
20. [Testing, debugging, and introspection](#20-testing-debugging-and-introspection)
21. [Pythonic idioms and best practices](#21-pythonic-idioms-and-best-practices)
22. [Common pitfalls](#22-common-pitfalls)
23. [Modern Python 3.14 notes](#23-modern-python-314-notes)
24. [Revision checklist](#24-revision-checklist)
25. [References](#25-references)

---

## 1. What Python is

Python is a **high-level, interpreted, general-purpose programming language** with readable syntax, dynamic typing, automatic memory management, and a large standard library.

### Key characteristics

- Readability-first syntax
- Indentation-based block structure
- Multi-paradigm: procedural, object-oriented, functional
- Dynamic and strongly typed
- “Batteries included” standard library
- Strong ecosystem for scripting, automation, web, data work, testing, tooling, and education

### First program

```python
print("Hello, Python!")
```

---

## 2. How Python code is organized and executed

Python programs are built from **code blocks** such as:
- a module (usually a `.py` file),
- a function body,
- a class body,
- interactive commands.

A **module** is Python's normal file-level unit of organization and its usual import unit. In everyday Python, a module is usually one `.py` file that can contain variables, functions, classes, and top-level statements. The same file can be run directly as a script or imported from another file as a module.

### Example: importing a module

```python
# file: utils.py
def greet(name):
    return f"Hello, {name}"
```

```python
# file: main.py
import utils

print(utils.greet("Alice"))
```

### REPL vs script

- **REPL**: interactive shell for quick experiments
- **Script**: saved `.py` file for reusable code

### Bytecode and interpreter

In normal **CPython** execution, Python source code is not run directly line by line as plain text. It is first **parsed** and **compiled** into **bytecode**, and that bytecode is then executed by the **CPython virtual machine**. This description is mainly about CPython, which is the reference implementation most people use; other implementations such as PyPy may execute Python differently internally. Bytecode is a lower-level instruction format for the Python interpreter, not native machine code for your CPU. You can think of it as an intermediate form between your `.py` source and the actual runtime work done by the interpreter.

Very roughly, CPython does this:

1. Read the source code.
2. Parse it according to Python's grammar into an internal structure (an abstract syntax tree, or AST).
3. If the code is valid, compile it into a **code object**.
4. Store bytecode instructions and related metadata inside that code object.
5. Execute the bytecode in the CPython evaluation loop.

If the source is syntactically invalid, Python raises a `SyntaxError` before normal execution begins.

A **code object** represents byte-compiled executable Python code. Besides bytecode, it also carries execution-related information such as constants, variable names, and other metadata the interpreter needs. When you define a function, its body is compiled into a code object; when you call that function later, CPython creates a new **frame** to execute that code.

CPython's virtual machine is **stack-based**. As it runs, it processes bytecode instructions one at a time, keeps track of the current execution **frame**, and uses an **evaluation stack** to hold intermediate values. A frame records where execution currently is and contains the namespaces relevant to that execution, such as local names, global names, and built-ins.

The bytecode instructions themselves do not directly "do the work" in the way machine code does on hardware. Instead, they tell the interpreter what runtime operation to perform on Python objects. For example, an instruction may:

- load a local variable,
- load a constant,
- call a function,
- perform an operation such as addition,
- return a value.

Those operations still involve normal Python runtime behavior such as method lookup, function calls, and object handling. So bytecode is best thought of as the interpreter's instruction stream for manipulating Python objects.

You can inspect bytecode with the `dis` module:

```python
import dis

def add_one(x):
    return x + 1

dis.dis(add_one)
```

The exact opcode names can vary across Python versions, but conceptually the output shows: load `x`, load the constant `1`, perform the addition, and return the result. The goal is to understand the execution model, not memorize opcode names.

You usually do not manage bytecode directly, but you may see `__pycache__/` directories. When CPython imports a module, it will often cache compiled bytecode in a `.pyc` file inside `__pycache__/`, with a name such as `module.cpython-XY.pyc`. On later imports, Python can reuse that cached bytecode if it is still valid, which speeds up module loading. This caching mainly matters for imports. These files are cache artifacts, not source files, and Python can still run even if they are missing or cannot be written.

---

## 3. Lexical structure and syntax basics

## 3.1 Indentation matters

Python uses indentation to define blocks.

```python
if True:
    print("inside block")
print("outside block")
```

Bad indentation raises an error.

```python
if True:
print("wrong")  # IndentationError
```

## 3.2 Comments

```python
# This is a single-line comment
x = 10  # inline comment
```

Python has no special multiline comment syntax; repeated `#` is standard.

## 3.3 Docstrings

A docstring documents modules, functions, classes, and methods.

```python
def add(a, b):
    """Return the sum of a and b."""
    return a + b
```

## 3.4 Statements and expressions

- **Expression**: produces a value
- **Statement**: performs an action

```python
2 + 3          # expression
x = 2 + 3      # assignment statement
```

## 3.5 Keywords

Examples:

```python
if, else, elif, for, while, break, continue, pass,
def, return, class, try, except, finally, raise,
with, as, import, from, lambda, yield, global,
nonlocal, async, await, match, case
```

Do not use keywords as variable names.

## 3.6 Naming conventions

Common style conventions:
- `snake_case` for variables and functions
- `PascalCase` for classes
- `UPPER_CASE` for constants
- leading underscore `_name` for internal-use names
- double underscore `__name` inside a class is name-mangled to `_ClassName__name`
- dunder names like `__init__` are special protocol hooks

## 3.7 Literals

### Numeric literals

```python
a = 10
b = 3.14
c = 2 + 3j
d = 0b1010
e = 0xFF
```

### String literals

```python
single = 'hello'
double = "hello"
multi = """line 1
line 2"""
raw = r"C:\new\text"
formatted = f"2 + 3 = {2 + 3}"
```

### Bytes literals

```python
data = b"ABC"
```

### Boolean and null-like values

```python
flag = True
nothing = None
empty_text = ""
```

Python does not have a separate `null` keyword. `None` is Python's null-like singleton and is used for "no value", "missing value", or "not set". Values like `0`, `""`, `[]`, `{}`, and `False` are falsy in conditions, but they are not the same as `None`. When you specifically want to check for the null-like value, use `is None`.

---

## 4. Objects, names, identity, mutability, and memory model

Python variables are **names bound to objects**.

```python
x = 10
y = x
```

Here, `x` and `y` are both bound to the same integer object `10`.

That does **not** mean changing `x` will change `y`. Integers are immutable, so an assignment such as `x = 20` does not mutate `10`; it simply rebinds `x` to a different object.

```python
x = 10
y = x

x = 20
print(x)  # 20
print(y)  # 10
```

With a mutable object, two names can observe the same change because the object itself is modified:

```python
a = [1, 2]
b = a

a.append(3)
print(a)  # [1, 2, 3]
print(b)  # [1, 2, 3]
```

So the key distinction is:
- **rebinding a name** points that name at a different object
- **mutating an object** changes the object itself

## 4.1 Identity, type, and value

Every object has:
- **identity**
- **type**
- **value**

```python
x = [1, 2, 3]
print(id(x))      # object identity
print(type(x))    # <class 'list'>
```

## 4.2 `==` vs `is`

- `==` compares values
- `is` compares identity

```python
a = [1, 2]
b = [1, 2]
print(a == b)  # True
print(a is b)  # False
```

Use `is` mainly for singleton checks:

```python
x = None
if x is None:
    print("No value")
```

## 4.3 Mutability vs immutability

Mutable objects can be changed after they are created. Immutable objects cannot be changed in place; when they seem to "change", Python creates a new object and the name is rebound. Mutability is a property of the object, not the variable name. In Python, variables are better thought of as names, and names themselves are not “mutable” or “immutable.”Mutability applies to objects, not variable names. A variable can be rebound to a different object at any time.

### Common immutable types
- `int`
- `float`
- `bool`
- `complex`
- `str`
- `tuple`
- `bytes`
- `frozenset`

### Common mutable types
- `list`
- `dict`
- `set`
- `bytearray`
- most class instances

"Immutable" does not always mean every object inside is also immutable.

```python
s = "hello"
# s[0] = "H"  # TypeError: strings do not support item assignment
s = s.upper()  # creates a new string and rebinds s
print(s)  # HELLO

nums = [1, 2, 3]
nums[0] = 99
print(nums)  # [99, 2, 3]

record = ([1, 2], "A")
record[0].append(3)
print(record)  # ([1, 2, 3], 'A')
# record[0] = [9, 9]  # TypeError
```

A tuple is immutable as a container, but the objects stored inside it can still be mutable.
If an immutable container holds mutable or unhashable elements, that matters for hashing and shared-state behavior, which are covered later.
If two names refer to the same mutable object, changes through one name are visible through the other.

## 4.4 Assignment binds names; it does not copy objects

```python
a = [1, 2]
b = a
b.append(3)
print(a)  # [1, 2, 3]
```

After `b = a`, both names refer to the same list object. No copy is made unless you explicitly create one.

## 4.5 Shallow vs deep copy

```python
import copy

a = [[1, 2], [3, 4]]
b = copy.copy(a)      # new outer list, same inner lists
c = copy.deepcopy(a)  # new outer list, new inner lists

a[0].append(99)

print(a)  # [[1, 2, 99], [3, 4]]
print(b)  # [[1, 2, 99], [3, 4]]
print(c)  # [[1, 2], [3, 4]]
```

`copy.copy(a)` makes a shallow copy: it creates a new outer object, but it does not recursively copy the objects inside it.
In this example, `a` and `b` are different outer lists, but they still refer to the same inner lists, so changing `a[0]` also changes what `b[0]` shows. But if a new element is appended to a then this is not reflected in b.

`copy.deepcopy(a)` makes a deep copy: it recursively copies nested objects too.
That is why `c` stays unchanged after `a[0].append(99)`.

For a flat list such as `[1, 2, 3]`, a shallow copy is usually enough.
The difference matters when the object contains other mutable objects such as nested lists, dictionaries, or sets.

---

## 5. Built-in data types

## 5.1 Numeric types

```python
a = 10        # int
b = 3.5       # float
c = 2 + 3j    # complex # python has complex numbers too!
```

### Basic arithmetic

```python
print(10 + 3)   # 13
print(10 - 3)   # 7
print(10 * 3)   # 30
print(10 / 3)   # 3.333...
print(10 // 3)  # 3
print(10 % 3)   # 1
print(2 ** 5)   # 32
```

## 5.2 Booleans

```python
print(True and False)  # False
print(True or False)   # True
print(not True)        # False
```

Booleans are a subtype of integers in Python:

```python
print(True == 1)   # True
print(False == 0)  # True
```

## 5.2.1 `None`

`None` is Python's singleton object used to represent “no value” or “no result”.

```python
value = None

if value is None:
    print("Nothing here")
```

Compare to `None` with `is`, not `==`.

## 5.3 Strings

Strings are immutable sequences of Unicode characters.

```python
text = "Python"
print(text[0])      # P
print(text[-1])     # n
print(text[1:4])    # yth
```

### Common string methods

```python
name = "  alice bob  "
print(name.strip())               # "alice bob"
print(name.upper())               # "  ALICE BOB  "
print(name.replace("alice", "A")) # "  A bob  "
print("a,b,c".split(","))         # ['a', 'b', 'c']
print("-".join(["a", "b", "c"]))  # "a-b-c"
```

### String formatting

```python
name = "Alice"
age = 20

print(f"{name} is {age} years old")
print("{} is {} years old".format(name, age))
print("%s is %d years old" % (name, age))
```

## 5.4 Lists

Lists are ordered, mutable sequences.

```python
nums = [10, 20, 30]
nums.append(40)
nums.insert(1, 15)
nums.remove(20)
print(nums)
```

### Slicing

```python
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])   # [1, 2, 3]
print(nums[:3])    # [0, 1, 2]
print(nums[::2])   # [0, 2, 4]
print(nums[::-1])  # reversed copy
```

### Sorting lists

```python
nums = [5, 2, 9, 1]
nums.sort()
print(nums)  # [1, 2, 5, 9]

words = ["pear", "a", "banana"]
words.sort(key=len)
print(words)  # ['a', 'pear', 'banana']
```

`sorted(iterable)` returns a new sorted list, while `list.sort()` sorts a list in place.

## 5.5 Tuples

Tuples are ordered, immutable sequences.

```python
point = (3, 4)
x, y = point
print(x, y)
```

Single-element tuple needs a trailing comma:

```python
single = (5,)
```

## 5.5.1 Packing and unpacking

```python
point = 10, 20          # packing
x, y = point            # unpacking
```

Extended unpacking:

```python
first, *middle, last = [1, 2, 3, 4, 5]
print(first)   # 1
print(middle)  # [2, 3, 4]
print(last)    # 5
```

## 5.6 Sets and frozensets

A `set` is a mutable collection of unique hashable elements. A `frozenset` is the immutable version of a set.

```python
items = {1, 2, 2, 3}
frozen_items = frozenset([1, 2, 2, 3])

print(items)         # {1, 2, 3}
print(frozen_items)  # frozenset({1, 2, 3})
```

Both remove duplicates and support operations like union and intersection.
- `set` can be changed in place.
- `frozenset` cannot be changed after creation.

### Set operations

```python
a = {1, 2, 3}
b = {3, 4, 5}

print(a | b)  # union
print(a & b)  # intersection
print(a - b)  # difference
print(a ^ b)  # symmetric difference
```

Symmetric difference means the values that are in either set, but not in both. Here, the result is `{1, 2, 4, 5}`. a ^ b = (a | b) - (a & b)

### Frozensets

```python
f = frozenset([1, 2, 3])
# f.add(4)  # AttributeError: 'frozenset' object has no attribute 'add'

x = frozenset({1, 2, 3})
y = frozenset({3, 4})
print(x | y)  # frozenset({1, 2, 3, 4})
print(x & y)  # frozenset({3})
```

Set operations on `frozenset` return new `frozenset` objects; they do not modify the original.

### Practical uses of `frozenset`

Because `frozenset` is immutable, it can be used where a regular `set` cannot.

```python
labels = {frozenset({"red", "blue"}): "color pair"}
print(labels[frozenset({"blue", "red"})])  # color pair

groups = {frozenset({1, 2}), frozenset({3, 4})}
print(frozenset({1, 2}) in groups)  # True
```

This works because `frozenset` is hashable, unlike `set`. See `5.7.1 Hashability` for the general rule.

## 5.7 Dictionaries

Dictionaries map keys to values.

```python
student = {"name": "Ana", "age": 21}
print(student["name"])
student["age"] = 22
student["city"] = "Delhi"
```

### Common dict operations

```python
print(student.keys())
print(student.values())
print(student.items())
print(student.get("grade", "N/A"))
```

### Dictionary iteration

```python
for key, value in student.items():
    print(key, value)
```

## 5.7.1 Hashability

A value must be **hashable** to be used as:
- a dictionary key,
- a set element.

Many immutable values are hashable, but immutable containers are hashable only if all of their elements are hashable.

```python
d = {"name": "Alice"}      # str key is hashable
coords = {(1, 2), (3, 4)}  # tuple of hashable values is hashable

# bad = {[1, 2]: "x"}      # TypeError: list is unhashable
```

A tuple is hashable only if all of its elements are hashable.

## 5.8 Bytes, bytearray, memoryview

`str` is for text (Unicode characters). `bytes`, `bytearray`, and `memoryview` are for **raw binary data** such as file contents, network payloads, images, compressed data, or serialized data.

- `bytes`: immutable sequence of integers from `0` to `255`
- `bytearray`: mutable version of `bytes`
- `memoryview`: a zero-copy view over existing binary storage

### `bytes`

Use `bytes` when you want read-only binary data.

```python
text = "ABC"
b = text.encode("utf-8")

print(b)                 # b'ABC'
print(b[0])              # 65
print(list(b))           # [65, 66, 67]
print(b.decode("utf-8")) # ABC
```

Unlike a string, each element of `bytes` is an integer byte value, not a one-character string.

### `bytearray`

Use `bytearray` when the binary data must be changed in place.

```python
ba = bytearray(b"ABC")
ba[0] = 97
ba.append(68)

print(ba)        # bytearray(b'aBCD')
print(bytes(ba)) # b'aBCD'
```

This is the key difference:
- `bytes` cannot be modified after creation
- `bytearray` can be modified after creation

### `memoryview`

A `memoryview` lets you access existing binary data **without copying it**. This is useful when the data is large or when performance matters.

```python
data = bytearray(b"ABCDE")
view = memoryview(data)

print(bytes(view[1:4]))  # b'BCD'

view[0] = 122
print(data)              # bytearray(b'zBCDE')
```

The change through `view` also changes `data` because the `memoryview` points to the same underlying bytes.

### Real-world uses

- `bytes`: reading binary files, receiving data from sockets, working with images, PDFs, ZIP files, or encoded data
- `bytearray`: building packets, modifying chunks before writing them, or reusing a mutable binary buffer
- `memoryview`: parsing or slicing large binary buffers in streaming or performance-sensitive code without making extra copies

### Rule of thumb

- choose `bytes` for read-only binary data
- choose `bytearray` for mutable binary data
- choose `memoryview` for zero-copy access to existing binary data

## 5.9 `range`

`range` represents an arithmetic progression and is commonly used in loops.

```python
for i in range(5):
    print(i)
```

## 5.10 Truthiness and falsiness

Falsy values include:
- `False`
- `None`
- zero numeric values
- empty strings
- empty lists, tuples, dicts, sets
- empty ranges

```python
if not []:
    print("empty list is falsy")
```

---

## 6. Operators and expressions

## 6.1 Arithmetic operators

```python
+, -, *, /, //, %, **
```

## 6.2 Comparison operators

```python
==, !=, <, <=, >, >=
```

Python supports chained comparisons:

```python
x = 10
print(1 < x < 20)  # True
```

## 6.3 Logical operators

```python
and, or, not
```

## 6.4 Membership operators

```python
in, not in
```

```python
print("a" in "cat")  # True
print(2 in [1, 2, 3])  # True
```

## 6.5 Identity operators

```python
is, is not
```

## 6.6 Bitwise operators

```python
&, |, ^, ~, <<, >>
```

```python
print(5 & 3)  # 1
print(5 | 3)  # 7
```

## 6.7 Assignment operators

```python
=, +=, -=, *=, /=, //=, %=, **=, &=, |=, ^=, <<=, >>=
```

## 6.8 Walrus operator (`:=`)

Assigns and returns a value in an expression.

```python
if (n := len("python")) > 3:
    print(n)
```

Use it when it improves clarity, not just because it exists.

## 6.9 Conditional expression

```python
age = 17
status = "adult" if age >= 18 else "minor"
```

## 6.10 Unpacking operators `*` and `**`

`*` unpacks an iterable into separate positional items. `**` unpacks a mapping into separate key-value pairs. This section is about unpacking in calls and literals, not parameter collection.

### In function calls

```python
nums = [1, 2, 3]

def add(a, b, c):
    return a + b + c

print(add(*nums))  # 6
print(*nums)       # 1 2 3
```

### In collection and dict literals

```python
a = [1, 2]
b = [*a, 3, 4]
print(b)  # [1, 2, 3, 4]

t = (*a, 3, 4)
print(t)  # (1, 2, 3, 4)

x = {"a": 1, "b": 2}
y = {**x, "b": 99, "c": 3}
print(y)  # {'a': 1, 'b': 99, 'c': 3}
```

When duplicate keys appear during dictionary unpacking, the later value wins.

`*` and `**` are also used in assignment unpacking and function definitions. See `5.5.1` for assignment unpacking and `8.5` for `*args` and `**kwargs`.

## 6.11 Lambda expressions

Small anonymous functions.

```python
square = lambda x: x * x
print(square(5))
```

Usually prefer `def` when logic becomes non-trivial.

## 6.12 Operator precedence

Example:

```python
result = 2 + 3 * 4   # 14, not 20
```

Use parentheses when in doubt.

---

## 7. Control flow

## 7.1 `if`, `elif`, `else`

```python
score = 82

if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
else:
    grade = "C"

print(grade)
```

## 7.2 `for` loops

```python
for ch in "abc":
    print(ch)
```

Loop over indices when needed:

```python
items = ["a", "b", "c"]
for i, item in enumerate(items):
    print(i, item)
```

## 7.3 `while` loops

```python
count = 3
while count > 0:
    print(count)
    count -= 1
```

## 7.4 `break`, `continue`, `pass`, and `del`

```python
for n in range(5):
    if n == 2:
        continue
    if n == 4:
        break
    print(n)
```

`pass` is a no-op placeholder.

```python
def todo():
    pass
```

`del` removes a name binding or deletes an item, slice, or attribute depending on context.

```python
nums = [10, 20, 30]
del nums[1]
print(nums)  # [10, 30]
```

## 7.5 Loop `else`

The `else` block runs if the loop finishes **without `break`**.

```python
for n in [1, 3, 5]:
    if n % 2 == 0:
        print("even found")
        break
else:
    print("no even number found")
```

## 7.6 `match` / `case` (structural pattern matching)

The value after `match` can be almost any Python object: an `int`, `str`, `list`, `tuple`, `dict`, `None`, or even a class instance.

What matters is that each `case` must use a **valid pattern**. A `case` is **not** a general Python expression.

### What patterns can you use?

- **Literal patterns**: `case 200`, `case "ok"`, `case None`, `case True`
- **Sequence patterns**: `case [x, y]`, `case (x, y, z)`
- **Mapping patterns**: `case {"name": name}`
- **Class patterns**: `case Point(x=0, y=0)`, `case Point(x, y)`
- **OR patterns**: `case 401 | 403`
- **Capture patterns**: `case x` matches anything and stores it in `x`
- **Wildcard**: `case _` matches anything and does not store it
- **Guards**: `case x if x < 0`

### What does not work?

- `case x > 0` is invalid because patterns are not arbitrary boolean expressions.
- `case some_variable` does **not** mean "match the value of `some_variable`". A bare name is treated as a **capture pattern**. (same as OCaml)
- To match a named constant, use a literal or a qualified name such as `HTTPStatus.OK` or `Color.RED`.

```python
def http_status(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"
```

This example uses **literal patterns**, so it works well for numbers, strings, booleans, and `None`.

### Matching sequences

Sequence patterns are for sequence-shaped data such as `list` and `tuple`.

They do **not** match `str`, `bytes`, or `bytearray`.

```python
def describe(value):
    match value:
        case [x, y]:
            return f"Two-item list: {x}, {y}"
        case [x, y, z]:
            return f"Three-item list: {x}, {y}, {z}"
        case _:
            return "Something else"
```

### Matching dictionaries

Mapping patterns are for `dict` objects and other mapping types.

```python
def get_name(record):
    match record:
        case {"name": name}:
            return name
        case _:
            return None
```

### Matching class instances

Class patterns are useful when you want to match objects by type and unpack their attributes.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def locate(value):
    match value:
        case Point(0, 0):
            return "origin"
        case Point(x, y):
            return f"Point at {x}, {y}"
        case _:
            return "Not a Point"
```

### Guards

```python
def classify(n):
    match n:
        case x if x < 0:
            return "negative"
        case 0:
            return "zero"
        case _:
            return "positive"
```

Pattern matching is best for **shape-based branching**:

- value equals a literal,
- value has a certain sequence or mapping structure,
- value is an instance of a class with a certain shape.

Use ordinary `if` / `elif` when you just need general boolean conditions.

---

## 8. Functions

## 8.1 Defining functions

```python
def greet(name):
    return f"Hello, {name}"
```

## 8.2 Parameters and arguments

```python
def power(base, exponent):
    return base ** exponent

print(power(2, 3))
```

## 8.3 Positional and keyword arguments

```python
def introduce(name, age):
    print(name, age)

introduce("Asha", 21)
introduce(age=21, name="Asha")
```

## 8.4 Default values for arguments

```python
def greet(name, prefix="Hello"):
    return f"{prefix}, {name}"
```

### Important pitfall: mutable defaults

Mutable default arguments are bad because the default value is created only once, when the function is defined, not each time the function is called. If that default value is mutable, such as a list, dictionary, or set, changes made in one call will still be there in later calls.

That means state can "leak" between calls in a way that is surprising:

In the bad version below, both calls reuse the same list object. In the good version, `None` is just a safe placeholder, and a new list is created inside the function whenever no list was provided.

Bad:

```python
def append_item(item, items=[]):
    items.append(item)
    return items
```

```python
print(append_item("a"))  # ['a']
print(append_item("b"))  # ['a', 'b']  <- unexpected if you wanted a fresh list
```

Good:

```python
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

## 8.5 Variable-length arguments

```python
def demo(*args, **kwargs):
    print(args)
    print(kwargs)

demo(1, 2, x=10, y=20)
```

- `*args` collects extra positional arguments
- `**kwargs` collects extra keyword arguments

## 8.6 Keyword-only and positional-only parameters

```python
def f(a, b, /, c, *, d):
    print(a, b, c, d)

f(1, 2, 3, d=4)
```

- parameters before `/` are positional-only
- parameters between `/` and `*` can be passed positionally or by keyword
- parameters after `*` are keyword-only

## 8.7 Returning values

A function returns a value with `return`. If omitted, it returns `None`.

```python
def do_nothing():
    pass

print(do_nothing())  # None
```

## 8.8 Multiple return values

Python actually returns a tuple.

```python
def min_max(values):
    return min(values), max(values)

low, high = min_max([3, 1, 9, 4])
```

## 8.9 First-class functions

Functions can be assigned, passed, and returned.

```python
def shout(text):
    return text.upper()

fn = shout
print(fn("hello"))
```

## 8.10 Higher-order functions

```python
def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda x: x + 1, 3))  # 5
```

## 8.11 Recursion

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

Python supports recursion, but deep recursion can hit recursion limits.
Python does not optimize tail-recursive Python functions, so tail recursion still uses additional stack frames.

## 8.12 Docstrings and annotations

```python
def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b
```

Annotations do not automatically enforce types at runtime.

---

## 9. Scope, namespaces, closures, `global`, and `nonlocal`

## 9.1 LEGB rule

Python resolves names in this order:

- **L**ocal
- **E**nclosing
- **G**lobal
- **B**uilt-in

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)

    inner()

outer()
```

## 9.2 `global`

`global` tells Python that when you assign to a name inside the function, you mean the name in the module's global namespace, not a new local variable.

```python
count = 0

def increment():
    global count
    count += 1
```

Without `global`, Python would treat `count` as a local variable because it is assigned inside the function, and `count += 1` would fail.

Use `global` sparingly because it makes functions depend on shared mutable state:

- the function is harder to test and reuse
- changes can come from many places, which makes bugs harder to trace
- code becomes less predictable because calling one function may affect unrelated code later

In general, prefer passing values in and returning values out when possible.

## 9.3 `nonlocal`

`nonlocal` is similar, but it does not refer to the module-level global scope. It refers to a variable in the nearest enclosing function scope.

```python
def outer():
    count = 0

    def inner():
        nonlocal count
        count += 1
        return count

    return inner

counter = outer()
print(counter())  # 1
print(counter())  # 2
```

Here, `count` is not global. It belongs to `outer`, and `inner` updates that enclosed variable using `nonlocal`.

The difference is:

- `global` rebinding targets a name at module scope
- `nonlocal` rebinding targets a name in an enclosing function
- `global` is often used for module-wide shared state
- `nonlocal` is often used for closures that need to remember and update state between calls

Also note:

- use `global` only for names defined at module level
- use `nonlocal` only for names defined in an enclosing function
- both are needed only when you want to rebind a name; simply reading an outer name does not require them

## 9.4 Closures

A closure remembers values from its enclosing scope.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

times3 = make_multiplier(3)
print(times3(10))  # 30
```

## 9.5 Namespace basics

A namespace is a mapping from names to objects.

Examples:
- module namespace
- function local namespace
- class namespace
- built-in namespace

---

## 10. Modules, packages, imports, and `__name__`

## 10.1 What is a module?

A module is an importable unit of Python code. In everyday Python, a module is usually one `.py` file, but not every module comes from a `.py` file.

A module has its own namespace. Names defined inside it, such as variables, functions, and classes, belong to that module and are usually accessed as `module_name.name`.

`math_utils.py`

```python
PI = 3.14159

def square(x):
    return x * x
```

Use it:

```python
import math_utils
print(math_utils.PI)
print(math_utils.square(5))
```

## 10.1.1 What top-level executable statements are

Top-level executable statements are statements written directly in the module body, not inside another block such as a function, method, or class body. Python executes them in order when the module is first loaded in an interpreter session, whether that happens because the file is run directly or because it is imported.

```python
# file: demo.py
x = 10                   # assignment at top level
import math              # import at top level
print("loading demo")    # runs immediately

if x > 5:                # if statement at top level
    print("x is large")

def greet(name):         # creates and binds a function object
    print(f"Hello, {name}")  # runs later, when greet(...) is called

class User:              # executes the class body now to create the class
    role = "member"
```

In this example, the assignment, import, `print`, and `if` statement all execute immediately when the module loads. The `def` statement also executes immediately, but it creates the function object; the function body itself does not run until the function is called. The `class` statement executes immediately too, and Python runs the class body in order to create the class object.

```python
# file: worker.py
print("loading worker")

def run():
    print("working")

if __name__ == "__main__":
    run()
```

If `worker.py` is imported, `print("loading worker")` runs during import, but `run()` does not run because `__name__ == "__main__"` is false. If `worker.py` is run directly, both the top-level `print` and the guarded `run()` call execute.

## 10.1.2 Important module edge cases

Not every module is a `.py` file. From your program's point of view, these are still modules because they can be imported and have module namespaces.

- **Source modules**: ordinary `.py` files, which are the most common kind you write yourself
- **Built-in modules**: provided directly by the interpreter, such as `sys`
- **Extension modules**: implemented in compiled native code and imported like normal modules; in CPython these often come from platform-specific extension files such as `.so` or `.pyd`
- **Frozen modules**: embedded into the interpreter/runtime instead of being loaded from an ordinary source file
- **Package modules**: package directories whose `__init__.py` file makes the package itself a module
- **Namespace packages**: package-like modules that may span multiple directories and may not contain `__init__.py`

There are rarer cases too, such as bytecode-only or zip-imported modules. In normal Python code, you still use them through `import`.

## 10.2 Import forms

```python
import math
import math as m
from math import sqrt
from math import sqrt as s
```

Avoid `from module import *` in most real programs.

## 10.3 What is a package?

A package is a special kind of module that groups submodules, and often subpackages too.

Example:

```text
mypkg/
    __init__.py
    tools.py
    helpers.py
```

Import:

```python
from mypkg import tools
```

When a package has an `__init__.py` file, importing the package executes the top-level code in that file.

## 10.4 `__name__ == "__main__"`

```python
def main():
    print("Run as script")

if __name__ == "__main__":
    main()
```

`__name__` is a special variable that Python automatically creates for every module.

Its value depends on how the file is used:
- If the file is imported, `__name__` is the module's import name.
- If the file is run directly, `__name__` is the string `"__main__"`.

`"__main__"` is the special name Python gives to the entry-point module, meaning the file Python started executing first.

So:
- `if __name__ == "__main__":` means "is this file being run directly?"
- If yes, `main()` runs.
- If no, the file is being imported, so `main()` does not run automatically.

Example:

```python
# file: demo.py
print(__name__)
```

- Running `python demo.py` prints `__main__`.
- Importing `demo` from another file makes `demo.__name__` equal to `"demo"`.

More examples:

- If `demo.py` is imported with `import demo`, then `__name__ == "demo"`.
- If `mypkg/tools.py` is imported with `import mypkg.tools`, then `__name__ == "mypkg.tools"`.
- If `mypkg/__init__.py` is loaded by `import mypkg`, then `__name__ == "mypkg"`.

So `__name__` is not always just the file name or just the package name. It is the full name Python used to import that module.

## 10.5 Module search path

Python looks for modules in locations such as:
- current directory,
- standard library,
- installed packages,
- paths in `sys.path`.

Some modules, such as built-in or frozen modules, are not found through ordinary filesystem lookup.

## 10.6 Import side effects

Because top-level statements run when a module is first loaded, importing a module can have side effects.

Common side effects include printing, opening files, reading configuration, or starting expensive work during import.

Keep imports lightweight. Put script-only behavior or heavy work inside functions, or guard it with `if __name__ == "__main__":`.

---

## 11. Object-oriented programming

## 11.1 Defining classes

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof"
```

`__init__()` is a special method that Python calls automatically right after a new object is created.

It is often called a constructor, and that usage is common and usually understood. More precisely, it is an initializer, because the object has already been created by the time `__init__()` runs. The object is created first, then __init__() initializes it.

Its job is to initialize the new object by giving it its starting data.

In `Dog("Bruno")`, Python creates a new `Dog` instance, then calls `__init__(self, "Bruno")`.

Inside the method, `self` is the new object, and `self.name = name` stores `"Bruno"` inside that object as an instance attribute named `name`.

## 11.2 Creating objects

```python
d = Dog("Bruno")
print(d.name)
print(d.bark())
```

## 11.3 `self`

`self` refers to the current instance.

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
```

`self` is a naming convention, not a keyword.

## 11.4 Instance attributes vs class attributes

```python
class Student:
    school = "ABC School"  # class attribute

    def __init__(self, name):
        self.name = name    # instance attribute
```

## 11.5 Inheritance

```python
class Animal:
    def speak(self):
        return "sound"

class Cat(Animal):
    def speak(self):
        return "meow"
```

## 11.6 `super()`

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed
```

## 11.7 Polymorphism

Polymorphism means "many forms": the same operation can be used with
different objects, and each object can respond in its own way.

In Python, polymorphism commonly appears in two ways:

- Through inheritance and method overriding
- Through duck typing, where code cares about behavior rather than the
  object's exact class

```python
class Dog:
    def speak(self):
        return "woof"

class Cat:
    def speak(self):
        return "meow"

def make_it_speak(animal):
    print(animal.speak())

make_it_speak(Dog())  # woof
make_it_speak(Cat())  # meow
```

`make_it_speak()` is polymorphic because the same function works with
different objects. This example uses duck typing because any object with a
`speak()` method will work.

## 11.8 Encapsulation conventions

Python does not enforce private members like some languages.

Conventions:
- `_name` → internal use (can be accessed from outside but by convention you're not supposed to use it.)
- `__name` → inside a class body, Python rewrites it to `_ClassName__name`

Name mangling is a renaming step, not true privacy.

If you write an attribute or method name that:
- starts with two underscores
- does not end with two underscores
- is defined inside a class body

then Python rewrites the name to include the class name. For example,
`__value` inside class `Demo` becomes `_Demo__value`.

This mainly helps avoid accidental name collisions in subclasses. It does
not make the attribute impossible to access.

```python
class Demo:
    def __init__(self):
        self._internal = 1
        self.__mangled = 2
```

```python
d = Demo()

print(d._internal)       # 1
# print(d.__mangled)     # AttributeError
print(d._Demo__mangled)  # 2
```

So `self.__mangled = 2` is really stored under the name `_Demo__mangled`.

This also explains why mangling helps with subclasses:

```python
class Parent:
    def __init__(self):
        self.__value = "parent"

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__value = "child"

c = Child()
print(c._Parent__value)  # parent
print(c._Child__value)   # child
```

The two `__value` attributes do not clash because Python stores them under
different names.

Methods are mangled too:

```python
class Demo:
    def __helper(self):
        return "secret helper"

    def call_helper(self):
        return self.__helper()

d = Demo()
print(d.call_helper())      # secret helper
# print(d.__helper())       # AttributeError
print(d._Demo__helper())    # secret helper
```

Important:
- `__name` can be mangled in classes.
- `__name__` is different. Names with double underscores on both sides are
  special Python names and are not name-mangled.

## 11.9 Class methods and static methods

A normal method works with one specific object, so its first parameter is
usually `self`.

A class method works with the class itself, so its first parameter is `cls`.
Use a class method when the method needs to read or change class-level data
shared by all objects.

A static method is just a regular function placed inside the class because it is closely related to that class. It does not receive `self` or `cls` automatically.

In short:
- Normal method: works with one object (`self`)
- Class method: works with the class (`cls`)
- Static method: works like a helper function inside the class and outside the class. A static method does not require a object of the class to be called. It can be called directly like ClassName.static_method() from outside the class.

Example:

```python
class Example:
    count = 0

    def __init__(self, name):
        self.name = name
        Example.count += 1

    def describe(self):
        return f"This object is {self.name}"

    @classmethod
    def how_many(cls):
        return cls.count

    @staticmethod
    def add(a, b):
        return a + b
```

How this works:
- `describe(self)` is a normal method. It uses instance data such as
  `self.name`.
- `how_many(cls)` is a class method. It uses `cls.count`, which belongs to the
  class and is shared by all objects.
- `add(a, b)` is a static method. It does not need instance data or class data.

Usage:

```python
e1 = Example("first")
e2 = Example("second")

print(e1.describe())        # This object is first
print(Example.how_many())   # 2
print(Example.add(3, 4))    # 7
```

Another important use of class methods is to create alternative constructors:

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def from_string(cls, text):
        name, age = text.split(",")
        return cls(name, int(age))

p = Person.from_string("Asha,26")
print(p.name)   # Asha
print(p.age)    # 26
```

Here `from_string()` is a class method because it creates and returns a new object of the class.

Static methods are useful for helper logic related to the class:

```python
class MathHelper:
    @staticmethod
    def is_even(number):
        return number % 2 == 0

print(MathHelper.is_even(10))  # True
print(MathHelper.is_even(7))   # False
```

`is_even()` is a static method because it does not need any object state or class state. It is simply a utility function grouped inside the class.

## 11.10 Properties

Properties let you control access to an attribute while still using normal
attribute syntax.

In other words, the user of the class writes `obj.value`, but behind the scenes Python calls a method. This is useful when you want to validate data, compute a value, or keep the internal representation private.

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Too cold")
        self._celsius = value

t = Temperature(25)
print(t.celsius)   # 25

t.celsius = 30
print(t.celsius)   # 30

# t.celsius = -300   # Raises ValueError
```

`celsius` looks like a normal attribute, but it is managed by two methods:

- The getter (`@property`) runs when you read `t.celsius`.
- The setter (`@celsius.setter`) runs when you assign to `t.celsius`.

The actual value is stored in `_celsius`. The leading underscore is a
convention that means "internal use inside the class."

This works because `celsius` and `_celsius` are not the same thing:

- `celsius` is a property on the class.
- `_celsius` is the instance variable that actually stores the number.

When Python sees `t.celsius`, it calls the getter method instead of directly reading an instance variable named `celsius`. The getter then returns `self._celsius`.

When Python sees `t.celsius = 30`, it calls the setter method. The setter
validates the value and then stores it in `self._celsius`.

So after this line:

```python
t = Temperature(25)
```

the object typically contains:

```python
{'_celsius': 25}
```

The reason we store the value in `_celsius` is to avoid infinite recursion. If the setter did `self.celsius = value`, that would call the setter again and again. Using `_celsius` gives the property a separate internal storage place.

## 11.11 Dataclasses

Useful for data-heavy classes.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(2, 3)
print(p)
```

Dataclasses automatically generate useful methods such as `__init__` and `__repr__` by default.

## 11.12 `__slots__` (advanced)

`__slots__` can restrict instance attributes and sometimes reduce memory usage for large numbers of instances.

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

Use it only when you understand its trade-offs.

## 11.13 Abstract base classes (ABCs)

An abstract base class defines a common interface that other classes must
follow.

You usually use an ABC when several classes should all provide the same methods, but the actual implementation will be different in each subclass.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

rect = Rectangle(4, 5)
print(rect.area())   # 20

# shape = Shape()    # Raises TypeError
```

Here `Shape` is not meant to be created directly. Instead, it says that every subclass of `Shape` must provide an `area()` method.

If a subclass does not implement all abstract methods, Python will not let you create an object of that subclass.

ABCs are useful when you want different classes to share the same contract. For example, `Rectangle`, `Circle`, and `Triangle` could all be different kinds of `Shape`, and each one would need its own version of `area()`.

---

## 12. Python data model and special methods

The Python data model is the set of protocols that tell Python how objects behave with built-in syntax, operators, and functions.

At a high level:
- `print(obj)` uses `str(obj)`, which usually calls `obj.__str__()`
- `repr(obj)` calls `obj.__repr__()`
- `len(obj)` calls `obj.__len__()`
- `obj[i]` calls `obj.__getitem__(i)`
- `for x in obj` uses `obj.__iter__()` and then the iterator's `__next__()`
- `with obj` uses `obj.__enter__()` and `obj.__exit__()`
- `await obj` uses `obj.__await__()`

## 12.1 What special methods are

Special methods are methods with names like `__len__`, `__iter__`, and `__add__`. They are often called **dunder methods** because they begin and end with double underscores.

You usually do not call these methods directly. Instead, you write normal Python syntax and let Python call the correct method for you.

Examples:
- `len(x)` asks whether `x` provides `__len__`
- `x + y` asks whether `x` provides `__add__`
- `for item in x` asks whether `x` provides iteration support

These methods define **protocols**. A protocol is simply a rule such as "if an object has these methods, Python knows how to use it in this way."

Important note:
- Special method lookup for built-in syntax is generally done on the class, not the instance. For example, assigning `obj.__len__ = ...` does not change what `len(obj)` does.

This section covers both the common protocols you use every day and some advanced ones that explain how Python's object system works internally.

## 12.2 Object creation and lifecycle

Object creation usually involves two steps:
- `__new__(cls, ...)` creates and returns a new instance
- `__init__(self, ...)` initializes that instance after it has been created

```python
class Point:
    def __new__(cls, x, y):
        print("__new__")
        return super().__new__(cls)

    def __init__(self, x, y):
        print("__init__")
        self.x = x
        self.y = y

p = Point(2, 3)
```

What happens here:
- `__new__` runs first
- it must return the new object
- `__init__` then receives that object and fills in its attributes
- `__init__` should return `None`, not another object

In everyday code, you normally define `__init__` and leave `__new__` alone. `__new__` is more common when working with immutable types or advanced object creation patterns.

One subtle rule:
- if `__new__` returns something that is not an instance of `cls`, Python does not call `__init__`

`__del__(self)` is a finalizer that may run when an object is about to be destroyed, but it is usually a poor tool for resource management.

Why `__del__` is tricky:
- it does not guarantee prompt cleanup
- it may run at an inconvenient time
- it is harder to reason about than explicit cleanup

For files, locks, database connections, and similar resources, prefer a context manager with `with`.

## 12.3 Representation, display, and conversion

`__repr__` and `__str__` both produce strings, but they serve different purposes.

- `__repr__` is the developer-oriented representation
- `__str__` is the user-oriented readable form

```python
class Measurement:
    def __init__(self, meters):
        self.meters = meters

    def __repr__(self):
        return f"Measurement({self.meters!r})"

    def __str__(self):
        return f"{self.meters} m"

    def __format__(self, spec):
        if spec == "cm":
            return f"{self.meters * 100} cm"
        return str(self)

    def __bytes__(self):
        return str(self).encode("utf-8")

    def __int__(self):
        return int(self.meters)

    def __float__(self):
        return float(self.meters)
```

In an f-string, `!r` means "format this value with `repr()`". So `f"{self.meters!r}"` uses the developer-facing representation of `self.meters`, which is a common pattern inside `__repr__`.

```python
m = Measurement(2.5)

print(repr(m))         # Measurement(2.5) -> __repr__
print(str(m))          # 2.5 m            -> __str__
print(f"{m:cm}")       # 250.0 cm         -> __format__
print(bytes(m))        # b'2.5 m'         -> __bytes__
print(float(m))        # 2.5              -> __float__
print(int(m))          # 2                -> __int__
```

Important rules:
- `repr(obj)` calls `__repr__`
- `str(obj)` and `print(obj)` use `__str__`
- if `__str__` is missing, Python falls back to `__repr__`
- `format(obj, spec)` and f-strings like `f"{obj:spec}"` use `__format__`
- `bytes(obj)` uses `__bytes__`

Numeric conversion hooks:

| Method | Used by | Meaning |
| --- | --- | --- |
| `__int__` | `int(obj)` | convert to an integer |
| `__float__` | `float(obj)` | convert to a floating-point value |
| `__index__` | slicing, `range()`, `bin()`, `hex()` | provide an exact integer value |

`__index__` is stronger than `__int__`. It is for cases where Python requires a true integer, not just something that can be numerically converted.

## 12.4 Truthiness, comparison, and hashing

Truthiness controls how an object behaves in `if`, `while`, `and`, `or`, and `bool(obj)`.

```python
class Score:
    def __init__(self, points):
        self.points = points

    def __bool__(self):
        return self.points > 0
```

Rules for truthiness:
- if `__bool__` exists, Python uses it
- otherwise, if `__len__` exists, Python treats length `0` as false and nonzero length as true
- otherwise, the object is considered true

Comparison methods are called **rich comparison methods**:

| Method | Operator |
| --- | --- |
| `__eq__` | `==` |
| `__ne__` | `!=` |
| `__lt__` | `<` |
| `__le__` | `<=` |
| `__gt__` | `>` |
| `__ge__` | `>=` |

Example:

```python
class Person:
    def __init__(self, age):
        self.age = age

    def __eq__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return self.age == other.age

    def __lt__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return self.age < other.age
```

Important comparison rules:
- return `NotImplemented` when the other operand is of an unsupported type
- `NotImplemented` is a special value, not the same thing as `NotImplementedError`
- if an operation is still unsupported after Python tries both sides, Python raises `TypeError`

Hashing is controlled by `__hash__`. Hashes are used by dictionaries and sets.

```python
class Key:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Key):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
```

Hashing rules:
- if `a == b`, then `hash(a)` must equal `hash(b)`
- dictionary keys and set elements must be hashable
- if you define `__eq__` but do not define `__hash__`, Python usually makes instances unhashable
- mutable objects that compare by value are often a bad fit for custom hashing, because changing their value can break dictionary/set behavior

## 12.5 Container and sequence/mapping behavior

These methods let an object behave like a container, sequence, or mapping.

```python
class MyList:
    def __init__(self, values):
        self.values = list(values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def __contains__(self, item):
        return item in self.values
```

What each method does:
- `__len__` supports `len(obj)`
- `__getitem__` supports indexing and lookup with `obj[key]`
- `__setitem__` supports assignment with `obj[key] = value`
- `__delitem__` supports deletion with `del obj[key]`
- `__contains__` supports membership tests with `item in obj`

Slicing is usually handled inside `__getitem__`:

```python
nums = MyList([10, 20, 30, 40])
print(nums[1])       # 20
print(nums[1:3])     # [20, 30]
```

When Python sees `nums[1:3]`, it passes a `slice` object to `__getitem__`, not two separate integers.

Useful notes:
- `__getitem__` can support integer indexes, slices, keys, or any other lookup object you choose
- if `__contains__` is missing, `in` can fall back to iteration

## 12.6 Iteration protocol

The iteration protocol explains how `for` loops work.

- an **iterable** is an object that can produce an iterator
- an **iterator** is an object that yields values one by one and remembers where it is

The protocol uses two methods:
- `__iter__()` returns an iterator
- `__next__()` returns the next value, or raises `StopIteration` when there are no more values

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value
```

This `Countdown` object is both:
- an iterable, because it has `__iter__`
- an iterator, because `__next__` yields successive values and `__iter__` returns `self`

Internally, a `for` loop does roughly this:
- call `iter(obj)`
- repeatedly call `next(iterator)`
- stop when `StopIteration` is raised

Advanced note:
- old-style sequence iteration can also fall back to repeated `__getitem__(0)`, `__getitem__(1)`, and so on until `IndexError`, but new code should implement `__iter__` explicitly

Chapter 13 expands on iterables, iterators, generators, and comprehensions. This section focuses only on the protocol itself.

## 12.7 Callables and context managers

### `__call__`

`__call__` lets an instance behave like a function.

```python
class Adder:
    def __init__(self, n):
        self.n = n

    def __call__(self, x):
        return x + self.n

add5 = Adder(5)
print(add5(10))  # 15
```

When Python sees `add5(10)`, it calls `add5.__call__(10)`.

This is useful for:
- configurable function-like objects
- stateful callables
- objects that wrap behavior but still want function-call syntax

### `__enter__` and `__exit__`

These methods define the context manager protocol used by `with`.

```python
class Demo:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("exit")
        return False
```

What `with` does:
- call `__enter__` at the start of the block
- bind the returned value after `as`, if present
- call `__exit__` at the end of the block, even if an exception happened

`__exit__(exc_type, exc, tb)` receives exception information:
- if no exception happened, all three arguments are `None`
- if an exception happened, they describe that exception

Exception suppression:
- if `__exit__` returns a truthy value, the exception is suppressed
- if it returns `False` or `None`, the exception keeps propagating

## 12.8 Descriptors and attribute access

A **descriptor** is an object stored on a class that controls what happens when an attribute is read, assigned, or deleted.

The descriptor protocol uses these methods:
- `__get__(self, obj, objtype=None)` for attribute reads
- `__set__(self, obj, value)` for attribute assignment
- `__delete__(self, obj)` for attribute deletion
- `__set_name__(self, owner, name)` to learn the attribute name when the class is created

Descriptors are everywhere in normal Python:
- functions are descriptors, which is why methods become bound to instances
- `property` is descriptor-based
- `classmethod` and `staticmethod` are descriptor-based tools

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError("Must be positive")
        setattr(obj, self.name, value)

class Product:
    price = Positive()

    def __init__(self, price):
        self.price = price
```

How this works:
- `price` is not a normal instance variable on the class
- it is a descriptor object stored in `Product.__dict__`
- assigning `self.price = price` triggers `Positive.__set__`
- reading `product.price` triggers `Positive.__get__`
- the real value is stored in `_price`

Attribute access hooks:

| Method | When it runs |
| --- | --- |
| `__getattribute__` | for every attribute access |
| `__getattr__` | only if normal lookup fails |
| `__setattr__` | for every attribute assignment |
| `__delattr__` | for every attribute deletion |

Important distinction:
- `__getattribute__` is the main attribute-access hook
- `__getattr__` is only a fallback for missing attributes

At a high level, normal instance lookup performed by `object.__getattribute__` follows this order:
1. data descriptor on the class
2. instance dictionary
3. non-data descriptor or other class attribute
4. `__getattr__`, if the attribute is still missing

Descriptor terminology:
- a **data descriptor** defines `__set__` or `__delete__`
- a **non-data descriptor** defines only `__get__`

That is why a property overrides an instance attribute, while a normal method can be shadowed by an instance attribute with the same name.

Critical warning:
- custom `__getattribute__` and `__setattr__` methods can easily cause infinite recursion
- inside them, use `object.__getattribute__(self, name)` and `object.__setattr__(self, name, value)` when you need the default behavior

Example:

```python
class Logged:
    def __getattribute__(self, name):
        print("getting", name)
        return object.__getattribute__(self, name)
```

## 12.9 Arithmetic and operator overloading

Python lets classes define how operators behave.

For a binary operator such as `a + b`, Python usually tries:
1. `a.__add__(b)`
2. if that returns `NotImplemented`, `b.__radd__(a)`
3. if neither side handles it, raise `TypeError`

For some mixed-type operations, Python gives the reflected method of the right operand priority when the right operand's type is a subclass of the left operand's type.

In-place operators such as `+=` first try the in-place method like `__iadd__`. If that is unavailable or returns `NotImplemented`, Python falls back to the normal binary operation.

Unary operators:

| Syntax | Method |
| --- | --- |
| `+a` | `__pos__` |
| `-a` | `__neg__` |
| `abs(a)` | `__abs__` |
| `~a` | `__invert__` |

Binary arithmetic operators:

| Syntax | Left-side method |
| --- | --- |
| `a + b` | `__add__` |
| `a - b` | `__sub__` |
| `a * b` | `__mul__` |
| `a @ b` | `__matmul__` |
| `a / b` | `__truediv__` |
| `a // b` | `__floordiv__` |
| `a % b` | `__mod__` |
| `divmod(a, b)` | `__divmod__` |
| `a ** b` or `pow(a, b)` | `__pow__` |

Bitwise and shift operators:

| Syntax | Left-side method |
| --- | --- |
| `a << b` | `__lshift__` |
| `a >> b` | `__rshift__` |
| `a & b` | `__and__` |
| `a ^ b` | `__xor__` |
| `a | b` | `__or__` |

Reflected methods:

| Syntax | Reflected method |
| --- | --- |
| `a + b` | `__radd__` |
| `a - b` | `__rsub__` |
| `a * b` | `__rmul__` |
| `a @ b` | `__rmatmul__` |
| `a / b` | `__rtruediv__` |
| `a // b` | `__rfloordiv__` |
| `a % b` | `__rmod__` |
| `divmod(a, b)` | `__rdivmod__` |
| `a ** b` | `__rpow__` |
| `a << b` | `__rlshift__` |
| `a >> b` | `__rrshift__` |
| `a & b` | `__rand__` |
| `a ^ b` | `__rxor__` |
| `a | b` | `__ror__` |

In-place methods:

| Syntax | In-place method |
| --- | --- |
| `a += b` | `__iadd__` |
| `a -= b` | `__isub__` |
| `a *= b` | `__imul__` |
| `a @= b` | `__imatmul__` |
| `a /= b` | `__itruediv__` |
| `a //= b` | `__ifloordiv__` |
| `a %= b` | `__imod__` |
| `a **= b` | `__ipow__` |
| `a <<= b` | `__ilshift__` |
| `a >>= b` | `__irshift__` |
| `a &= b` | `__iand__` |
| `a ^= b` | `__ixor__` |
| `a |= b` | `__ior__` |

Important rules:
- return `NotImplemented` when an operator does not support the other operand type
- do not raise `NotImplementedError` for normal binary dispatch
- in-place methods may mutate `self` and return it, or return a new object

Related numeric hooks that are not infix operators:
- `__round__` for `round(obj)`
- `__trunc__` for `math.trunc(obj)`
- `__floor__` for `math.floor(obj)`
- `__ceil__` for `math.ceil(obj)`

Example:

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)
```

## 12.10 Class creation hooks and metaclasses

Classes are objects too. The default metaclass is `type`, which means ordinary class creation is handled by `type`.

Conceptually, this:

```python
class User:
    pass
```

is similar to:

```python
User = type("User", (), {})
```

### `__init_subclass__`

`__init_subclass__` is a hook on a base class that runs whenever a subclass is created.

```python
class PluginBase:
    registry = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        PluginBase.registry.append(cls)

class AudioPlugin(PluginBase):
    pass
```

This is often enough when you want to:
- register subclasses
- validate subclass attributes
- enforce a simple class-level convention

### Metaclasses

A metaclass is a class whose instances are themselves classes.

```python
class Meta(type):
    def __new__(mcls, name, bases, namespace):
        namespace["kind"] = name.lower()
        return super().__new__(mcls, name, bases, namespace)

class Example(metaclass=Meta):
    pass

print(Example.kind)  # example
```

Important metaclass hooks:
- `__prepare__(name, bases, **kwargs)` supplies the mapping used for the class body namespace before the class body runs
- metaclass `__new__` builds the class object
- metaclass `__init__` initializes the class object after creation

Practical guidance:
- use a normal class first
- use a class decorator or `__init_subclass__` if that is enough
- use a metaclass only when you really need to control class creation itself

## 12.11 Async protocols

Async code has its own protocols, parallel to the synchronous ones.

| Syntax | Protocol methods |
| --- | --- |
| `await obj` | `__await__` |
| `async for x in obj` | `__aiter__`, `__anext__` |
| `async with obj` | `__aenter__`, `__aexit__` |

`__await__`:
- used by `await obj`
- must return an iterator that drives the awaitable operation

`__aiter__` and `__anext__`:
- define the async iteration protocol
- `__aiter__` returns an async iterator
- `__anext__` returns an awaitable that eventually produces the next value
- when the async iterator is finished, it raises `StopAsyncIteration`

```python
class AsyncCounter:
    def __init__(self, stop):
        self.current = 0
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        value = self.current
        self.current += 1
        return value
```

`__aenter__` and `__aexit__`:
- define the async context manager protocol used by `async with`
- both methods are awaited
- like `__exit__`, `__aexit__` can suppress an exception by returning a truthy value

`StopAsyncIteration` is different from `StopIteration`:
- `StopIteration` ends a normal iterator
- `StopAsyncIteration` ends an async iterator

Chapter 18 expands on asynchronous programming. This section only introduces the protocol hooks.

## 12.12 Quick reference summary

| Syntax or built-in | Main hook |
| --- | --- |
| `Class(args)` | metaclass `__call__`, then `__new__`, then `__init__` |
| `repr(obj)` | `__repr__` |
| `str(obj)`, `print(obj)` | `__str__` |
| `bytes(obj)` | `__bytes__` |
| `format(obj, spec)`, `f"{obj:spec}"` | `__format__` |
| `bool(obj)` | `__bool__` or fallback to `__len__` |
| `len(obj)` | `__len__` |
| `obj[key]` | `__getitem__` |
| `obj[key] = value` | `__setitem__` |
| `del obj[key]` | `__delitem__` |
| `item in obj` | `__contains__` |
| `iter(obj)` | `__iter__` |
| `next(it)` | `__next__` |
| `obj()` | `__call__` |
| `a == b`, `a < b`, and so on | comparison methods such as `__eq__`, `__lt__` |
| `a + b`, `a * b`, `a << b`, and so on | operator methods such as `__add__`, `__mul__`, `__lshift__` |
| `with obj` | `__enter__`, `__exit__` |
| `obj.attr`, `obj.attr = value`, `del obj.attr` | `__getattribute__`, `__getattr__`, `__setattr__`, `__delattr__`, descriptors |
| class creation | `__init_subclass__`, metaclass hooks |
| `await obj` | `__await__` |
| `async for x in obj` | `__aiter__`, `__anext__` |
| `async with obj` | `__aenter__`, `__aexit__` |

---

## 13. Iterables, iterators, generators, and comprehensions

## 13.1 Iterable vs iterator

- **Iterable**: can produce an iterator
- **Iterator**: produces values one by one and remembers state

```python
nums = [1, 2, 3]      # iterable
it = iter(nums)       # iterator

print(next(it))       # 1
print(next(it))       # 2
```

## 13.2 `for` works with iterators

```python
for x in [10, 20, 30]:
    print(x)
```

Internally, `for` uses `iter()` and `next()` until `StopIteration`.

## 13.3 List comprehensions

```python
squares = [x * x for x in range(6)]
print(squares)
```

With condition:

```python
evens = [x for x in range(10) if x % 2 == 0]
```

## 13.4 Set and dict comprehensions

```python
unique_lengths = {len(word) for word in ["a", "to", "tea", "a"]}

mapping = {x: x * x for x in range(5)}
```

## 13.5 Generator expressions

```python
gen = (x * x for x in range(5))
print(next(gen))
```

## 13.6 Generators with `yield`

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for n in countdown(3):
    print(n)
```

## 13.7 `yield from`

```python
def chain():
    yield from [1, 2, 3]
    yield from [4, 5]
```

## 13.8 Why generators matter

They are memory-efficient for streams or large data.

```python
def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()
```

---

## 14. Exceptions and error handling

## 14.1 What exceptions are

Exceptions are objects representing errors or unusual conditions.

## 14.2 Basic `try` / `except`

```python
try:
    x = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
```

## 14.3 Catching multiple exceptions

```python
try:
    value = int("abc")
except (ValueError, TypeError) as e:
    print("Problem:", e)
```

## 14.4 `else` and `finally`

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("error")
else:
    print("success:", result)
finally:
    print("always runs")
```

- `else` runs if no exception occurs
- `finally` runs whether or not an exception occurs

## 14.5 Raising exceptions

```python
def divide(a, b):
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b
```

## 14.6 Custom exceptions

```python
class InvalidAgeError(Exception):
    pass
```

## 14.7 Exception chaining

```python
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("Conversion failed") from e
```

## 14.8 `assert`

```python
def sqrt(x):
    assert x >= 0, "x must be non-negative"
```

Use `assert` for internal sanity checks, not for user-facing validation in production logic.

## 14.9 Exception groups and `except*`

Modern Python also supports handling multiple exceptions bundled together with `ExceptionGroup` and `except*`.

```python
try:
    raise ExceptionGroup("many errors", [ValueError("bad"), TypeError("wrong")])
except* ValueError as eg:
    print("value errors:", eg)
except* TypeError as eg:
    print("type errors:", eg)
```

This is mainly useful in concurrent and advanced error-aggregation scenarios.

---

## 15. Files, I/O, serialization, and context managers

## 15.1 Reading files

```python
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()
```

## 15.2 Writing files

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello\n")
```

## 15.3 Why `with` is preferred

`with` ensures cleanup.

```python
with open("data.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

## 15.4 JSON

```python
import json

data = {"name": "Ana", "age": 20}

text = json.dumps(data)
again = json.loads(text)
```

## 15.5 CSV

```python
import csv

with open("items.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

## 15.6 Pickle

```python
import pickle

obj = {"x": 1}

blob = pickle.dumps(obj)
restored = pickle.loads(blob)
```

Use pickle only with trusted data.

## 15.7 Custom context managers

### Class-based

```python
class Managed:
    def __enter__(self):
        print("start")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("end")
```

### Generator-based

```python
from contextlib import contextmanager

@contextmanager
def managed():
    print("start")
    try:
        yield
    finally:
        print("end")
```

---

## 16. Decorators

A decorator takes a callable and returns a modified callable.

## 16.1 Basic example

```python
def debug(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@debug
def add(a, b):
    return a + b
```

## 16.2 Preserving metadata with `functools.wraps`

```python
from functools import wraps

def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

## 16.3 Decorators with arguments

```python
from functools import wraps

def repeat(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("hello")
```

## 16.4 Common built-in decorators

- `@property`
- `@classmethod`
- `@staticmethod`
- `@dataclass`

---

## 17. Typing and annotations

## 17.1 Basic annotations

```python
name: str = "Alice"
age: int = 22

def add(a: int, b: int) -> int:
    return a + b
```

## 17.2 Important fact about typing

Type hints help:
- editors,
- linters,
- static type checkers,
- documentation,
- readability.

They do **not** automatically enforce types at runtime.

## 17.3 Common generic types

```python
def total(values: list[int]) -> int:
    return sum(values)

def invert(d: dict[str, int]) -> dict[int, str]:
    return {v: k for k, v in d.items()}
```

## 17.4 `Optional` and unions

Modern syntax:

```python
def greet(name: str | None) -> str:
    if name is None:
        return "Hello, guest"
    return f"Hello, {name}"
```

Equivalent older style:

```python
from typing import Optional

def greet(name: Optional[str]) -> str:
    ...
```

## 17.5 `Any`

```python
from typing import Any

def echo(x: Any) -> Any:
    return x
```

Use `Any` deliberately; too much of it reduces type-checking value.

## 17.6 Type aliases

```python
UserId = int
```

## 17.7 Protocols and duck typing

```python
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None: ...
```

A protocol describes required behavior rather than a specific inheritance chain.

## 17.8 Typed dictionaries

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int
```

## 17.9 Literals and overloads

```python
from typing import Literal

def set_mode(mode: Literal["r", "w"]) -> None:
    print(mode)
```

## 17.10 Generics

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

---

## 18. Asynchronous programming

Async programming is useful for I/O-bound concurrency, such as:
- network requests,
- websocket servers,
- async APIs,
- many waiting tasks.

## 18.1 `async def` and `await`

```python
import asyncio

async def say_hi():
    await asyncio.sleep(1)
    print("Hi")

asyncio.run(say_hi())
```

## 18.2 Running multiple coroutines

```python
import asyncio

async def work(name, delay):
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    results = await asyncio.gather(
        work("A", 1),
        work("B", 2),
    )
    print(results)

asyncio.run(main())
```

## 18.3 Async iterators and async context managers

```python
class AsyncCounter:
    def __init__(self, stop):
        self.current = 0
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        value = self.current
        self.current += 1
        return value
```

## 18.4 `async for` and `async with`

```python
async def consume(counter):
    async for item in counter:
        print(item)
```

`async with` is the asynchronous form of context management and is used when entering or exiting the managed block itself requires awaiting.

## 18.5 When not to use async

Do not use async just because it looks modern.

It helps mainly when your program spends time **waiting** for I/O.  
For CPU-heavy work, threads, processes, or native extensions may be more suitable.

---

## 19. Useful standard-library concepts every Python programmer should know

These are not the whole standard library, but they are core practical tools.

## 19.1 `pathlib`

```python
from pathlib import Path

p = Path("data") / "file.txt"
print(p.exists())
```

## 19.2 `collections`

```python
from collections import Counter, defaultdict

print(Counter("banana"))

groups = defaultdict(list)
groups["a"].append(1)
```

## 19.3 `itertools`

```python
from itertools import count, combinations

c = count(start=10, step=2)
print(next(c))
print(list(combinations([1, 2, 3], 2)))
```

## 19.4 `functools`

```python
from functools import lru_cache, reduce

@lru_cache
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(reduce(lambda a, b: a + b, [1, 2, 3], 0))
```

## 19.5 `enum`

Python has a built-in `enum` module, but its `Enum` type is **not** the same as a full Rust `enum`.

Use `Enum` when you want a fixed set of named constant values.

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)        # Color.RED
print(Color.RED.name)   # RED
print(Color.RED.value)  # 1
```

This is roughly similar to a simple Rust enum whose variants do **not** carry extra data.

Important distinction:

- Python `Enum` = named constant members
- Rust `enum` = can also represent variants that carry **different data shapes**

Python does **not** have one built-in construct that exactly matches Rust's "data-carrying enum variants" (also called a tagged union or algebraic data type).

A common Python way to model that idea is:

1. define one class per variant, often with `@dataclass`
2. combine them with a union type
3. use `match` / `case` to branch by variant shape

Example:

```python
from dataclasses import dataclass

@dataclass
class Quit:
    pass

@dataclass
class Move:
    x: int
    y: int

@dataclass
class Write:
    text: str

Message = Quit | Move | Write

def handle(msg: Message) -> str:
    match msg:
        case Quit():
            return "quit"
        case Move(x, y):
            return f"move to {x}, {y}"
        case Write(text):
            return f"write: {text}"

print(handle(Move(10, 20)))   # move to 10, 20
print(handle(Write("hello"))) # write: hello
```

So the closest mental model is:

- `Enum` is the Python equivalent of a Rust enum with only simple named variants
- `dataclass` + union types + `match` is the closest Python style to Rust enums with payloads

## 19.6 `datetime`

```python
from datetime import datetime

now = datetime.now()
print(now.isoformat())
```

## 19.7 `re`

```python
import re

match = re.search(r"\d+", "Order 123")
print(match.group())  # 123
```

## 19.8 `os` and `sys`

```python
import os
import sys

print(os.getcwd())
print(sys.version)
print(sys.argv)
```

## 19.9 Virtual environments

A virtual environment isolates dependencies per project.

```bash
python -m venv .venv
```

Activate it, then install packages with `pip`.

---

## 20. Testing, debugging, and introspection

## 20.1 `unittest`

```python
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == "__main__":
    unittest.main()
```

## 20.2 `doctest`

```python
def square(x):
    """
    >>> square(4)
    16
    """
    return x * x
```

## 20.3 Debugging with `breakpoint()`

```python
def compute(x):
    breakpoint()
    return x * 2
```

## 20.4 Introspection tools

```python
print(type([]))
print(isinstance([], list))
print(dir(str))
print(help(len))
```

---

## 21. Pythonic idioms and best practices

## 21.1 Prefer direct iteration

Good:

```python
for item in items:
    print(item)
```

Less ideal when index is unnecessary:

```python
for i in range(len(items)):
    print(items[i])
```

## 21.2 Prefer `enumerate()` when you need index + value

```python
for i, value in enumerate(items):
    print(i, value)
```

## 21.3 Prefer `zip()` for parallel iteration

```python
names = ["A", "B"]
scores = [90, 80]

for name, score in zip(names, scores):
    print(name, score)
```

## 21.4 Use comprehensions when clear

Good:

```python
squares = [x * x for x in range(10)]
```

Do not force comprehensions into unreadable one-liners.

## 21.5 EAFP vs LBYL

Python often favors **EAFP**:
> Easier to Ask Forgiveness than Permission

```python
try:
    value = d["key"]
except KeyError:
    value = None
```

Instead of always checking first:

```python
if "key" in d:
    value = d["key"]
else:
    value = None
```

Both styles are useful; choose based on clarity and context.

## 21.6 Use `with` for managed resources

```python
with open("file.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

## 21.7 Write small functions with clear names

This improves readability and testability.

## 21.8 Follow PEP 8 in normal codebases

Examples:
- 4-space indentation
- meaningful names
- spaces around operators
- keep lines readable
- blank lines between logical sections

---

## 22. Common pitfalls

## 22.1 Mutable default arguments

Already covered earlier, but worth repeating:
- never use mutable objects as defaults unless you explicitly want shared state.

## 22.2 Aliasing surprises

```python
a = [[0] * 3] * 2
a[0][0] = 99
print(a)  # both rows change
```

Safer:

```python
a = [[0] * 3 for _ in range(2)]
```

## 22.3 Modifying a list while iterating over it

Bad:

```python
nums = [1, 2, 3, 4]
for x in nums:
    if x % 2 == 0:
        nums.remove(x)
```

Safer:

```python
nums = [x for x in nums if x % 2 != 0]
```

## 22.4 Floating-point precision

```python
print(0.1 + 0.2)  # 0.30000000000000004
```

For exact decimal arithmetic in financial contexts, consider `decimal.Decimal`.

## 22.5 Confusing `is` with `==`

```python
a = 1000
b = 1000
print(a == b)  # compare values
```

Use `is` only for identity checks such as `x is None`.

## 22.6 Catching very broad exceptions carelessly

Avoid this unless you truly mean it:

```python
try:
    do_work()
except Exception:
    pass
```

It can hide real bugs.

## 22.7 Shadowing built-ins

Avoid names like:

```python
list = [1, 2, 3]
str = "hello"
sum = 10
```

These override built-in names in your current scope.

---

## 23. Modern Python 3.14 notes

These are modern-language notes worth knowing when revising Python today.

## 23.1 Annotations are now deferred by default

Modern Python evaluates annotations lazily when accessed, which changes some runtime behavior around `__annotations__` and forward references.

Practical takeaway:
- annotations are still mainly for tooling and introspection,
- runtime behavior around them has evolved,
- avoid depending on obscure old annotation-evaluation behavior.

## 23.2 Template string literals (t-strings)

Python 3.14 introduced **template string literals** using a `t` prefix.

```python
# Example syntax
message = t"Hello {name}"
```

These are related to formatted string syntax, but they produce a template object for custom processing rather than an ordinary `str` in the same way as an f-string.

This is a newer feature; most existing Python code still relies mainly on:
- regular strings,
- f-strings,
- `str.format()`.

## 23.3 Pattern matching, async, and typing are mainstream modern Python concepts

If you are revising Python for interviews, real projects, or advanced study, make sure you are comfortable with:
- structural pattern matching,
- type hints,
- async/await,
- dataclasses,
- context managers,
- generators.

---

## 24. Revision checklist

Use this list to verify your understanding.

### Syntax and basics
- [ ] indentation
- [ ] comments and docstrings
- [ ] names, keywords, literals
- [ ] statements vs expressions

### Data model
- [ ] objects, identity, type, value
- [ ] mutability vs immutability
- [ ] `==` vs `is`
- [ ] copying and aliasing

### Core types
- [ ] numbers
- [ ] booleans and `None`
- [ ] strings
- [ ] lists
- [ ] tuples
- [ ] sets / frozensets
- [ ] dictionaries
- [ ] bytes / bytearray / memoryview
- [ ] hashability
- [ ] truthiness

### Expressions and operators
- [ ] arithmetic
- [ ] comparisons
- [ ] logical operators
- [ ] membership and identity
- [ ] bitwise operators
- [ ] walrus operator
- [ ] conditional expressions
- [ ] unpacking operators
- [ ] lambda

### Control flow
- [ ] `if / elif / else`
- [ ] `for`
- [ ] `while`
- [ ] `break / continue / pass`
- [ ] `del`
- [ ] loop `else`
- [ ] `match / case`

### Functions
- [ ] parameters and arguments
- [ ] defaults
- [ ] `*args` and `**kwargs`
- [ ] positional-only and keyword-only params
- [ ] return values
- [ ] recursion
- [ ] higher-order functions
- [ ] annotations

### Scope
- [ ] LEGB
- [ ] closures
- [ ] `global`
- [ ] `nonlocal`

### Modules and packaging
- [ ] imports
- [ ] packages
- [ ] `__name__ == "__main__"`
- [ ] import side effects

### OOP
- [ ] classes and instances
- [ ] attributes and methods
- [ ] inheritance
- [ ] `super()`
- [ ] class methods
- [ ] static methods
- [ ] properties
- [ ] dataclasses
- [ ] `__slots__`
- [ ] ABCs

### Data model protocols
- [ ] `__new__`, `__init__`, `__del__`
- [ ] `__repr__`, `__str__`, `__bytes__`, `__format__`
- [ ] truthiness, comparisons, `__hash__`
- [ ] `__len__`, `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`
- [ ] `__iter__`, `__next__`
- [ ] `__call__`
- [ ] descriptors, `__getattribute__`, `__getattr__`
- [ ] context manager protocol
- [ ] operator overloading
- [ ] `__init_subclass__`, metaclasses
- [ ] async protocols

### Iteration tools
- [ ] iterables vs iterators
- [ ] comprehensions
- [ ] generator expressions
- [ ] generators
- [ ] `yield from`

### Errors and resources
- [ ] exceptions
- [ ] `try / except / else / finally`
- [ ] `raise`
- [ ] custom exceptions
- [ ] `assert`
- [ ] `ExceptionGroup` / `except*`
- [ ] `with`
- [ ] file handling
- [ ] JSON / CSV / pickle basics

### Advanced practical topics
- [ ] decorators
- [ ] type hints
- [ ] protocols and generics
- [ ] async / await
- [ ] testing
- [ ] introspection
- [ ] Pythonic idioms
- [ ] common pitfalls

---

## 25. References

This guide was prepared against the official Python documentation, especially:

1. The Python Tutorial  
2. The Python Language Reference  
3. Data model  
4. Built-in types  
5. Built-in exceptions  
6. `typing` module documentation  
7. What’s New in Python 3.14  

Official documentation home:
- https://docs.python.org/3/

Suggested next study order from the official docs:
1. Tutorial
2. Language Reference
3. Standard Library
4. What’s New for your target Python version

---

## Final note

No single revision file can literally replace the entire official specification and every standard-library page, but this document covers the **important Python language concepts and practical core ideas that a serious Python learner is expected to know**. If you can explain every section above and write the examples yourself, your Python foundation is strong.
