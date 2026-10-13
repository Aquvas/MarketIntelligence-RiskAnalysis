# Evaluation Plan

## 1. Overview
This document outlines the evaluation strategy for the AI-Powered Market Intelligence and Predictive Business Risk Analysis Platform. The platform's initial machine learning component focuses on **market-stress event classification** within the semiconductor sector (covering NVIDIA, AMD, Intel, TSMC, and Samsung). 

The initial model utilizes historical price and volume data to predict whether a stock will experience a significant downward price movement within a forward-looking window. The current candidate definition of a stress event is a **$\ge 5\%$ decline over 10 trading days** (marked as **PROVISIONAL** and subject to empirical validation). 

Evaluating financial time-series models demands rigorous validation methodologies to prevent data leakage, counter class imbalance, and measure real-world decision utility. This plan establishes empirical protocols, baseline comparisons, evaluation metrics, and reporting standards before model deployment.

---

## 2. Chronological Train/Validation/Test Strategy

### 2.1 Chronological Splitting (No Random Splitting)
Standard cross-validation using random shuffling introduces severe look-ahead bias, as future observations leak into past predictions through autocorrelated returns, market regimes, and overlapping labels. Therefore, **all data splits must strictly preserve chronological order**.

The dataset is partitioned into three consecutive chronological periods:
1. **Training Set**: Earliest historical data up to an initial cutoff timestamp $T_1$. Used for model parameter learning and initial feature screening.
2. **Validation Set**: The subsequent period between timestamp $T_1 + \text{gap}$ and timestamp $T_2$. Used exclusively for hyperparameter tuning, model architecture selection, probability calibration, and decision threshold search.
3. **Test Set**: The most recent period starting after timestamp $T_2 + \text{gap}$ through the end of available data. This set remains completely held out until all modeling choices, feature sets, and decision thresholds are finalized.

> **Crucial Rule:** The test set must **never** be accessed during feature selection, model tuning, threshold adjustment, or exploratory analysis. It is evaluated exactly once for final reporting.

### 2.2 Time-Series Validation Schemes
To assess stability across varying market conditions, two time-series cross-validation schemes are considered:
- **Expanding-Window (Anchored Walk-Forward)**: The training window starts at a fixed historical origin and expands forward over successive folds, adding new validation segments. This maximizes sample size for later folds.
- **Sliding-Window (Rolling Walk-Forward)**: The training window maintains a fixed length (e.g., rolling $N$ years) and shifts forward across time. This adapts faster to regime shifts by discarding stale historical market structures, though with a smaller training sample size.

### 2.3 Split Boundary Buffers (Embargo Gaps)
Because labels are defined over a 10-day forward rolling window, samples within 10 trading days before a split boundary have outcome windows that overlap with the subsequent split. To prevent label leakage, an **embargo buffer of at least 10 trading days** must be enforced between the training set and validation set, and between the validation set and test set.

---

## 3. Baseline Models
Any proposed machine learning model must demonstrate statistically meaningful improvement over simple, reproducible benchmarks. The platform will benchmark against four baseline models:

1. **Always-Predict-Majority-Class (Naive Baseline)**:
   - Always predicts "No Event" (0).
   - Serves as the ground floor for accuracy and specificity, highlighting why naive accuracy is an uninformative metric under class imbalance.
2. **Always-Predict-Positive (Upper Bound on Recall)**:
   - Always flags a stress event (1).
   - Achieves 100% recall at the cost of minimum precision (equal to base rate), illustrating the extreme trade-off of unselective alerting.
3. **Moving-Average Crossover Signal (Heuristic Baseline)**:
   - A traditional technical analysis rule (e.g., when the short-term moving average crosses below the long-term moving average, signal a stress event).
   - Establishes whether statistical or machine learning models outperform standard deterministic momentum indicators.
4. **Logistic Regression with Minimal Features (Linear Baseline)**:
   - A regularized linear classifier trained on basic, intuitive signals (e.g., recent 5-day return and rolling 10-day realized volatility).
   - Serves as the benchmark for whether complex nonlinear models (e.g., gradient-boosted trees or neural networks) add tangible predictive value.

---

## 4. Primary Evaluation Metrics
Given the asymmetric nature of financial risk detection, model performance cannot be judged by accuracy. The primary evaluation framework comprises:

- **Precision** $\left(\frac{TP}{TP + FP}\right)$: Of all alerts raised by the model, what fraction actually resulted in a $\ge 5\%$ decline over the subsequent 10 trading days? Precision directly governs analyst trust and operational efficiency.
- **Recall** $\left(\frac{TP}{TP + FN}\right)$: Of all actual stress events that unfolded, what fraction did the model successfully detect? Recall measures the system's risk-coverage capability.
- **F1-Score** $\left(2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}\right)$: The harmonic mean of precision and recall, balancing event capture with false-alarm containment at a chosen operating threshold.
- **PR-AUC (Precision-Recall Area Under Curve)**: Evaluates trade-offs across all potential decision thresholds. In imbalanced classification, PR-AUC is substantially more informative than ROC-AUC because it focuses on the minority class without being distorted by the large volume of true negatives.
- **Calibration (Reliability Diagram & Expected Calibration Error)**: Assesses whether the model's output probability scores reflect true event frequencies (e.g., if the model assigns a 60% probability of a stress event across 100 instances, approximately 60 of those instances should experience an actual stress event). Well-calibrated probabilities are critical for downstream decision engines and analyst confidence.

---

## 5. Supplementary Metrics
To provide complete diagnostic insight, the following secondary metrics will be monitored:

- **ROC-AUC (Receiver Operating Characteristic AUC)**: Tracked for reference and historical parity, with explicit acknowledgment that it overstates performance when the negative class dominates.
- **Confusion Matrix**: Full breakdown of True Positives ($TP$), False Positives ($FP$), True Negatives ($TN$), and False Negatives ($FN$) at candidate decision thresholds.
- **Precision-Recall Curves across Thresholds**: Visualizing precision and recall trade-offs as the classification threshold sweeps from 0.0 to 1.0 to inform user-configurable operational thresholds.
- **Brier Score** $\left(\frac{1}{N}\sum (p_i - y_i)^2\right)$: Strictly proper scoring rule quantifying both calibration and refinement of probability forecasts.
- **Lead Time**: For all true positives, measuring how many trading days before the maximum drawdown or the 5% drop threshold the warning was first issued. Longer lead times provide higher actionable value to risk analysts.

---

## 6. False-Positive and False-Negative Cost Analysis
In enterprise risk intelligence, prediction errors carry asymmetric business costs:

- **Cost of a False Positive ($FP$)**:
  - The model issues an alert, but no stress event occurs.
  - Consequences: Analyst spends time conducting manual investigations, reviewing SEC filings, and cross-checking supply chain feeds for non-events. Chronic false positives induce alert fatigue and degrade trust in the platform.
- **Cost of a False Negative ($FN$)**:
  - The model remains silent while a company experiences a sharp $\ge 5\%$ downturn.
  - Consequences: Analysts and portfolio stakeholders are blindsided by unexpected capital losses, unhedged downside exposure, or unmitigated business risk.

### Threshold Adjustability
Because the relative cost ratio $C_{FN} / C_{FP}$ differs across organizations and investment mandates (e.g., a defensive risk desk may tolerate high false alarms to avoid missing any drop, whereas an operational analyst prefers high precision), the platform will **not hard-code a fixed 0.5 probability cutoff**. Instead:
- The model outputs continuous, calibrated probabilities.
- Decision thresholds will be adjustable to align with stakeholder preferences and explicit cost matrices established with analyst feedback.

---

## 7. Class Imbalance

### 7.1 Expected Data Distribution
Market-stress events ($\ge 5\%$ drop within 10 days) are expected to be rarer than normal trading periods. The exact class imbalance ratio cannot be known prior to exploratory data analysis on the ingested dataset and **must not be fabricated or assumed**. 

### 7.2 Imbalance Mitigation Strategies
If class imbalance proves severe during the training and validation phase, the following candidate strategies will be tested:
- **Cost-Sensitive Learning / Class Weighting**: Penalizing false negatives more heavily during loss optimization.
- **Resampling Techniques**: Exploring balanced subsampling of the majority class or synthetic oversampling on training data only (never on validation or test sets).
- **Post-Hoc Threshold Tuning**: Optimizing classification cutoffs on the validation set to meet target precision or recall specifications rather than defaulting to 0.5.

> **Metric Constraint:** Standard accuracy $\left(\frac{TP + TN}{Total}\right)$ is uninformative under class imbalance (e.g., a trivial model predicting "No Event" can achieve high accuracy while failing all predictive utility) and will not be used as a primary decision metric.

---

## 8. Overlapping Label Windows and Leakage Prevention

### 8.1 The Overlap Problem
Labels are derived using a 10-day forward rolling window:
$$\text{Label}_t = \mathbb{I}\left(\min_{k \in [1, 10]} \frac{P_{t+k} - P_t}{P_t} \le -0.05\right)$$
Because dates $t$ and $t+1$ share nine days of common price movement in their forward windows:
- Labels of adjacent dates are strongly autocorrelated.
- If data from date $t$ is in the training set and data from date $t+1$ is in the validation set, the model can exploit shared outcome information, leading to artificial inflation of validation scores.

### 8.2 Mitigation and Trade-offs
To eliminate leakage from overlapping windows:
1. **Purging & Embargo**: An embargo gap of at least **10 trading days** must be placed between the end of the training set and the start of the validation set, and between the validation set and the test set.
2. **Feature Availability**: All predictive features at timestamp $t$ must only use information available at market close of day $t$ (strictly backward-looking rolling statistics, no future leakage).
3. **Data Loss Trade-off**: Enforcing embargo gaps discards boundary observations at each split transition. This loss of training instances is an intentional trade-off required to maintain mathematical integrity and prevent look-ahead bias.

---

## 9. Per-Company Evaluation
Evaluating solely on aggregate pooled metrics can conceal severe model bias toward specific high-volatility or large-cap stocks.

- **Individual Company Metrics**: Precision, Recall, F1, PR-AUC, and Brier score must be calculated and reported independently for each of the five companies:
  - NVIDIA (NVDA)
  - AMD (AMD)
  - Intel (INTC)
  - TSMC (TSM)
  - Samsung (005930.KS)
- **Sample Size Constraints**: Five companies represent a focused, constrained cohort. Performance discrepancies across firms (e.g., foundry business models vs. fabless designers vs. integrated device manufacturers) must be cataloged rather than smoothed over in pooled averages.

---

## 10. Generalization Limitations
Findings from this initial model cannot be generalized across broader equity markets without caveat:

- **Sector Concentration**: Semiconductor stocks exhibit sector-specific characteristics, including high cyclicality, capital expenditure cycles, geopolitical exposure, and concentrated supply chains. Performance on these five stocks cannot be assumed to hold for other tech sectors or non-tech equities.
- **Regime Shifts**: Historical performance during low-volatility or bull market regimes may not transfer to high-volatility, macroeconomic rate shock, or supply shortage regimes. Models evaluated on past regimes must explicitly document the temporal market context of the training and evaluation periods.

---

## 11. Threshold Sensitivity Analysis

### 11.1 Provisional Event Definition
The drop threshold of **5% decline over 10 trading days** is a **provisional candidate** chosen for initial pipeline construction. It is not confirmed as the optimal definition of business or market stress.

### 11.2 Sensitivity Exploration Protocol
During the exploratory and validation phase, event frequencies and model behaviors will be analyzed across multiple candidate drop magnitudes:
- **3% decline** over 10 trading days
- **5% decline** over 10 trading days (current candidate)
- **7% decline** over 10 trading days
- **10% decline** over 10 trading days

### 11.3 Rules for Threshold Selection
- The analysis must verify that a chosen threshold yields sufficient positive instances in the training set to enable stable parameter estimation.
- Threshold sensitivity analysis must be conducted **exclusively on the training and validation sets**.
- The definition of the stress event must be permanently locked **before** unblinding the held-out test set.

---

## 12. Reporting Standards
To ensure reproducibility and eliminate reporting bias, final model evaluations must adhere to the following standards:

1. **Held-Out Test Reporting**: All final performance metrics must be reported on the untouched test partition only after all modeling, feature engineering, and threshold selection decisions are frozen.
2. **Uncertainty Quantification**: Report confidence intervals (e.g., via stationary block bootstrap) or standard errors for primary metrics where feasible.
3. **No Selective Reporting**: Prohibit reporting "best-of-many-runs" without explicitly documenting the number of trials and adjusting for multiple testing.
4. **Reproducibility Log**: Every reported evaluation run must link to:
   - Git commit hash of the code repository.
   - Exact training, validation, and test split dates (including embargo window definitions).
   - Complete hyperparameter configurations and random seeds.
   - Exact feature definitions and preprocessing transformations.
