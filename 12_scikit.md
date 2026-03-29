# Scikit-learn (Python) — Complete Revision Notes

> Version note: This guide is aligned to the **stable scikit-learn documentation (1.8.0)** at the time of writing.  
> Goal: cover the **important concepts, APIs, workflows, model families, evaluation methods, and pitfalls** you should know to revise scikit-learn well.

---

## 1) What scikit-learn is

**scikit-learn** is a general-purpose machine learning library for Python built around a **consistent estimator API**.

It is strongest for:

- classical machine learning on tabular data
- preprocessing and feature engineering
- model selection and evaluation
- pipelines and reproducible workflows
- clustering, dimensionality reduction, and other unsupervised methods

It is **not** the main library for:

- deep learning at modern scale
- reinforcement learning
- structured prediction / sequence modeling at depth

It includes a simple MLP, but scikit-learn is mainly for **classical ML**, not end-to-end deep learning systems.

---

## 2) The core design philosophy

The single most important scikit-learn concept is the **uniform API**.

Different algorithms mostly follow the same pattern:

1. **Instantiate** an object with hyperparameters.
2. **Fit** it on training data.
3. **Use** it to predict, transform, score, inspect, or visualize.

This makes algorithms interchangeable inside pipelines, cross-validation, and hyperparameter search.

Example pattern:

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(C=1.0, max_iter=1000)  # instantiate
model.fit(X_train, y_train)                       # learn from data
y_pred = model.predict(X_test)                    # infer on new data
score = model.score(X_test, y_test)               # quick default metric
```

---

## 3) The main object types

### 3.1 Estimator
An **estimator** is any object that learns from data using `fit(...)`.

```python
estimator.fit(X, y)   # supervised
estimator.fit(X)      # unsupervised
```

Examples:
- `LogisticRegression`
- `RandomForestClassifier`
- `StandardScaler`
- `PCA`
- `KMeans`

### 3.2 Predictor
A **predictor** can make predictions after fitting.

Common methods:

- `predict(X)`
- `predict_proba(X)` for class probabilities
- `decision_function(X)` for raw decision scores

Examples:
- classifiers
- regressors
- some unsupervised estimators with `fit_predict`

### 3.3 Transformer
A **transformer** changes the representation of data.

Common methods:

- `transform(X)`
- `fit_transform(X)`

Examples:
- `StandardScaler`
- `OneHotEncoder`
- `SimpleImputer`
- `PCA`
- `PolynomialFeatures`

### 3.4 Model
Some estimators expose a `score(...)` method, usually meaning “higher is better,” but the exact meaning depends on the estimator.

Examples:
- classifiers: accuracy by default
- regressors: \(R^2\) by default
- clustering models: estimator-dependent defaults or none

### 3.5 Meta-estimator
A **meta-estimator** wraps another estimator.

Examples:
- `Pipeline`
- `GridSearchCV`
- `RandomizedSearchCV`
- `OneVsRestClassifier`
- `BaggingClassifier`
- `VotingClassifier`
- `StackingRegressor`

This is one of the most important scikit-learn ideas: **composition**.

---

## 4) Hyperparameters vs learned parameters

### Hyperparameters
These are values you set **before training**.

Examples:
- `n_estimators`
- `max_depth`
- `C`
- `alpha`
- `n_neighbors`

They are passed to the constructor:

```python
RandomForestClassifier(n_estimators=300, max_depth=8)
```

### Learned parameters / fitted attributes
These are learned **during `fit`** and usually end with a trailing underscore `_`.

Examples:
- `coef_`
- `intercept_`
- `classes_`
- `feature_importances_`
- `cluster_centers_`
- `components_`

Important rule:

- `coef_` means “learned from data”
- `_coef` or names beginning with `_` are internal / private

---

## 5) Common estimator methods

### Core methods
- `fit(X, y=None)`
- `predict(X)`
- `transform(X)`
- `fit_transform(X, y=None)`
- `fit_predict(X, y=None)`
- `inverse_transform(X)`
- `score(X, y=None)`

### Model configuration / introspection
- `get_params()`
- `set_params(...)`

These are critical because:
- pipelines depend on them
- grid/random search depends on them
- cloning estimators depends on them

### Partial / incremental learning
Some estimators support:
- `partial_fit(...)`

This is used for:
- online learning
- mini-batch training
- out-of-core workflows

Common examples:
- `SGDClassifier`, `SGDRegressor`
- `PassiveAggressiveClassifier`
- `MiniBatchKMeans`
- some Naive Bayes estimators

### Decision outputs
For classifiers:
- use `predict_proba` when you need probabilities
- use `decision_function` when the algorithm exposes margins or raw scores
- thresholding these outputs is a separate decision from model fitting

---

## 6) Data conventions

### 6.1 X and y
- `X`: input features
- `y`: target / label

Typical shapes:
- `X`: `(n_samples, n_features)`
- `y`: `(n_samples,)`

For multioutput problems:
- `y`: `(n_samples, n_outputs)`

### 6.2 Supported input types
scikit-learn commonly accepts:
- NumPy arrays
- SciPy sparse matrices
- pandas DataFrames / Series
- sometimes polars DataFrames
- Python lists that convert cleanly to arrays

Internally, many estimators convert data into NumPy arrays or sparse matrices.

### 6.3 Tabular-data attributes
Fitted tabular estimators commonly expose:
- `n_features_in_`
- `feature_names_in_` (when trained with named columns)

These are extremely useful for debugging pipelines and feature-name tracking.

### 6.4 Dense vs sparse
Some estimators work well with sparse matrices, some do not.

Sparse is common for:
- one-hot encoded categorical data
- bag-of-words / TF-IDF text features

### 6.5 Missing values
scikit-learn does **not** assume every estimator can handle `NaN` directly.

Typical choices:
- impute values first
- use an estimator that explicitly supports missing values

Always check the estimator’s docs.

---

## 7) The standard machine learning workflow in scikit-learn

A high-quality scikit-learn workflow usually looks like this:

1. Load data
2. Split train/test
3. Build preprocessing
4. Build model
5. Put preprocessing + model in a pipeline
6. Cross-validate
7. Tune hyperparameters
8. Refit on training data
9. Evaluate once on held-out test data
10. Persist / deploy

Canonical pattern:

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000))
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
```

The **pipeline** is the safest default.

---

## 8) Train/test split and leakage

### `train_test_split`
The default helper for creating hold-out sets.

Key parameters:
- `test_size`
- `train_size`
- `random_state`
- `shuffle`
- `stratify`

Use `stratify=y` for classification when class balance matters.

### Data leakage
One of the biggest scikit-learn mistakes.

Leakage happens when information from test/validation data influences training.

Common leakage examples:
- fitting a scaler on full data before splitting
- imputing on full data before splitting
- feature selection on full data before splitting
- target-aware preprocessing outside CV folds

Correct fix:
- place preprocessing inside a `Pipeline`
- do CV on the entire pipeline, not on already-transformed full data

---

## 9) Cross-validation (CV)

CV estimates generalization performance more reliably than a single split.

### Core tools
- `cross_val_score`
- `cross_validate`
- `cross_val_predict`
- `validation_curve`
- `learning_curve`

### Common splitters
- `KFold`
- `StratifiedKFold`
- `GroupKFold`
- `ShuffleSplit`
- `StratifiedShuffleSplit`
- `RepeatedKFold`
- `RepeatedStratifiedKFold`
- `LeaveOneOut`
- `PredefinedSplit`
- `TimeSeriesSplit`

### When to use which
- **Classification**: usually `StratifiedKFold`
- **Regression**: usually `KFold`
- **Grouped data**: `GroupKFold` or related grouped splitters
- **Time series**: `TimeSeriesSplit`
- **Small data / expensive models**: fewer folds may be practical

### Important CV principles
- Preprocessing must happen **inside** each fold
- Feature selection must happen **inside** each fold
- Hyperparameter tuning must happen **inside** CV, not after seeing test results
- Keep the final test set untouched until the very end

### Nested CV
Use nested CV when you want less biased performance estimation while also tuning hyperparameters.

Outer loop:
- performance estimation

Inner loop:
- hyperparameter tuning

---

## 10) Scoring and metrics

scikit-learn separates:
- **estimators**
- **metrics**
- **scorers**

### 10.1 Metrics vs score
- `estimator.score(...)` = estimator’s default quick metric
- `sklearn.metrics.*` = explicit evaluation functions
- `scoring=` = scorer name or custom scorer used in CV/search

### 10.2 Classification metrics
Important ones:
- `accuracy_score`
- `balanced_accuracy_score`
- `precision_score`
- `recall_score`
- `f1_score`
- `fbeta_score`
- `roc_auc_score`
- `average_precision_score`
- `log_loss`
- `matthews_corrcoef`
- `confusion_matrix`
- `classification_report`

Key concepts:
- **precision**: of predicted positives, how many are correct
- **recall**: of true positives, how many are found
- **F1**: harmonic mean of precision and recall
- **ROC AUC**: ranking ability across thresholds
- **PR AUC / average precision**: often better under heavy class imbalance
- **balanced accuracy**: useful for imbalanced classes
- **log loss**: evaluates calibrated probabilistic predictions

### 10.3 Regression metrics
Important ones:
- `mean_squared_error`
- `root_mean_squared_error`
- `mean_absolute_error`
- `median_absolute_error`
- `mean_absolute_percentage_error`
- `r2_score`
- `explained_variance_score`

Key concepts:
- **MSE / RMSE** punish large errors more
- **MAE** is more robust to outliers than MSE
- **\(R^2\)** compares against predicting the mean; it can be negative

### 10.4 Clustering metrics
Important ones:
- `silhouette_score`
- `adjusted_rand_score`
- `normalized_mutual_info_score`
- `homogeneity_score`
- `completeness_score`
- `v_measure_score`

Use:
- **internal metrics** when no true labels exist
- **external metrics** when ground-truth labels exist

### 10.5 Averaging for multiclass / multilabel
Metrics such as precision, recall, and F1 can use:
- `binary`
- `micro`
- `macro`
- `weighted`
- `samples` (multilabel)

Know these well:
- **macro** = treat classes equally
- **weighted** = weight by support
- **micro** = aggregate over individual decisions

### 10.6 Dummy baselines
Always compare against:
- `DummyClassifier`
- `DummyRegressor`

A sophisticated model that barely beats a dummy baseline may not be useful.

### 10.7 Negative scorers
In search/CV, some losses are exposed as **negative** scorers, such as:
- `neg_mean_squared_error`

Reason:
- scikit-learn’s scorer interface follows “higher is better”

---

## 11) Threshold tuning vs probability estimation

For classification, predicting a label is often:

```python
score_or_prob = model.predict_proba(X)[:, 1]
label = score_or_prob >= threshold
```

The threshold is **not** always 0.5.

You should tune thresholds when:
- false positives and false negatives have different costs
- precision matters more than recall
- recall matters more than precision
- the operating point matters more than raw ranking quality

Important distinction:
- **Model training** learns scores/probabilities
- **Threshold tuning** decides how to convert those into class labels

---

## 12) Probability calibration

Some classifiers produce poorly calibrated probabilities.

Calibration tools:
- `CalibratedClassifierCV`
- calibration curves / reliability diagrams

Use calibration when:
- probabilities themselves matter
- downstream decisions depend on probability quality
- you need trustworthy risk estimates

Common examples needing calibration:
- SVMs
- tree ensembles in some settings
- boosted models in some settings

---

## 13) Pipelines and composite estimators

This is one of the most important sections in all of scikit-learn.

### 13.1 `Pipeline`
Chains preprocessing steps followed by a final estimator.

```python
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression())
])
```

Benefits:
- avoids leakage
- keeps workflow reproducible
- works naturally with CV/search
- makes deployment easier

Parameter access uses `step__param`:

```python
pipe.set_params(clf__C=0.5)
```

### 13.2 `make_pipeline`
Convenience helper that auto-generates step names.

### 13.3 `ColumnTransformer`
Applies different preprocessing to different columns.

This is the standard solution for mixed tabular data:
- numeric columns → impute + scale
- categorical columns → impute + one-hot encode

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

numeric_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocess = ColumnTransformer([
    ("num", numeric_pipe, numeric_cols),
    ("cat", categorical_pipe, categorical_cols),
])
```

### 13.4 `FeatureUnion`
Combines features from multiple transformers in parallel.

Useful when several feature representations should be concatenated.

### 13.5 `TransformedTargetRegressor`
Transforms `y` in regression.

Common examples:
- log-transform target
- inverse-transform predictions back to original scale

### 13.6 Visualizing composite estimators
Pipelines and composite estimators can be displayed richly in notebooks, which is useful for debugging and teaching.

### 13.7 `set_output`
Transformers can be configured to output:
- default array-like output
- pandas DataFrames
- in newer workflows, sometimes polars output depending on support

This is useful for preserving feature names after transformation.

---

## 14) Preprocessing fundamentals

Preprocessing is not an add-on in scikit-learn. It is central.

### 14.1 Scaling / standardization
Common tools:
- `StandardScaler`
- `MinMaxScaler`
- `MaxAbsScaler`
- `RobustScaler`

When to scale:
- linear models with regularization
- SVMs
- k-nearest neighbors
- neural networks
- PCA
- distance-based or gradient-based methods

When scaling matters less:
- tree-based models are usually much less sensitive

#### Quick guide
- `StandardScaler`: mean 0, variance 1; default general-purpose scaler
- `MinMaxScaler`: maps to a range, often `[0, 1]`
- `MaxAbsScaler`: convenient for sparse data
- `RobustScaler`: more robust to outliers

### 14.2 Normalization
Tool:
- `Normalizer`

This scales **rows / samples**, not columns.

Common use:
- text vectors
- cosine-similarity workflows

Do not confuse:
- **standardization** = feature-wise scaling
- **normalization** = sample-wise norm scaling

### 14.3 Nonlinear transforms
Tools:
- `PowerTransformer`
- `QuantileTransformer`

Use these to make distributions more Gaussian-like or more uniform, reduce skew, and sometimes stabilize variance.

### 14.4 Categorical encoding
Important tools:
- `OneHotEncoder`
- `OrdinalEncoder`
- target handling tools such as `LabelEncoder` for `y`, not for `X`

#### Best practice
- for nominal / unordered categories: usually `OneHotEncoder`
- for truly ordered categories: sometimes `OrdinalEncoder`
- avoid feeding arbitrary integer labels for unordered categories into linear/distance models

Important parameter:
- `handle_unknown="ignore"` in `OneHotEncoder` for production safety

### 14.5 Native categorical support
Some estimators have limited native categorical support in specific cases, but the general scikit-learn mindset is still:
- preprocess categorical variables explicitly
- use `ColumnTransformer` + encoder by default

### 14.6 Discretization / binning
Tool:
- `KBinsDiscretizer`

Converts continuous values to bins. Useful in some linear or rule-like models.

### 14.7 Polynomial / interaction features
Tool:
- `PolynomialFeatures`

Used to expand linear models with nonlinear basis functions.

Important:
- feature count can explode quickly
- combine with regularization

### 14.8 Custom transforms
Tools:
- `FunctionTransformer`
- custom transformer classes implementing `fit` / `transform`

Useful for domain-specific feature engineering.

---

## 15) Imputation and missing values

Important imputers:
- `SimpleImputer`
- `KNNImputer`
- `IterativeImputer` (multivariate / more advanced)

### 15.1 `SimpleImputer`
Strategies:
- `mean`
- `median`
- `most_frequent`
- `constant`

Use as the safe default.

### 15.2 `KNNImputer`
Uses neighboring samples to impute missing values.

Useful when local similarity matters.

### 15.3 `IterativeImputer`
Models each feature with missing values as a function of the others.

More expressive, but slower and more assumption-heavy.

### 15.4 Missing indicators
You can mark which values were imputed using missing-indicator style features. This can help models learn whether missingness itself is informative.

### 15.5 Estimators that handle `NaN`
Some estimators can handle missing values natively, but not all. Never assume this globally.

Rule:
- if unsure, impute in a pipeline

---

## 16) Feature extraction

Feature extraction converts raw data into numerical features.

This is different from **feature selection**.

### 16.1 Dict / mapping features
- `DictVectorizer`
- `FeatureHasher`

Useful for dictionary-like input records.

### 16.2 Text feature extraction
Core tools:
- `CountVectorizer`
- `TfidfVectorizer`
- `HashingVectorizer`
- `TfidfTransformer`

Important text concepts:
- tokenization
- stop words
- n-grams
- vocabulary
- document-term matrix
- sparse representation
- term frequency
- inverse document frequency (TF-IDF)

Typical text pipeline:

```python
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

text_clf = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("clf", LogisticRegression(max_iter=1000))
])
```

### 16.3 Image feature extraction
scikit-learn includes some image-oriented feature extraction utilities, but it is not a modern deep computer vision framework.

---

## 17) Dimensionality reduction and decomposition

### 17.1 PCA
- `PCA`

Core concept:
- project data into orthogonal directions of maximal variance

Uses:
- compression
- denoising
- visualization
- collinearity reduction
- preprocessing before another model

Important notes:
- PCA centers data
- PCA does **not** automatically scale features
- scale first if feature units differ substantially

### 17.2 `TruncatedSVD`
Good for sparse high-dimensional data, especially text.

Common use:
- latent semantic analysis (LSA)

### 17.3 `KernelPCA`
Nonlinear extension of PCA.

### 17.4 `IncrementalPCA`
For larger / chunked settings.

### 17.5 NMF
- `NMF`

Nonnegative matrix factorization:
- parts-based representation
- often useful for topic-like or count-like nonnegative data

### 17.6 ICA
- `FastICA`

Independent Component Analysis:
- seeks statistically independent components

### 17.7 Factor Analysis
Probabilistic latent-factor model.

### 17.8 Dictionary learning
Sparse coding / learned basis vectors.

### 17.9 Latent Dirichlet Allocation
- `LatentDirichletAllocation`

Topic modeling for count-like text data.

---

## 18) Random projection and kernel approximation

### Random projection
Tools:
- `GaussianRandomProjection`
- `SparseRandomProjection`

Use when:
- dimensionality is huge
- approximate distance preservation is acceptable
- you need a cheap projection

### Kernel approximation
Tools:
- `Nystroem`
- `RBFSampler`
- additive/skewed chi-squared approximations
- tensor-sketch polynomial approximation

Use when:
- you want kernel-like behavior with linear-time models
- exact kernel methods are too slow

---

## 19) Pairwise metrics, affinities, and kernels

scikit-learn contains pairwise similarity / distance tools.

Important concepts:
- cosine similarity
- Euclidean distance
- Manhattan distance
- kernels: linear, polynomial, sigmoid, RBF, Laplacian, chi-squared

These matter for:
- nearest neighbors
- clustering
- SVMs
- manifold learning
- some feature construction workflows

---

## 20) Target transformation tools

These transform the **target** rather than features.

Important ones:
- `LabelEncoder` for encoding class labels in `y`
- `LabelBinarizer`
- `MultiLabelBinarizer`
- `TransformedTargetRegressor` for numeric `y` transformations

Important warning:
- `LabelEncoder` is for **target labels**, not general feature columns in `X`

---

## 21) Linear models

This is a huge scikit-learn family.

### 21.1 Ordinary Least Squares
- `LinearRegression`

Use for standard linear regression.

### 21.2 Ridge
- `Ridge`
- `RidgeCV`
- `RidgeClassifier`

Adds L2 regularization.

Good when:
- many correlated features
- you want shrinkage but usually not exact sparsity

### 21.3 Lasso
- `Lasso`
- `LassoCV`

Adds L1 regularization.

Good when:
- you want sparse coefficients / implicit feature selection

### 21.4 Elastic Net
- `ElasticNet`
- `ElasticNetCV`

Mixes L1 and L2.

Often more stable than pure Lasso under correlated features.

### 21.5 Multi-task variants
For multioutput regression with shared sparsity structure:
- `MultiTaskLasso`
- `MultiTaskElasticNet`

### 21.6 Least Angle Regression family
- `Lars`
- `LassoLars`
- related information-criterion / CV variants

Specialized algorithms mainly relevant for sparse linear modeling theory and some high-dimensional settings.

### 21.7 Orthogonal Matching Pursuit
- `OrthogonalMatchingPursuit`

Greedy sparse approximation.

### 21.8 Bayesian regression
- `BayesianRidge`
- `ARDRegression`

Probabilistic linear regression with priors.

### 21.9 Logistic regression
- `LogisticRegression`
- `LogisticRegressionCV`

The workhorse linear classifier.

Important notes:
- despite the name, it is for **classification**
- supports binary and multiclass settings
- often a top baseline for tabular and text classification
- scaling usually helps
- regularization matters

### 21.10 Generalized Linear Models
Examples:
- Poisson-style or Gamma-style target modeling in specialized settings

Use when the response distribution is not well modeled by ordinary least squares assumptions.

### 21.11 SGD-based linear models
- `SGDClassifier`
- `SGDRegressor`

Important when:
- data is large
- sparse
- streaming
- online / partial-fit learning is needed

### 21.12 Robust regression
Examples:
- `HuberRegressor`
- `RANSACRegressor`
- `TheilSenRegressor`

Use when outliers matter.

### 21.13 Quantile regression
Estimates conditional quantiles instead of the conditional mean.

Useful for:
- asymmetric error costs
- prediction intervals / quantile forecasting ideas

### 21.14 Polynomial regression
Usually done by:
- `PolynomialFeatures` + linear model

Important concept:
- still linear in parameters after basis expansion

### 21.15 Important linear-model ideas
- coefficients are easiest to interpret after sensible preprocessing
- regularization changes coefficient magnitude
- correlated features complicate interpretation
- “important coefficient” is not the same as causal effect
- scale-sensitive models must be compared only after proper scaling

---

## 22) Discriminant analysis

### Models
- `LinearDiscriminantAnalysis` (LDA)
- `QuadraticDiscriminantAnalysis` (QDA)

### Core idea
Model class-conditional distributions and derive decision boundaries.

Differences:
- **LDA**: shared covariance across classes → linear boundaries
- **QDA**: separate covariance per class → quadratic boundaries

LDA can also be used for **dimensionality reduction**.

---

## 23) Support Vector Machines (SVM)

### Main estimators
- `SVC`
- `LinearSVC`
- `SVR`
- `LinearSVR`
- `NuSVC`
- `NuSVR`
- `OneClassSVM`

### Core concepts
- maximum-margin classification / regression
- support vectors
- kernels
- regularization parameter `C`
- kernel-specific parameters such as `gamma`

### When SVMs are strong
- medium-sized datasets
- high-dimensional data
- text data (especially linear SVM)
- complex boundaries with kernels

### Important practical notes
- scaling is usually essential
- kernel SVMs can be slow on large datasets
- `LinearSVC` and SGD-based linear models scale better
- `probability=True` in `SVC` adds extra work for probability estimation

### One-class SVM
Used for novelty / anomaly style settings.

---

## 24) Nearest Neighbors

### Main estimators
- `KNeighborsClassifier`
- `KNeighborsRegressor`
- `NearestNeighbors`
- `RadiusNeighborsClassifier`
- `RadiusNeighborsRegressor`
- `NearestCentroid`

### Core concept
Prediction depends on nearby samples under a chosen distance metric.

### Important parameters
- `n_neighbors`
- `weights`
- `metric`
- algorithm choice: brute / KD-tree / Ball-tree (automatic choice often fine)

### Practical notes
- scaling is extremely important
- prediction can be slower than training
- performance can degrade in very high dimensions

### Related concept
- `NeighborhoodComponentsAnalysis` learns a supervised distance metric / projection

---

## 25) Gaussian Processes

### Main estimators
- `GaussianProcessRegressor`
- `GaussianProcessClassifier`

### Core concept
A probabilistic, kernel-based nonparametric Bayesian method.

Good for:
- uncertainty-aware small/medium problems
- flexible function modeling

Trade-off:
- powerful but often computationally expensive

---

## 26) Cross decomposition

Important estimators:
- `PLSRegression`
- `PLSCanonical`
- `PLSSVD`
- `CCA`

These methods connect two data blocks or seek latent directions maximizing covariance/correlation.

Most relevant in chemometrics and multiview / multiblock settings.

---

## 27) Naive Bayes

### Main estimators
- `GaussianNB`
- `MultinomialNB`
- `ComplementNB`
- `BernoulliNB`
- `CategoricalNB`

### Core concept
Assume conditional independence of features given the class.

### When they work well
- text classification
- count-like features
- quick baselines
- small-data settings

### Which one when
- `GaussianNB`: continuous features
- `MultinomialNB`: counts / frequencies
- `ComplementNB`: often better on imbalanced text
- `BernoulliNB`: binary features
- `CategoricalNB`: integer-coded categorical features

### Out-of-core
Some Naive Bayes estimators support incremental training patterns.

---

## 28) Decision Trees

### Main estimators
- `DecisionTreeClassifier`
- `DecisionTreeRegressor`

### Core ideas
- recursive partitioning
- axis-aligned splits
- interpretable rules
- nonparametric modeling
- piecewise-constant predictions

### Important parameters
- `max_depth`
- `min_samples_split`
- `min_samples_leaf`
- `max_leaf_nodes`
- `criterion`
- `ccp_alpha` (cost-complexity pruning)

### Strengths
- nonlinear boundaries
- little need for feature scaling
- handles mixed feature effects well
- interpretable at small depth

### Weaknesses
- unstable
- prone to overfitting
- often lower predictive performance than ensembles

### Important concepts
- impurity criteria (`gini`, `entropy` / `log_loss`, squared error variants)
- pruning
- feature importance from impurity reduction
- missing-value support depends on estimator/version/setting; always verify docs

---

## 29) Ensembles

Ensembles combine multiple models to improve performance, stability, or calibration.

### 29.1 Random forests and related randomized trees
Main estimators:
- `RandomForestClassifier`
- `RandomForestRegressor`
- `ExtraTreesClassifier`
- `ExtraTreesRegressor`

Core idea:
- many randomized trees
- average or vote their outputs

Strengths:
- strong tabular baseline
- little scaling needed
- handles nonlinearities and interactions well

Weaknesses:
- can be large
- feature importance can be misleading under correlation
- less interpretable than a single tree

### 29.2 Gradient boosting
Important estimators:
- `GradientBoostingClassifier`
- `GradientBoostingRegressor`
- `HistGradientBoostingClassifier`
- `HistGradientBoostingRegressor`

Core idea:
- build weak learners sequentially to correct residual errors

Important concepts:
- learning rate
- number of estimators / iterations
- tree depth / leaf constraints
- early stopping
- regularization
- histogram-based boosting for speed and scale

`HistGradientBoosting*` is often the more modern default inside scikit-learn for large tabular data.

### 29.3 Bagging
- `BaggingClassifier`
- `BaggingRegressor`

Fits many base estimators on bootstrap samples and aggregates them.

### 29.4 Voting
- `VotingClassifier`
- `VotingRegressor`

Combines several already-trained estimators by:
- hard voting
- soft voting
- averaging

### 29.5 Stacking
- `StackingClassifier`
- `StackingRegressor`

Learns a meta-model over base-model predictions.

### 29.6 AdaBoost
- `AdaBoostClassifier`
- `AdaBoostRegressor`

Sequentially focuses on hard examples / errors.

### 29.7 Ensemble feature importance caveat
Tree-based importance from impurity decrease can be biased:
- toward high-cardinality features
- by correlated features

Safer inspection options:
- permutation importance
- partial dependence / ICE
- domain reasoning

---

## 30) Multiclass, multilabel, and multioutput

These are easy to mix up.

### 30.1 Multiclass classification
One target, more than two classes.

scikit-learn handles this in many estimators automatically.

Meta-estimators:
- `OneVsRestClassifier`
- `OneVsOneClassifier`
- `OutputCodeClassifier`

### 30.2 Multilabel classification
Each sample can belong to multiple classes simultaneously.

Tools:
- `MultiLabelBinarizer`
- multilabel-aware metrics
- `OneVsRestClassifier` is common

### 30.3 Multioutput regression
Several numeric targets per sample.

### 30.4 Multiclass-multioutput classification
Multiple classification targets at once.

Wrappers:
- `MultiOutputClassifier`
- `MultiOutputRegressor`
- `ClassifierChain`
- `RegressorChain`

---

## 31) Feature selection

Feature selection chooses among already-constructed features.

This differs from feature extraction.

### Main approaches

#### 31.1 Filter methods
Examples:
- `VarianceThreshold`
- univariate tests (`SelectKBest`, `SelectPercentile`, etc.)

Use fast statistical criteria independent of a downstream model.

#### 31.2 Wrapper methods
Examples:
- `RFE`
- `RFECV`
- `SequentialFeatureSelector`

Use repeated model fitting to evaluate subsets.

#### 31.3 Embedded methods
Examples:
- `SelectFromModel`
- L1 models
- tree-based importances

Selection is part of fitting the model itself.

### Key rule
Feature selection must be inside the pipeline / CV loop to avoid leakage.

---

## 32) Semi-supervised learning

Important estimators:
- `SelfTrainingClassifier`
- label propagation / label spreading family

Use when:
- you have a small labeled set plus more unlabeled data

Needs careful validation. Semi-supervised learning is not automatically beneficial.

---

## 33) Isotonic regression

- `IsotonicRegression`

Fits a monotonic nonparametric function.

Common use:
- calibration
- monotonic relationships without assuming linearity

---

## 34) Neural networks in scikit-learn

### Main estimators
- `MLPClassifier`
- `MLPRegressor`
- unsupervised: Bernoulli RBM (`BernoulliRBM`)

### Core concepts for MLP
- feed-forward multilayer perceptron
- hidden layers
- activation functions
- optimization by gradient-based training
- regularization
- warm starts

### Practical reality
scikit-learn’s neural-network support is useful for learning and some moderate tasks, but it is **not** a replacement for modern deep-learning frameworks.

---

## 35) Clustering

Unsupervised grouping of samples.

### Main algorithms

#### 35.1 K-means
- `KMeans`
- `MiniBatchKMeans`

Best for:
- roughly spherical clusters
- large numeric datasets (`MiniBatchKMeans` for scale)

Important concepts:
- centroids
- inertia
- initialization
- local minima
- `n_clusters`

#### 35.2 Affinity Propagation
No need to pre-specify number of clusters, but can be expensive/sensitive.

#### 35.3 Mean Shift
Mode-seeking clustering; bandwidth matters.

#### 35.4 Spectral clustering
Graph / affinity-based method for nonconvex shapes.

#### 35.5 Hierarchical clustering
- `AgglomerativeClustering`
- dendrogram concepts

Useful for nested cluster structure.

#### 35.6 Density-based clustering
- `DBSCAN`
- `HDBSCAN`
- `OPTICS`

Good for:
- arbitrary shapes
- noise handling
- outlier-aware grouping

Important concepts:
- neighborhood radius / density thresholds
- core points, border points, noise

#### 35.7 BIRCH
Efficient for large datasets / incremental clustering ideas.

### Clustering evaluation
If labels are unavailable:
- silhouette and related internal criteria

If labels exist:
- adjusted Rand index, NMI, etc.

Important warning:
cluster labels are arbitrary integers; label “0” and label “1” have no semantic rank.

---

## 36) Gaussian mixture models

Important estimators:
- `GaussianMixture`
- `BayesianGaussianMixture`

Core idea:
- probabilistic clustering via mixtures of Gaussians

Compared with K-means:
- soft assignments
- covariance structure
- probabilistic density interpretation

Use when cluster covariance matters and hard spherical assumptions are too restrictive.

---

## 37) Manifold learning

Important methods:
- `Isomap`
- `LocallyLinearEmbedding`
- `SpectralEmbedding`
- `MDS`
- `TSNE`

Main use:
- visualization or nonlinear embedding

Important caution:
many manifold methods are primarily for **exploration / visualization**, not for stable downstream predictive pipelines.

### t-SNE
Use mainly for visualization.

Important cautions:
- not a clustering algorithm
- axes have no direct meaning
- distances can be visually misleading
- perplexity and random state matter

---

## 38) Biclustering

Biclustering simultaneously clusters:
- rows
- columns

Important estimators:
- `SpectralCoclustering`
- `SpectralBiclustering`

Useful when submatrices or co-structured row/column groups matter.

---

## 39) Covariance estimation

Important estimators / concepts:
- empirical covariance
- shrunk covariance
- sparse inverse covariance
- robust covariance

Use cases:
- anomaly detection
- Gaussian assumptions
- covariance matrix stabilization in high dimensions

---

## 40) Novelty detection and outlier detection

These are related but different.

### Outlier detection
Training data may already contain outliers.

### Novelty detection
Train on mostly clean “normal” data, then detect new abnormal samples.

Important estimators:
- `IsolationForest`
- `LocalOutlierFactor`
- `OneClassSVM`
- covariance-based methods such as `EllipticEnvelope`

Important caution:
- method behavior depends strongly on contamination assumptions and scaling
- novelty vs outlier settings can differ, especially for LOF

---

## 41) Density estimation

Important tools:
- histograms
- `KernelDensity`

Use when you want to estimate a probability density rather than only classify/regress.

---

## 42) Inspection and interpretability

scikit-learn provides **inspection** tools, not magic explanations.

### 42.1 Permutation importance
- `permutation_importance`

Main idea:
shuffle one feature, observe score drop.

Advantages:
- model-agnostic
- often more trustworthy than impurity-based tree importance

Limitations:
- slower
- can be misleading with strongly correlated features

### 42.2 Partial dependence
Tools:
- partial dependence plots
- `PartialDependenceDisplay`

Shows average effect of a feature on model predictions.

### 42.3 ICE plots
Individual Conditional Expectation plots show per-sample response curves instead of only the average.

### 42.4 Coefficients and feature importances
Interpret carefully:
- coefficients depend on feature scaling and collinearity
- tree importances can be biased
- association is not causation

---

## 43) Visualizations and display objects

scikit-learn uses **display objects** for plotting.

Important displays include:
- `ConfusionMatrixDisplay`
- `RocCurveDisplay`
- `PrecisionRecallDisplay`
- `DetCurveDisplay`
- `CalibrationDisplay`
- `DecisionBoundaryDisplay`
- `PartialDependenceDisplay`
- estimator / pipeline HTML displays in notebooks

Preferred creation style:
- `from_estimator(...)`
- `from_predictions(...)`

These integrate cleanly with fitted estimators and predictions.

---

## 44) Dataset utilities

### Built-in datasets
Toy datasets:
- iris
- digits
- diabetes
- wine
- breast cancer
- linnerud

Real-world datasets:
- 20 newsgroups
- California housing
- Olivetti faces
- LFW
- forest covertypes
- RCV1
- others in docs

Generated data:
- `make_classification`
- `make_regression`
- `make_blobs`
- `make_moons`
- `make_circles`
- manifold/decomposition generators

Other loaders:
- OpenML
- svmlight/libsvm format
- sample images

Important object:
- many dataset loaders return a **Bunch**, which behaves like a dict with attribute-style access

---

## 45) Choosing the right estimator

scikit-learn has an official “choose the right estimator” guide.

Practical starting defaults:

### Classification
- baseline: `DummyClassifier`
- linear/text: `LogisticRegression`, `LinearSVC`, `SGDClassifier`
- mixed tabular: `RandomForestClassifier`, `HistGradientBoostingClassifier`
- small nonlinear problems: `SVC`
- probability-sensitive tasks: calibrated logistic / calibrated tree models as needed

### Regression
- baseline: `DummyRegressor`
- linear relationships: `LinearRegression`, `Ridge`, `Lasso`, `ElasticNet`
- robust / nonlinear tabular: `RandomForestRegressor`, `HistGradientBoostingRegressor`
- small nonlinear problems: `SVR`
- sparse / large-scale: `SGDRegressor`

### Clustering
- centroid-style: `KMeans`
- arbitrary shapes + noise: `DBSCAN` / `HDBSCAN` / `OPTICS`
- hierarchy wanted: agglomerative clustering
- probabilistic clusters: Gaussian mixtures

### Dimensionality reduction
- dense continuous data: `PCA`
- sparse text: `TruncatedSVD`
- visualization: manifold methods such as t-SNE with caution

---

## 46) Model selection / hyperparameter tuning

### 46.1 Grid search
- `GridSearchCV`

Exhaustively evaluates parameter combinations.

Best when:
- search space is small / structured

### 46.2 Randomized search
- `RandomizedSearchCV`

Samples parameter combinations.

Best when:
- search space is large
- only a few parameters matter strongly
- you need a better compute/performance tradeoff

### 46.3 Successive halving
Important idea:
- allocate less budget to poor candidates early
- more budget to promising candidates later

Useful for resource-aware search.

### 46.4 Search best practices
- tune the whole pipeline
- choose metrics aligned to business/scientific objective
- use sensible ranges, often log-spaced for scale parameters
- avoid giant blind grids
- keep a final untouched test set
- inspect variance, not only the best mean score
- remember the winning config may overfit the validation process if search is excessive

### 46.5 Parameter naming in pipelines
Use double underscore:

```python
param_grid = {
    "preprocess__num__imputer__strategy": ["mean", "median"],
    "model__C": [0.1, 1, 10]
}
```

---

## 47) Learning curves and validation curves

### Learning curve
Shows score as training size increases.

Useful for diagnosing:
- high bias
- high variance
- whether more data may help

### Validation curve
Shows score as one hyperparameter changes.

Useful for:
- understanding regularization
- identifying underfit vs overfit regions

---

## 48) Class imbalance

Important scikit-learn concept even though not a separate top-level chapter.

Common strategies:
- stratified splitting
- appropriate metrics (`balanced_accuracy`, F1, PR AUC, ROC AUC depending on objective)
- class weighting (`class_weight="balanced"` in many estimators)
- threshold tuning
- resampling with external libraries if needed (for example imbalanced-learn)

Never judge imbalanced classifiers by accuracy alone.

---

## 49) Randomness and reproducibility

Very important in scikit-learn.

### `random_state`
Controls randomness in:
- train/test splitting
- CV shuffling
- randomized estimators
- some optimization procedures

### Practical rules
- set `random_state` when you want reproducible experiments
- keep it fixed across comparable runs
- understand that repeated `fit` without fixed randomness may change results
- randomness can enter both the model and the data split

---

## 50) Computing, performance, and scale

### 50.1 `n_jobs`
Many estimators/utilities support parallelism through `n_jobs`.

Common meaning:
- `n_jobs=-1` → use all available cores

But actual behavior depends on the estimator and underlying libraries.

### 50.2 Out-of-core learning
For data too large for memory, the classic scikit-learn pattern is:

1. stream mini-batches
2. extract features incrementally if possible
3. use an estimator with `partial_fit`

### 50.3 Sparse data
Especially important for text workflows.

### 50.4 Latency vs throughput
Production settings may optimize for:
- single-sample latency
- batch throughput

These are different goals.

### 50.5 Scale-aware model choices
- huge linear sparse problem → SGD / linear models
- huge kernel problem → approximate kernels or linear alternatives
- huge clustering → minibatch variants
- large tabular boosting → histogram-based boosting

---

## 51) Metadata routing (experimental)

This is more advanced, but important to know conceptually.

Metadata means extra information passed alongside `X` and `y`, such as:
- `sample_weight`
- `groups`
- `classes` in some incremental settings

Metadata routing allows meta-estimators and utilities to correctly pass such metadata to the components that request it.

Important points:
- it is **experimental**
- not all estimators support it
- it matters mostly in advanced compositions and custom estimator development

---

## 52) Array API / limited GPU-related support (experimental)

scikit-learn now has **experimental Array API support** for some estimators.

Conceptually:
- some compatible estimators can operate on Array-API-compatible inputs
- this can enable execution on non-NumPy array backends such as certain GPU-backed arrays in supported workflows

Important cautions:
- support is limited, not universal
- scikit-learn is still not primarily a GPU-first ML framework
- tree-based estimators are not generally the place to expect broad GPU acceleration in core scikit-learn

---

## 53) Model persistence and deployment

### Main persistence options
- ONNX
- `skops.io`
- `pickle`
- `joblib`
- `cloudpickle`

### How to think about them

#### ONNX
Best when:
- you mainly want serving / inference
- you do not need the original Python object
- security / portability matters

Trade-off:
- not all scikit-learn models are supported

#### `skops.io`
More secure than pickle-style loading; useful when you want a Python object with more inspectability and less automatic arbitrary code execution risk.

#### `pickle` / `joblib`
Most common Python-native persistence options.

Important warning:
loading pickle-based artifacts can execute arbitrary code.

#### `cloudpickle`
Helpful for custom Python objects/functions, but with weaker portability guarantees.

### Production rules
- save the entire pipeline, not just the final model
- version the environment
- keep training and serving feature logic identical
- do not load untrusted pickle-style files
- test inference on production-like inputs

---

## 54) Common pitfalls

This section is non-negotiable for revision.

### 54.1 Inconsistent preprocessing
Wrong:
- scale train data
- forget to scale test or production data

Right:
- use a pipeline

### 54.2 Data leakage
Wrong:
- fit preprocessing or feature selection on all data before CV

Right:
- fit everything inside the pipeline / fold

### 54.3 Misusing the test set
Wrong:
- repeatedly tune after looking at test performance

Right:
- use validation / CV for tuning, reserve test for final check

### 54.4 Forgetting stratification
On imbalanced classification, random splitting without stratification can distort evaluation.

### 54.5 Using accuracy for imbalanced data
Often misleading.

### 54.6 Misinterpreting coefficients / importances
- coefficient size depends on scaling
- correlated predictors distort interpretation
- feature importance is not causality

### 54.7 Not fixing random seeds
Makes comparisons noisy and hard to reproduce.

### 54.8 Scaling where it matters / not where it matters
- nearest neighbors, SVMs, linear regularized models, PCA: scaling usually matters a lot
- trees: often much less

### 54.9 Using the wrong encoder
- `LabelEncoder` is for `y`
- `OneHotEncoder` / `OrdinalEncoder` are for `X`

### 54.10 Ignoring feature explosion
One-hot encoding and polynomial features can drastically increase dimensionality.

### 54.11 Using t-SNE as proof of clustering
A classic mistake.

### 54.12 Treating CV mean as certainty
Inspect variance and stability, not only the best average number.

---

## 55) Important estimator-specific heuristics

These are practical revision rules, not laws.

### Linear / logistic models
Use when:
- interpretability matters
- features are many and sparse
- good baseline needed
- text classification

### SVM
Use when:
- medium-sized data
- strong decision boundaries needed
- scaling is acceptable

### KNN
Use when:
- local similarity matters
- dataset is moderate in size/dimension
- scaling is handled

### Trees
Use when:
- interpretability or simple nonlinear interactions matter

### Random forests / ExtraTrees
Use when:
- you want strong tabular baseline performance with minimal preprocessing

### Histogram gradient boosting
Use when:
- tabular data is large / important
- you want a high-performance tree ensemble inside native scikit-learn

### Naive Bayes
Use when:
- text / count features
- fast baseline needed

### PCA / TruncatedSVD
Use when:
- dimensionality is high
- denoising / compression / visualization is needed

### DBSCAN / HDBSCAN / OPTICS
Use when:
- cluster shapes are irregular
- noise handling matters
- centroid assumptions are poor

---

## 56) Custom estimators and transformers

To make your own scikit-learn-compatible object:

### For transformers
Implement:
- `fit`
- `transform`

### For estimators
Implement:
- `fit`
- plus `predict` and/or `transform` as appropriate

Best practice:
- inherit from `BaseEstimator`
- use the correct mixins when needed
- keep constructor arguments as pure hyperparameters
- do not put training data inside `__init__`
- learned public attributes should end with `_`

This compatibility is what lets custom objects work with:
- `Pipeline`
- `GridSearchCV`
- CV utilities
- model inspection tools

---

## 57) A compact map of the major scikit-learn topic areas

This is the high-level revision map:

1. **Estimator API**
2. **Data conventions (`X`, `y`, shapes, sparse/dense, DataFrames)**
3. **Preprocessing**
4. **Feature extraction**
5. **Pipelines / composition**
6. **Train/test split**
7. **Cross-validation**
8. **Metrics / scoring**
9. **Threshold tuning**
10. **Hyperparameter search**
11. **Supervised learning**
12. **Unsupervised learning**
13. **Feature selection**
14. **Inspection / interpretability**
15. **Visualizations**
16. **Dataset utilities**
17. **Performance / parallelism / out-of-core**
18. **Persistence / deployment**
19. **Randomness / reproducibility**
20. **Common pitfalls**
21. **Experimental features** (metadata routing, Array API support)

If you understand these thoroughly, you understand scikit-learn at a strong practical level.

---

## 58) Minimal “gold standard” tabular workflow to memorize

```python
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

numeric_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocess = ColumnTransformer([
    ("num", numeric_pipe, numeric_cols),
    ("cat", categorical_pipe, categorical_cols),
])

pipe = Pipeline([
    ("preprocess", preprocess),
    ("model", HistGradientBoostingClassifier(random_state=42)),
])

param_grid = {
    # Example: if the final estimator had searchable params
    # "model__max_depth": [None, 3, 5],
}

search = GridSearchCV(
    pipe,
    param_grid=param_grid,
    scoring="f1_macro",
    cv=5,
    n_jobs=-1
)

search.fit(X_train, y_train)
y_pred = search.predict(X_test)

print(search.best_params_)
print(classification_report(y_test, y_pred))
```

Things this workflow gets right:
- clean split
- preprocessing inside the pipeline
- heterogeneous columns handled properly
- search on the full pipeline
- correct final evaluation on held-out test data

---

## 59) Minimal text-classification workflow to memorize

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, stratify=labels, random_state=42
)

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
    ("clf", LogisticRegression(max_iter=1000))
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

print(classification_report(y_test, y_pred))
```

Why this is strong:
- sparse text representation
- strong linear baseline
- simple, reliable, reproducible

---

## 60) What to memorize vs what to look up

### Memorize
- estimator / transformer / predictor / meta-estimator
- `fit`, `predict`, `transform`, `fit_transform`, `score`
- train/test split and leakage rules
- pipeline + column transformer pattern
- main metrics for classification/regression/clustering
- CV basics and common splitters
- grid search / randomized search
- main model families and when to use them
- persistence safety warning
- randomness / `random_state`
- major pitfalls

### Look up when needed
- exact constructor signatures
- rarely used estimator options
- solver-specific details
- support for missing values / sparse input / DataFrames for a specific estimator
- advanced metadata-routing details
- experimental feature support matrix

---

## 61) Final revision checklist

You are ready with scikit-learn if you can answer these:

- Can you explain the estimator API from memory?
- Do you know the difference between transformer, predictor, and meta-estimator?
- Can you build a `Pipeline` and `ColumnTransformer` from scratch?
- Do you know how to avoid data leakage?
- Can you choose sensible metrics for classification vs regression?
- Do you know when to use `StratifiedKFold`, `GroupKFold`, and `TimeSeriesSplit`?
- Do you know the difference between grid search and randomized search?
- Can you explain when scaling matters and when it usually matters less?
- Do you know the main supervised model families?
- Do you know the main unsupervised model families?
- Can you explain feature extraction vs feature selection?
- Do you know why threshold tuning differs from probability estimation?
- Can you explain why pickle-based persistence is a security risk?
- Can you list the most common scikit-learn pitfalls?

If yes, your scikit-learn revision is in very good shape.

---

## 62) Official references worth keeping open

- User Guide (best conceptual source)
- API Reference (best exact-signature source)
- Glossary of Common Terms and API Elements
- Model selection and evaluation guide
- Pipelines and composite estimators guide
- Preprocessing / imputation / feature extraction guides
- Model persistence guide
- Common pitfalls guide
- Choosing the right estimator guide
- Release history / stable docs for version-specific behavior

---

## 63) One-line summary

**scikit-learn is best understood as a unified ML workflow system built around estimators, transformers, pipelines, cross-validation, and careful evaluation—not just as a bag of algorithms.**
