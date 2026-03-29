# PyTorch Revision Notes: Important Concepts with Examples

> Reviewed against the current stable PyTorch documentation line (**2.11 stable**) on **2026-03-28**.
>
> This file is designed for **revision**: it aims to cover the **important concepts** you are expected to know in real PyTorch work. No single file can literally contain every operator and edge case in the ecosystem, but this guide is intentionally broad and practical.

---

## Table of Contents

1. [What PyTorch is](#1-what-pytorch-is)
2. [Installation and imports](#2-installation-and-imports)
3. [Tensor fundamentals](#3-tensor-fundamentals)
4. [Autograd and gradients](#4-autograd-and-gradients)
5. [`nn.Module`, parameters, buffers, and model structure](#5-nnmodule-parameters-buffers-and-model-structure)
6. [Built-in layers and the functional API](#6-built-in-layers-and-the-functional-api)
7. [Loss functions](#7-loss-functions)
8. [Data pipeline: `Dataset`, `DataLoader`, samplers, collate functions](#8-data-pipeline-dataset-dataloader-samplers-collate-functions)
9. [The training loop](#9-the-training-loop)
10. [Evaluation and inference](#10-evaluation-and-inference)
11. [Optimizers and learning-rate schedulers](#11-optimizers-and-learning-rate-schedulers)
12. [Devices, dtypes, memory, and performance basics](#12-devices-dtypes-memory-and-performance-basics)
13. [Saving, loading, and checkpointing](#13-saving-loading-and-checkpointing)
14. [`torch.compile`, FX, `torch.export`, ONNX, and deployment](#14-torchcompile-fx-torchexport-onnx-and-deployment)
15. [`torch.func` and higher-order transforms](#15-torchfunc-and-higher-order-transforms)
16. [Distributed training and large-scale training](#16-distributed-training-and-large-scale-training)
17. [Quantization](#17-quantization)
18. [Profiling, debugging, reproducibility, and testing](#18-profiling-debugging-reproducibility-and-testing)
19. [Extending PyTorch](#19-extending-pytorch)
20. [Common mistakes and best practices](#20-common-mistakes-and-best-practices)
21. [End-to-end example](#21-end-to-end-example)
22. [What to revise before interviews or exams](#22-what-to-revise-before-interviews-or-exams)
23. [Official references](#23-official-references)

---

## 1. What PyTorch is

PyTorch is a Python-first deep learning framework centered around:

- **Tensors**: N-dimensional arrays with GPU support
- **Autograd**: automatic differentiation
- **`nn.Module`**: reusable neural-network components
- **Optimizers**: parameter update algorithms
- **Data utilities**: datasets, loaders, samplers
- **Compilation/export/deployment tools**: `torch.compile`, `torch.export`, ONNX export, etc.
- **Distributed training**: DDP, FSDP, distributed checkpointing

You can think of a typical PyTorch workflow as:

1. Load data
2. Build model
3. Compute loss
4. Backpropagate gradients
5. Update parameters
6. Save/export/deploy

---

## 2. Installation and imports

Always use the official installer selector on the PyTorch “Get Started” page because install commands depend on:

- OS
- Python version
- package manager
- CUDA / ROCm / CPU-only choice

Basic imports:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
```

Check the environment:

```python
print(torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("MPS available:", torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False)
```

Choose a device:

```python
if torch.cuda.is_available():
    device = torch.device("cuda")
elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print(device)
```

---

## 3. Tensor fundamentals

### 3.1 Creating tensors

```python
import torch

x = torch.tensor([1, 2, 3], dtype=torch.float32)
zeros = torch.zeros(2, 3)
ones = torch.ones(2, 3)
randn = torch.randn(2, 3)
arange = torch.arange(0, 10, 2)

print(x)
print(randn)
```

### 3.2 Shape, rank, dtype, and device

```python
x = torch.randn(4, 5, 6)

print(x.shape)      # torch.Size([4, 5, 6])
print(x.ndim)       # 3
print(x.dtype)      # torch.float32
print(x.device)     # cpu or cuda:0
```

Important terms:

- **shape**: tensor dimensions
- **rank / ndim**: number of dimensions
- **dtype**: data type (`float32`, `int64`, `bfloat16`, etc.)
- **device**: where the tensor lives (`cpu`, `cuda`, `mps`, ...)

### 3.3 Common dtypes

Frequently used dtypes:

- `torch.float32` — default floating-point dtype
- `torch.float64` — higher precision, slower
- `torch.float16` — mixed precision on supported accelerators
- `torch.bfloat16` — mixed precision with larger exponent range
- `torch.int64` (`torch.long`) — common for class indices and embeddings
- `torch.bool` — masks

```python
x = torch.tensor([1, 2, 3], dtype=torch.long)
mask = torch.tensor([True, False, True], dtype=torch.bool)
```

### 3.4 Tensor creation “like” another tensor

```python
x = torch.randn(2, 3, device=device)
y = torch.zeros_like(x)
z = torch.ones_like(x, dtype=torch.float64)
```

### 3.5 Reshaping and views

```python
x = torch.arange(12)
a = x.reshape(3, 4)
b = a.view(2, 6)    # requires compatible memory layout
c = a.flatten()

print(a)
print(b)
print(c)
```

Use:

- `reshape()` when you want the safest general option
- `view()` when you know the tensor layout is compatible
- `flatten()` to collapse dimensions
- `squeeze()` / `unsqueeze()` to remove/add size-1 dimensions

```python
x = torch.randn(1, 3, 1, 5)
print(x.squeeze().shape)      # [3, 5]
print(x.unsqueeze(0).shape)   # [1, 1, 3, 1, 5]
```

### 3.6 Transpose and permute

```python
x = torch.randn(2, 3)
print(x.T.shape)  # [3, 2]

y = torch.randn(2, 3, 4)
z = y.permute(0, 2, 1)   # [2, 4, 3]
print(z.shape)
```

### 3.7 Indexing and slicing

```python
x = torch.arange(12).reshape(3, 4)

print(x[0])        # first row
print(x[:, 1])     # second column
print(x[1:3, 2:4])
print(x[-1])
```

Boolean masking:

```python
x = torch.tensor([1.0, -2.0, 3.0, -4.0])
print(x[x > 0])    # tensor([1., 3.])
```

### 3.8 Basic operations

```python
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

print(a + b)
print(a - b)
print(a * b)              # elementwise
print(a / b)
print(torch.dot(a, b))    # dot product
```

Matrix multiplication:

```python
A = torch.randn(2, 3)
B = torch.randn(3, 4)
C = A @ B
print(C.shape)  # [2, 4]
```

### 3.9 Reductions

```python
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])

print(x.sum())
print(x.mean())
print(x.max())
print(x.sum(dim=0))
print(x.mean(dim=1))
```

### 3.10 Broadcasting

PyTorch follows NumPy-style broadcasting.

```python
x = torch.ones(2, 3)
b = torch.tensor([10.0, 20.0, 30.0])  # shape [3]
y = x + b

print(y)
```

Broadcasting works when dimensions are compatible from the right side.

### 3.11 In-place operations

Operations ending with `_` are in-place:

```python
x = torch.tensor([1.0, 2.0, 3.0])
x.add_(1.0)
print(x)  # tensor([2., 3., 4.])
```

Be careful: in-place operations can interfere with autograd if they overwrite values needed for gradient computation.

### 3.12 NumPy interop

```python
import numpy as np
import torch

x = torch.tensor([1.0, 2.0, 3.0])
n = x.numpy()

print(type(n))  # numpy.ndarray

t = torch.from_numpy(np.array([4.0, 5.0, 6.0]))
print(t)
```

CPU tensors and NumPy arrays can share memory.

### 3.13 Copying, detaching, and cloning

```python
x = torch.randn(3, requires_grad=True)
y = x.detach()       # stops gradient tracking
z = x.clone()        # copies data, keeps grad history relation
w = x.detach().clone()  # independent tensor, no grad history
```

### 3.14 Useful tensor utilities

```python
x = torch.randn(2, 3)
scalar = torch.tensor(3.14)

print(x.numel())         # number of elements
print(scalar.item())     # only for 1-element tensors
print(x.tolist())        # convert to Python list
```

---

## 4. Autograd and gradients

Autograd is PyTorch’s automatic differentiation engine.

### 4.1 `requires_grad`

```python
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x + 1
print(y)  # tensor(..., grad_fn=...)
```

### 4.2 `.backward()`

```python
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x + 1
y.backward()

print(x.grad)  # derivative of y wrt x = 2x + 2 = 8
```

### 4.3 Computation graphs

```python
x = torch.tensor(2.0, requires_grad=True)
y = x * x
z = y + 3

print(y.grad_fn)
print(z.grad_fn)
```

Tensors produced from tracked operations have a `grad_fn`.

### 4.4 Gradient accumulation

Gradients accumulate by default.

```python
x = torch.tensor(2.0, requires_grad=True)

y1 = x ** 2
y1.backward()
print(x.grad)  # 4

y2 = 3 * x
y2.backward()
print(x.grad)  # 7, not 3
```

That is why training loops usually clear gradients every iteration.

### 4.5 Zeroing gradients

```python
model = nn.Linear(10, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

optimizer.zero_grad(set_to_none=True)
```

`set_to_none=True` is a common efficient choice.

### 4.6 Scalar vs non-scalar backward

`.backward()` without arguments works naturally for a scalar output.

```python
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y = x ** 2

# y.backward() would fail because y is not scalar
y.sum().backward()
print(x.grad)
```

### 4.7 `torch.autograd.grad`

Use it when you want gradients returned directly instead of accumulated in `.grad`.

```python
x = torch.tensor(2.0, requires_grad=True)
y = x ** 3

(grad_x,) = torch.autograd.grad(y, x)
print(grad_x)  # 12
```

### 4.8 `detach()`, `no_grad()`, and `inference_mode()`

#### `detach()`
Stops tracking for a specific tensor.

```python
x = torch.randn(3, requires_grad=True)
y = x.detach()
```

#### `torch.no_grad()`
Disables gradient calculation in a block.

```python
model = nn.Linear(4, 2)
x = torch.randn(8, 4)

with torch.no_grad():
    y = model(x)
```

#### `torch.inference_mode()`
Like `no_grad()`, but more restrictive and often faster for pure inference.

```python
with torch.inference_mode():
    y = model(x)
```

Rule of thumb:

- Use **`no_grad()`** for general evaluation if you just want no gradients.
- Use **`inference_mode()`** when you are sure the block is pure inference and won’t interact with autograd later.

### 4.9 Higher-order gradients

```python
x = torch.tensor(2.0, requires_grad=True)
y = x ** 3

(dy_dx,) = torch.autograd.grad(y, x, create_graph=True)
(d2y_dx2,) = torch.autograd.grad(dy_dx, x)

print(dy_dx)    # 12
print(d2y_dx2)  # 12
```

### 4.10 Custom autograd with `torch.autograd.Function`

Use this only when built-in PyTorch operations are not enough.

```python
class Square(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x * x

    @staticmethod
    def backward(ctx, grad_output):
        (x,) = ctx.saved_tensors
        return grad_output * 2 * x

x = torch.tensor(3.0, requires_grad=True)
y = Square.apply(x)
y.backward()
print(x.grad)  # 6
```

---

## 5. `nn.Module`, parameters, buffers, and model structure

`nn.Module` is the base class for neural network modules.

### 5.1 A simple module

```python
class MLP(nn.Module):
    def __init__(self, in_features, hidden, out_features):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden)
        self.fc2 = nn.Linear(hidden, out_features)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)

model = MLP(10, 32, 2)
print(model)
```

### 5.2 Parameters

Trainable tensors should usually be `nn.Parameter`.

```python
class MyLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(5, 5))

    def forward(self, x):
        return x @ self.weight
```

### 5.3 Buffers

Buffers are tensors stored in the module state but not optimized.

Examples:

- running mean / variance in BatchNorm
- masks
- constant lookup tables

```python
class MyModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer("scale", torch.tensor(0.5))

    def forward(self, x):
        return x * self.scale
```

Difference:

- **Parameter**: appears in `model.parameters()`
- **Buffer**: appears in `model.buffers()`
- Both can appear in `state_dict()` if the buffer is persistent

### 5.4 Containers

Useful module containers:

- `nn.Sequential`
- `nn.ModuleList`
- `nn.ModuleDict`
- `nn.ParameterList`
- `nn.ParameterDict`

Example:

```python
model = nn.Sequential(
    nn.Linear(10, 32),
    nn.ReLU(),
    nn.Linear(32, 2),
)
```

Use `ModuleList` when structure is dynamic:

```python
class DeepMLP(nn.Module):
    def __init__(self, widths):
        super().__init__()
        self.layers = nn.ModuleList(
            [nn.Linear(widths[i], widths[i + 1]) for i in range(len(widths) - 1)]
        )

    def forward(self, x):
        for layer in self.layers[:-1]:
            x = F.relu(layer(x))
        return self.layers[-1](x)
```

### 5.5 `state_dict()`

```python
model = nn.Linear(4, 2)
state = model.state_dict()

for name, value in state.items():
    print(name, value.shape)
```

`state_dict()` is the standard way to save model weights.

### 5.6 Train and eval modes

```python
model.train()   # enables training behavior
model.eval()    # enables evaluation behavior
```

This matters for modules like:

- `Dropout`
- `BatchNorm`

### 5.7 Hooks

Common hooks:

- forward hooks
- full backward hooks

Use hooks for debugging, feature extraction, and analysis.

```python
def forward_hook(module, inputs, output):
    print(f"{module.__class__.__name__} output shape:", output.shape)

model = nn.Linear(4, 2)
handle = model.register_forward_hook(forward_hook)

x = torch.randn(3, 4)
_ = model(x)

handle.remove()
```

Use hooks carefully: they can make code harder to reason about.

### 5.8 Initialization

```python
layer = nn.Linear(10, 20)
nn.init.xavier_uniform_(layer.weight)
nn.init.zeros_(layer.bias)
```

Popular initialization choices:

- Xavier / Glorot
- Kaiming / He
- zeros for some biases

---

## 6. Built-in layers and the functional API

PyTorch provides many standard layers.

### 6.1 Common learnable layers

- `nn.Linear`
- `nn.Conv1d`, `nn.Conv2d`, `nn.Conv3d`
- `nn.Embedding`
- `nn.LSTM`, `nn.GRU`, `nn.RNN`
- `nn.MultiheadAttention`
- `nn.TransformerEncoderLayer`, `nn.TransformerDecoderLayer`

Example: convolution

```python
conv = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
x = torch.randn(8, 3, 32, 32)
y = conv(x)
print(y.shape)  # [8, 16, 32, 32]
```

### 6.2 Activations

Module style:

```python
relu = nn.ReLU()
x = torch.tensor([-1.0, 0.0, 1.0])
print(relu(x))
```

Functional style:

```python
x = torch.tensor([-1.0, 0.0, 1.0])
print(F.relu(x))
```

Common activations:

- `ReLU`
- `LeakyReLU`
- `GELU`
- `SiLU`
- `Tanh`
- `Sigmoid`
- `Softmax`

### 6.3 Pooling and normalization

```python
pool = nn.MaxPool2d(kernel_size=2)
bn = nn.BatchNorm2d(16)

x = torch.randn(8, 16, 32, 32)
print(pool(x).shape)   # [8, 16, 16, 16]
print(bn(x).shape)     # [8, 16, 32, 32]
```

Common normalization layers:

- `BatchNorm*`
- `LayerNorm`
- `GroupNorm`
- `InstanceNorm*`
- `RMSNorm` (depending on version/components you use)

### 6.4 Dropout

```python
drop = nn.Dropout(p=0.5)

x = torch.ones(5)
drop.train()
print(drop(x))   # random zeros

drop.eval()
print(drop(x))   # unchanged in eval mode
```

### 6.5 Functional API vs module API

Use **module API** when the layer has state or configuration you want stored in the model.

```python
self.dropout = nn.Dropout(0.2)
x = self.dropout(x)
```

Use **functional API** for stateless operations or when you want explicit control:

```python
x = F.relu(x)
loss = F.cross_entropy(logits, target)
```

A common pattern:

- Modules for layers with parameters/state
- Functional ops inside `forward`

### 6.6 Example: custom CNN

```python
class SmallCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.fc = nn.Linear(32 * 7 * 7, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # [B,16,14,14]
        x = self.pool(F.relu(self.conv2(x)))  # [B,32,7,7]
        x = x.flatten(1)
        return self.fc(x)
```

---

## 7. Loss functions

### 7.1 Regression

```python
pred = torch.tensor([[2.5], [0.3]])
target = torch.tensor([[3.0], [0.0]])

mse = nn.MSELoss()
print(mse(pred, target))
```

Common regression losses:

- `nn.MSELoss`
- `nn.L1Loss`
- `nn.SmoothL1Loss`
- `nn.HuberLoss`

### 7.2 Binary classification

Use **logits** with `BCEWithLogitsLoss`.

```python
logits = torch.tensor([[0.2], [-1.3], [2.1]])
target = torch.tensor([[1.0], [0.0], [1.0]])

criterion = nn.BCEWithLogitsLoss()
loss = criterion(logits, target)
print(loss)
```

Do **not** apply `sigmoid` manually before `BCEWithLogitsLoss`.

### 7.3 Multiclass classification

Use **logits** with `CrossEntropyLoss`.

```python
logits = torch.randn(4, 3)          # [batch, num_classes]
target = torch.tensor([0, 2, 1, 2]) # class indices

criterion = nn.CrossEntropyLoss()
loss = criterion(logits, target)
print(loss)
```

Do **not** apply `softmax` before `CrossEntropyLoss`.

### 7.4 Sequence modeling losses

Frequently used:

- `nn.CrossEntropyLoss`
- `nn.CTCLoss`
- token-level losses with masking

### 7.5 Reduction modes

Many losses accept `reduction=`:

- `"mean"`
- `"sum"`
- `"none"`

```python
criterion = nn.MSELoss(reduction="none")
loss_per_item = criterion(torch.tensor([1.0, 2.0]), torch.tensor([0.0, 2.0]))
print(loss_per_item)
```

---

## 8. Data pipeline: `Dataset`, `DataLoader`, samplers, collate functions

Data loading is central in PyTorch.

### 8.1 `Dataset`

Custom map-style dataset:

```python
class ToyDataset(Dataset):
    def __init__(self):
        self.x = torch.randn(100, 10)
        self.y = (self.x.sum(dim=1) > 0).long()

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

dataset = ToyDataset()
print(len(dataset))
print(dataset[0])
```

### 8.2 `DataLoader`

```python
loader = DataLoader(
    dataset,
    batch_size=16,
    shuffle=True,
    num_workers=0,
)

for batch_x, batch_y in loader:
    print(batch_x.shape, batch_y.shape)
    break
```

Key arguments:

- `batch_size`
- `shuffle`
- `sampler`
- `num_workers`
- `collate_fn`
- `pin_memory`
- `drop_last`
- `persistent_workers`

### 8.3 Map-style vs iterable-style datasets

#### Map-style
Implements `__getitem__` and `__len__`.

Good for:
- files on disk
- indexed datasets
- random access

#### Iterable-style
Implements `__iter__`.

Good for:
- streams
- logs
- remote sources
- huge datasets where indexing is not natural

```python
from torch.utils.data import IterableDataset

class StreamDataset(IterableDataset):
    def __iter__(self):
        for i in range(10):
            yield torch.tensor([i], dtype=torch.float32)

for x in DataLoader(StreamDataset(), batch_size=4):
    print(x)
```

### 8.4 Custom `collate_fn`

Useful when samples have variable shapes or need special batching logic.

```python
def my_collate(batch):
    xs, ys = zip(*batch)
    xs = torch.stack(xs)
    ys = torch.tensor(ys)
    return xs, ys

loader = DataLoader(dataset, batch_size=8, collate_fn=my_collate)
```

### 8.5 Samplers

Common samplers:

- `RandomSampler`
- `SequentialSampler`
- `WeightedRandomSampler`
- `DistributedSampler`

Example:

```python
weights = torch.ones(len(dataset))
sampler = torch.utils.data.WeightedRandomSampler(weights, num_samples=len(dataset), replacement=True)
loader = DataLoader(dataset, batch_size=16, sampler=sampler)
```

### 8.6 Performance-related settings

On GPU workloads, common choices are:

```python
loader = DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    persistent_workers=True,
)
```

Then transfer to GPU with:

```python
for x, y in loader:
    x = x.to(device, non_blocking=True)
    y = y.to(device, non_blocking=True)
```

---

## 9. The training loop

This is the core PyTorch skill.

### 9.1 Canonical training loop

```python
model = MLP(10, 32, 2).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

for epoch in range(5):
    model.train()

    for x, y in loader:
        x = x.to(device)
        y = y.to(device)

        optimizer.zero_grad(set_to_none=True)

        logits = model(x)
        loss = criterion(logits, y)

        loss.backward()
        optimizer.step()
```

### 9.2 The order matters

Typical order:

1. `model.train()`
2. move batch to device
3. `optimizer.zero_grad(...)`
4. forward pass
5. compute loss
6. `loss.backward()`
7. `optimizer.step()`

### 9.3 Gradient clipping

Useful in RNNs, transformers, and unstable training.

```python
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

### 9.4 Gradient accumulation

Use when effective batch size is larger than memory allows.

```python
accum_steps = 4
optimizer.zero_grad(set_to_none=True)

for step, (x, y) in enumerate(loader):
    x, y = x.to(device), y.to(device)
    logits = model(x)
    loss = criterion(logits, y) / accum_steps
    loss.backward()

    if (step + 1) % accum_steps == 0:
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
```

### 9.5 Mixed precision training (AMP)

Common on CUDA.

```python
model = model.to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()
scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))

for x, y in loader:
    x, y = x.to(device), y.to(device)
    optimizer.zero_grad(set_to_none=True)

    with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device.type == "cuda")):
        logits = model(x)
        loss = criterion(logits, y)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

Notes:

- On CUDA, AMP commonly uses `autocast` + `GradScaler`
- On CPU with `bfloat16`, `autocast` is common, and gradient scaling is usually not the main focus

### 9.6 Monitoring training

```python
running_loss = 0.0

for x, y in loader:
    x, y = x.to(device), y.to(device)
    optimizer.zero_grad(set_to_none=True)
    logits = model(x)
    loss = criterion(logits, y)
    loss.backward()
    optimizer.step()

    running_loss += loss.item()

print("avg loss:", running_loss / len(loader))
```

---

## 10. Evaluation and inference

### 10.1 Evaluation loop

```python
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        preds = logits.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += y.size(0)

print("accuracy:", correct / total)
```

### 10.2 Why `eval()` and `no_grad()` are both needed

- `model.eval()` changes module behavior (for example, Dropout and BatchNorm)
- `torch.no_grad()` disables gradient tracking

These do different things.

### 10.3 Inference mode

```python
model.eval()
with torch.inference_mode():
    logits = model(torch.randn(4, 10, device=device))
```

Use `inference_mode()` when you want maximum inference-oriented behavior.

---

## 11. Optimizers and learning-rate schedulers

### 11.1 Common optimizers

- `SGD`
- `Adam`
- `AdamW`
- `RMSprop`
- `Adagrad`

```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-2)
```

### 11.2 Parameter groups

Use different hyperparameters for different parts of the model.

```python
optimizer = torch.optim.AdamW([
    {"params": model.fc1.parameters(), "lr": 1e-3},
    {"params": model.fc2.parameters(), "lr": 1e-4},
], weight_decay=1e-2)
```

### 11.3 Schedulers

Common schedulers:

- `StepLR`
- `MultiStepLR`
- `ExponentialLR`
- `CosineAnnealingLR`
- `ReduceLROnPlateau`
- `OneCycleLR`
- warmup via custom logic or scheduler composition

Example:

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

for epoch in range(20):
    train_one_epoch(...)
    scheduler.step()
```

`ReduceLROnPlateau` is different: it steps on a metric.

```python
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=2)
val_loss = 0.42
scheduler.step(val_loss)
```

### 11.4 Inspecting learning rates

```python
for group in optimizer.param_groups:
    print(group["lr"])
```

---

## 12. Devices, dtypes, memory, and performance basics

### 12.1 Move tensors and models to a device

```python
model = model.to(device)
x = x.to(device)
```

The model and all tensor inputs used together must usually be on the same device.

### 12.2 CPU, CUDA, and MPS

Common devices:

- **CPU**: always available
- **CUDA**: NVIDIA GPUs
- **MPS**: Apple Silicon / Metal backend

### 12.3 Device-aware tensor creation

Bad pattern:

```python
x = torch.randn(4, 10, device=device)
y = torch.zeros(4, 10)  # defaults to CPU
```

Better:

```python
y = torch.zeros_like(x)
# or
y = torch.zeros(4, 10, device=device)
```

### 12.4 Dtype conversions

```python
x = torch.tensor([1, 2, 3])
print(x.dtype)  # int64

x = x.float()
print(x.dtype)  # float32
```

### 12.5 Memory basics

Useful CUDA utilities:

```python
if torch.cuda.is_available():
    print(torch.cuda.memory_allocated())
    print(torch.cuda.memory_reserved())
```

Clear unused cached CUDA memory if needed:

```python
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

This does **not** free tensors you still reference; it clears unused cached memory.

### 12.6 Asynchronous transfer with pinned memory

Use this pairing for GPU input pipelines:

- `pin_memory=True` in `DataLoader`
- `.to(device, non_blocking=True)` when transferring batches

### 12.7 Performance basics

Common performance ideas:

- use larger batches when memory allows
- keep data loading efficient
- avoid unnecessary CPU↔GPU transfers
- use AMP on supported hardware
- try `torch.compile`
- profile before guessing
- use `channels_last` for some vision models when appropriate
- prefer vectorized ops over Python loops

### 12.8 `torch.compile`

```python
model = MLP(10, 32, 2).to(device)
compiled_model = torch.compile(model)

x = torch.randn(16, 10, device=device)
y = compiled_model(x)
```

`torch.compile` can improve performance, but graph breaks and dynamic behavior can reduce gains.

### 12.9 `channels_last` memory format (vision workloads)

```python
model = SmallCNN().to(device).to(memory_format=torch.channels_last)
x = torch.randn(8, 1, 28, 28).to(device=device, memory_format=torch.channels_last)
```

This is not universal, but it can help some convolutional workloads.

---

## 13. Saving, loading, and checkpointing

### 13.1 Save and load tensors

```python
x = torch.tensor([1.0, 2.0])
torch.save(x, "tensor.pt")
x2 = torch.load("tensor.pt")
print(x2)
```

### 13.2 Recommended: save `state_dict()`

```python
torch.save(model.state_dict(), "model_weights.pt")
```

Load:

```python
model = MLP(10, 32, 2)
state_dict = torch.load("model_weights.pt", map_location="cpu")
model.load_state_dict(state_dict)
model.eval()
```

### 13.3 Save training checkpoints

```python
checkpoint = {
    "epoch": epoch,
    "model_state": model.state_dict(),
    "optimizer_state": optimizer.state_dict(),
}

torch.save(checkpoint, "checkpoint.pt")
```

Load:

```python
checkpoint = torch.load("checkpoint.pt", map_location="cpu")
model.load_state_dict(checkpoint["model_state"])
optimizer.load_state_dict(checkpoint["optimizer_state"])
start_epoch = checkpoint["epoch"] + 1
```

### 13.4 Why `state_dict()` is preferred

Saving whole Python model objects is less portable because it depends on pickled Python class definitions. Saving the `state_dict()` is the common best practice.

### 13.5 `map_location`

Use it when loading on a different device:

```python
state = torch.load("model_weights.pt", map_location="cpu")
```

### 13.6 Safety note

Modern serialization guidance increasingly emphasizes safer loading patterns such as using `weights_only=True` when appropriate.

```python
state = torch.load("model_weights.pt", map_location="cpu", weights_only=True)
```

Use this when loading a plain weights file and you do not need arbitrary pickled Python objects.

### 13.7 Distributed checkpointing

For large distributed training jobs, PyTorch also provides `torch.distributed.checkpoint` (DCP), which saves and loads distributed state in parallel and supports resharding.

---

## 14. `torch.compile`, FX, `torch.export`, ONNX, and deployment

This is an important modern area in PyTorch.

### 14.1 `torch.compile`

`torch.compile` is a JIT-style performance optimization API.

```python
model = MLP(10, 32, 2).to(device)
model = torch.compile(model)

x = torch.randn(8, 10, device=device)
out = model(x)
print(out.shape)
```

Practical notes:

- Great for many training and inference workloads
- Not every model gets a speedup
- Python features or data-dependent control flow may cause graph breaks
- Measure before and after

### 14.2 FX (`torch.fx`)

FX lets you capture and transform model graphs in Python.

```python
from torch.fx import symbolic_trace

model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
gm = symbolic_trace(model)

print(gm.graph)
```

FX is useful for:

- graph inspection
- program transforms
- tooling
- research/prototyping

### 14.3 `torch.export`

Use `torch.export` when you need a full, ahead-of-time captured graph suitable for downstream deployment pipelines.

```python
from torch.export import export

model = nn.Linear(4, 2).eval()
example = (torch.randn(3, 4),)

exported_program = export(model, example)
print(exported_program)
```

High-level difference:

- `torch.compile`: flexible JIT optimization, may graph-break and fall back to eager
- `torch.export`: aims for a full graph and errors out when code is not exportable

### 14.4 TorchScript status

TorchScript still exists in the docs, but current documentation explicitly marks it as deprecated and recommends `torch.export` for modern export workflows.

### 14.5 ONNX export

```python
model = nn.Linear(4, 2).eval()
sample = torch.randn(1, 4)

torch.onnx.export(
    model,
    (sample,),
    "linear.onnx",
    input_names=["x"],
    output_names=["y"],
    dynamo=True,
)
```

Use ONNX when you need interoperability with external runtimes.

### 14.6 Deployment summary

Common choices:

- **pure PyTorch inference**: easiest
- **`torch.compile`**: performance tuning inside PyTorch runtime
- **`torch.export`**: AOT graph capture for deployment pipelines
- **ONNX export**: portability to ONNX-compatible runtimes

---

## 15. `torch.func` and higher-order transforms

`torch.func` brings composable function transforms into PyTorch.

Very important transforms:

- `grad`
- `grad_and_value`
- `vmap`
- `vjp`
- `jvp`
- `jacrev`
- `jacfwd`
- `hessian`
- `functional_call`

### 15.1 Why `torch.func` matters

It is useful for:

- per-sample gradients
- Jacobians / Hessians
- meta-learning
- efficient batched differentiation
- functionalized model execution

### 15.2 `grad`

```python
from torch.func import grad

def f(x):
    return (x ** 2).sum()

g = grad(f)
x = torch.tensor([1.0, 2.0, 3.0])
print(g(x))   # tensor([2., 4., 6.])
```

### 15.3 `vmap`

```python
from torch.func import vmap

def f(x):
    return x ** 2 + 1

xs = torch.arange(5.0)
print(vmap(f)(xs))
```

### 15.4 `jacrev` and `jacfwd`

```python
from torch.func import jacrev, jacfwd

def f(x):
    return torch.stack([x[0] ** 2, x[0] * x[1]])

x = torch.tensor([2.0, 3.0])
print(jacrev(f)(x))
print(jacfwd(f)(x))
```

### 15.5 Functional call on modules

```python
from torch.func import functional_call, grad

model = nn.Linear(4, 1)
params = dict(model.named_parameters())

def loss_fn(params, x, y):
    pred = functional_call(model, params, (x,))
    return F.mse_loss(pred, y)

x = torch.randn(8, 4)
y = torch.randn(8, 1)

grads = grad(loss_fn)(params, x, y)
print(grads.keys())
```

This style is useful in meta-learning, differentiable optimization, and advanced transformations.

---

## 16. Distributed training and large-scale training

### 16.1 `torch.distributed`

PyTorch provides distributed communication primitives and backends such as:

- Gloo
- NCCL
- MPI (optional/source builds)
- platform-dependent availability

### 16.2 `DistributedDataParallel` (DDP)

DDP is the standard approach for multi-GPU data parallel training.

High-level idea:

- one process per GPU
- each process has its own model replica
- gradients are synchronized across processes during backward

Minimal sketch:

```python
import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup():
    dist.init_process_group(backend="nccl")
    local_rank = int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(local_rank)
    return local_rank

local_rank = setup()
model = MLP(10, 32, 2).to(local_rank)
model = DDP(model, device_ids=[local_rank])
```

### 16.3 `DistributedSampler`

When using DDP, the dataset is usually partitioned with `DistributedSampler`.

```python
from torch.utils.data.distributed import DistributedSampler

sampler = DistributedSampler(dataset, shuffle=True)
loader = DataLoader(dataset, batch_size=32, sampler=sampler)

for epoch in range(num_epochs):
    sampler.set_epoch(epoch)
```

### 16.4 FSDP

`FullyShardedDataParallel` (FSDP) shards parameters across workers and is important for large models.

Use it when:

- the model is too large for ordinary DDP memory usage
- you need parameter sharding

### 16.5 Distributed checkpointing (DCP)

`torch.distributed.checkpoint` is designed for distributed save/load workflows, including resharding between topologies.

---

## 17. Quantization

Quantization reduces model size and can improve inference speed on supported backends/workloads.

Main ideas:

- represent weights/activations with lower precision integers
- reduce compute/memory cost
- often trade off a little accuracy for speed/size

### 17.1 Dynamic quantization example

Dynamic quantization is common for linear-heavy CPU inference.

```python
from torch.ao.quantization import quantize_dynamic

model = nn.Sequential(
    nn.Linear(16, 32),
    nn.ReLU(),
    nn.Linear(32, 4),
).eval()

quantized_model = quantize_dynamic(
    model,
    {nn.Linear},
    dtype=torch.qint8,
)

x = torch.randn(8, 16)
print(quantized_model(x))
```

### 17.2 Broad quantization categories

- dynamic quantization
- post-training static quantization
- quantization-aware training (QAT)

In practice, quantization workflows can be backend- and model-dependent, so always benchmark accuracy and speed on the real target system.

---

## 18. Profiling, debugging, reproducibility, and testing

### 18.1 Profiling with `torch.profiler`

```python
from torch.profiler import profile, record_function, ProfilerActivity

model = MLP(10, 32, 2)

x = torch.randn(128, 10)

with profile(activities=[ProfilerActivity.CPU], record_shapes=True) as prof:
    with record_function("model_inference"):
        model(x)

print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))
```

Use the profiler to understand:

- expensive operators
- shapes
- stack traces
- CPU/GPU activity

### 18.2 Detecting autograd anomalies

```python
torch.autograd.set_detect_anomaly(True)

x = torch.tensor([0.0], requires_grad=True)
y = x / x
loss = y.sum()

try:
    loss.backward()
except RuntimeError as e:
    print("Autograd anomaly detected:", e)
```

This is for debugging, not for normal fast training.

### 18.3 Gradcheck

For custom differentiable ops, validate gradients numerically.

```python
from torch.autograd import gradcheck

class SquareFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x * x

    @staticmethod
    def backward(ctx, grad_output):
        (x,) = ctx.saved_tensors
        return grad_output * 2 * x

x = torch.randn(3, dtype=torch.double, requires_grad=True)
print(gradcheck(SquareFn.apply, (x,)))
```

### 18.4 Reproducibility

```python
import random
import numpy as np
import torch

seed = 42
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

torch.use_deterministic_algorithms(True)
```

Important warning:

Even with fixed seeds, fully identical results are **not guaranteed** across PyTorch releases, platforms, and CPU/GPU executions.

### 18.5 Debugging shapes

A lot of PyTorch debugging is shape debugging.

```python
x = torch.randn(32, 3, 224, 224)
print("input:", x.shape)

conv = nn.Conv2d(3, 16, kernel_size=3, padding=1)
y = conv(x)
print("after conv:", y.shape)
```

### 18.6 TensorBoard logging

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/demo")

for step in range(5):
    writer.add_scalar("loss/train", 1.0 / (step + 1), step)

writer.close()
```

### 18.7 CUDA memory debugging

For serious CUDA memory debugging, PyTorch also provides CUDA memory snapshots and related tooling.

---

## 19. Extending PyTorch

### 19.1 When to extend PyTorch

Extend PyTorch when:

- built-in ops are not enough
- you need a custom differentiable op
- you need a custom C++/CUDA kernel
- you want new operators to integrate with the PyTorch dispatcher

### 19.2 Custom Python autograd op

Already shown with `torch.autograd.Function`.

### 19.3 Custom operators

Modern custom ops can be registered with:

- Python `torch.library`
- C++ `TORCH_LIBRARY`

This matters when you want PyTorch-native operator integration.

### 19.4 C++ / CUDA extensions

PyTorch supports writing custom C++ and CUDA extensions for performance-critical paths.

This is an advanced topic but very important in production and systems work.

---

## 20. Common mistakes and best practices

### 20.1 Mistake: forgetting `model.eval()`

Bad:

```python
with torch.no_grad():
    logits = model(x)
```

Better for evaluation:

```python
model.eval()
with torch.no_grad():
    logits = model(x)
```

### 20.2 Mistake: applying `softmax` before `CrossEntropyLoss`

Bad:

```python
probs = torch.softmax(logits, dim=1)
loss = nn.CrossEntropyLoss()(probs, target)
```

Correct:

```python
loss = nn.CrossEntropyLoss()(logits, target)
```

### 20.3 Mistake: applying `sigmoid` before `BCEWithLogitsLoss`

Bad:

```python
probs = torch.sigmoid(logits)
loss = nn.BCEWithLogitsLoss()(probs, target)
```

Correct:

```python
loss = nn.BCEWithLogitsLoss()(logits, target)
```

### 20.4 Mistake: not zeroing gradients

Bad:

```python
for x, y in loader:
    loss = criterion(model(x), y)
    loss.backward()
    optimizer.step()
```

Correct:

```python
for x, y in loader:
    optimizer.zero_grad(set_to_none=True)
    loss = criterion(model(x), y)
    loss.backward()
    optimizer.step()
```

### 20.5 Mistake: device mismatch

Bad:

```python
model = model.to("cuda")
x = torch.randn(4, 10)   # CPU tensor
y = model(x)             # error
```

Correct:

```python
x = x.to("cuda")
y = model(x)
```

### 20.6 Mistake: unsafe reshaping assumptions

After `permute()`, `view()` may fail or behave unexpectedly if memory is not laid out compatibly.

Safer habit:

```python
x = x.permute(0, 2, 3, 1).reshape(x.size(0), -1)
```

### 20.7 Best practices summary

- prefer `state_dict()` for saving/loading
- use `model.train()` / `model.eval()` correctly
- use `zero_grad(set_to_none=True)`
- profile before optimizing
- use AMP on supported hardware
- test tensor shapes often
- start simple, then add complexity
- keep the training loop explicit and readable

---

## 21. End-to-end example

This is a compact but realistic classification example.

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# 1) Dataset
class ToyClassificationDataset(Dataset):
    def __init__(self, n=1000):
        self.x = torch.randn(n, 20)
        self.y = (self.x[:, :5].sum(dim=1) > 0).long()

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

# 2) Model
class Classifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(20, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
        )

    def forward(self, x):
        return self.net(x)

# 3) Setup
device = (
    torch.device("cuda") if torch.cuda.is_available()
    else torch.device("mps") if hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    else torch.device("cpu")
)

train_ds = ToyClassificationDataset(1000)
val_ds = ToyClassificationDataset(200)

train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=64)

model = Classifier().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

# 4) Training + evaluation
for epoch in range(10):
    model.train()
    train_loss = 0.0

    for x, y in train_loader:
        x, y = x.to(device), y.to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            preds = logits.argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)

    scheduler.step()

    print(
        f"Epoch {epoch+1:02d} | "
        f"train_loss={train_loss / len(train_loader):.4f} | "
        f"val_acc={correct / total:.4f}"
    )

# 5) Save weights
torch.save(model.state_dict(), "classifier_weights.pt")
```

What this example covers:

- dataset creation
- dataloader usage
- model definition with `nn.Module`
- optimizer and scheduler
- train/eval mode
- forward + loss + backward + step
- inference with `no_grad()`
- saving `state_dict()`

---

## 22. What to revise before interviews or exams

If you want strong PyTorch fundamentals, be sure you can explain and write from memory:

### Core essentials
- tensor creation, shape, dtype, device
- broadcasting
- indexing, reshape, permute
- `requires_grad`, `.backward()`, gradient accumulation
- `detach`, `no_grad`, `inference_mode`
- how `nn.Module` works
- parameters vs buffers
- `state_dict()`
- `model.train()` vs `model.eval()`
- `Dataset` and `DataLoader`
- canonical training loop
- `CrossEntropyLoss` and `BCEWithLogitsLoss`
- optimizers and schedulers
- saving/loading checkpoints

### Modern PyTorch essentials
- `torch.compile`
- `torch.export`
- TorchScript deprecation direction
- AMP (`autocast`, `GradScaler`)
- profiler basics
- DDP basics
- `torch.func` basics

### Production-minded essentials
- device placement
- memory and batch size tradeoffs
- reproducibility caveats
- shape debugging
- gradient clipping
- checkpointing best practices

---

## 23. Official references

These are the most useful official places to revisit:

- PyTorch docs home
- Get Started / installation page
- `torch` package reference
- tensor docs
- autograd mechanics
- `nn.Module`
- `torch.nn`
- `torch.optim`
- `torch.utils.data`
- AMP docs
- `torch.compile`
- `torch.export`
- `torch.func`
- `torch.distributed`
- FSDP docs
- distributed checkpoint docs
- quantization docs
- profiler docs
- serialization semantics
- reproducibility note
- ONNX export docs

---

## Final mental model

When revising PyTorch, keep this simple model in your head:

- **Tensor** = data
- **Autograd** = gradients
- **`nn.Module`** = model structure/state
- **Loss** = objective
- **Optimizer** = parameter update rule
- **DataLoader** = batching pipeline
- **Device + dtype** = execution context
- **`state_dict()`** = model state
- **`torch.compile` / `torch.export` / ONNX** = performance and deployment
- **DDP / FSDP** = scaling out

If you master those connections, the rest of PyTorch becomes much easier to navigate.
