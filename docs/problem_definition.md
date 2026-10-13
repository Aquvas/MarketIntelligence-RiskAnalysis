# Problem Definition

## 1. Project Overview
The long-term vision of the **AI-Powered Market Intelligence and Predictive Business Risk Analysis Platform** is to provide quantitative and qualitative risk intelligence for enterprise strategy, market research, and risk management teams. The intended end-state system will ingest and synthesize diverse, multi-modal information streams—including financial market data, corporate filings and financial reports, real-time news feeds, macroeconomic trends, and multi-tier supply chain and business relationship graphs—to identify and contextualize emerging market and business risks across key economic sectors.

To establish a disciplined engineering and empirical foundation, development follows an incremental, phased roadmap. Rather than attempting to model holistic business risk from the outset, the initial project phase focuses on a tightly scoped, quantifiable machine learning problem within a specific high-impact domain.

## 2. Problem Statement
The initial phase addresses the problem of **market-stress classification** for publicly traded companies using historical time-series market indicators. Specifically, it formulates a supervised learning task to determine whether a given company's equity price will experience an acute adverse market movement over a defined near-term forward period.

Importantly, this initial phase does **not** constitute a complete business-risk prediction system. A market-price decline is driven by broader financial liquidity, macroeconomic sentiment, sector-wide shifts, and trading dynamics; it is not synonymous with operational failure, revenue decline, customer attrition, or structural business disruption. The initial model serves strictly as an early signal-detection component for market-stress events, which will subsequently be integrated into a broader business intelligence architecture.

## 3. Motivation
Market intelligence analysts and strategic risk officers frequently face information overload, making it challenging to anticipate acute market pressure before it materializes. Early detection of adverse asset movements allows analysts and decision-makers to:
- Flag volatile or deteriorating conditions ahead of tactical reviews.
- Prioritize deep-dive investigations into fundamental business catalysts or supply chain choke points.
- Implement proactive risk hedging or scenario planning.

By developing a systematic, reproducible ML pipeline for market-stress event classification, intelligence teams gain an automated quantitative screening mechanism that complements discretionary research.

## 4. Intended User
The primary target users are **market intelligence analysts**, **equity research associates**, and **strategic risk analysts**.

### Workflow Integration
1. **Daily Screening:** The analyst reviews automated alerts highlighting companies flagged as having an elevated probability of experiencing a market-stress event within the upcoming prediction horizon.
2. **Contextual Triangulation:** The analyst inspects quantitative feature contributions (e.g., volume anomalies, volatility regime changes, sector co-movement) alongside fundamental qualitative context (upcoming earnings releases, regulatory announcements, geopolitical headwinds).
3. **Actionable Delivery:** The analyst synthesizes these insights into internal risk advisories, portfolio watchlists, or executive briefing memos.

The platform is designed to augment human analyst workflows, serving as a triage and screening tool rather than an autonomous decision-making engine.

## 5. Initial Industry and Companies
The initial phase focuses exclusively on the **semiconductor industry**. This sector was chosen because of its capital intensity, cyclical demand, geopolitical sensitivity, and complex supply chain interdependencies, which frequently produce distinct market regimes and pronounced volatility.

The initial company universe consists of five leading, highly liquid global semiconductor firms:
- **NVIDIA Corporation (NVDA)** — Specialized in accelerated computing, GPUs, and AI hardware architecture.
- **Advanced Micro Devices, Inc. (AMD)** — Key provider of high-performance CPUs, GPUs, and embedded compute solutions.
- **Intel Corporation (INTC)** — Integrated device manufacturer across client, data center, and semiconductor foundry initiatives.
- **Taiwan Semiconductor Manufacturing Company (TSM)** — Dominant global pure-play semiconductor foundry.
- **Samsung Electronics Co., Ltd. (005930.KS / SMSN.L / OTC)** — Global leader in memory products, consumer electronics, and contract chip manufacturing.

Focusing on these five organizations provides coverage across design, manufacturing, foundries, and integrated device models while keeping data engineering and validation manageable.

## 6. Primary ML Problem
The primary machine learning problem is formulated as **binary market-stress event classification** under a rolling time-series paradigm.

### Formal Formulation
Given a feature vector $\mathbf{x}_{i, t}$ computed from historical data up to the market close of trading day $t$ for company $i$, the model estimates the conditional probability:
$$P(Y_{i, t} = 1 \mid \mathbf{x}_{i, t})$$
where $Y_{i, t} \in \{0, 1\}$ indicates whether a market-stress event occurs during the forward prediction horizon.

### Clarifications on Problem Scope
- **What it IS:** A statistical classifier predicting whether an adverse price dislocation will occur within a specified forward window based on observable historical market indicators.
- **What it is NOT:**
  - It is **not** a continuous price regression or price forecasting model (no point estimates of future stock price).
  - It is **not** an automated trading or execution algorithm (no buy/sell order generation).
  - It is **not** a complete enterprise business-risk model (does not predict insolvency, default, loss of key customers, or fraud).

## 7. Candidate Target Definition
The provisional candidate definition for a market-stress event $Y_{i, t} = 1$ is:
> An event occurs if the minimum trading price (or closing price) of company $i$ drops by at least **5%** below the reference closing price on prediction date $t$ at any point during the subsequent **10 trading sessions**:
> $$Y_{i, t} = \mathbb{I}\left( \min_{\tau \in \{1, \dots, H\}} P_{i, t+\tau} \le (1 - \theta) P_{i, t} \right)$$
> where candidate threshold $\theta = 0.05$ and candidate prediction horizon $H = 10$.

### Status: Provisional & Subject to Empirical Validation
This target definition is strictly a candidate hypothesis and is **not** locked. It requires systematic empirical evaluation during the exploratory data analysis (EDA) phase to determine:
- **Event Frequency & Class Balance:** A 5% drawdown threshold over 10 trading days may be an everyday fluctuation for high-beta stocks during volatile years, while representing a rare event during quiet bull markets or for less volatile equities.
- **Sensitivity to Threshold Value:** The impact of testing alternative candidate thresholds (e.g., 3%, 7%, 10%, or volatility-adjusted dynamic thresholds like $2 \times \sigma$).
- **Analyst Utility:** Whether an unadjusted 5% drawdown threshold provides meaningful signal value for an analyst or introduces excessive false positives.

## 8. Prediction Horizon
The provisional candidate prediction horizon is **10 trading days** (approximately two calendar weeks).

### Tradeoff Analysis
- **Shorter Horizons (e.g., 1–3 trading days):**
  - *Pros:* Stronger microstructure and momentum signals; less unobserved macro variance between feature computation and outcome.
  - *Cons:* Prone to high-frequency market noise and execution slippage; limited lead time for an analyst to conduct substantive review and take strategic action.
- **Longer Horizons (e.g., 20–60 trading days):**
  - *Pros:* Captures major corporate cycles (e.g., quarterly earnings cycles); provides ample time for strategic repositioning.
  - *Cons:* Substantially weaker predictive signal from short-term market features; severe label overlap and serial correlation; significant lag in evaluating predictions.
- **10-Trading-Day Horizon (Candidate Selection):**
  - Balances practical operational lead time for an analyst with sufficient signal retention from short-to-medium-term time-series features.
  - Remains a provisional choice that will be benchmarked against alternative horizons during pipeline prototyping.

## 9. Input Data Required

### Phase 1 Ingestion (Core Scope)
The initial classification model will rely exclusively on structured, point-in-time historical market data:
- **Price History:** Open, High, Low, Close, and Adjusted Close prices.
- **Volume Metrics:** Trading volume, dollar turnover, and relative volume statistics.
- **Benchmark & Sector Indices:** Market benchmarks (e.g., S&P 500 / SPY) and semiconductor sector benchmarks (e.g., SOX / SMH) to compute relative strength and beta.
- **Derived Technical & Statistical Features:** Moving average spreads, realized volatility, Average True Range (ATR), RSI, Bollinger band bandwidth, and rolling correlation against sector benchmarks.

### Potential Future Data Streams (Out of Scope for Initial Classifier)
Future iterations may integrate additional modalities, subject to acquisition cost, licensing, and processing complexity:
- Structured corporate financial statements (10-K, 10-Q, quarterly earnings releases).
- News sentiment, financial press feeds, and earnings call transcripts.
- Supply chain dependency graphs, customer-supplier relationship mapping, and geographic exposure matrices.
*Note: The platform architecture will not assume the availability of these data streams until Phase 1 is validated.*

## 10. Expected System Outputs
For any evaluation date $t$ and company $i$, the initial system will produce:
1. **Binary Classification Label ($\hat{Y}_{i, t} \in \{0, 1\}$):** Indicating whether a market-stress event is expected, calibrated to a decision threshold determined by user cost preferences.
2. **Probability Score ($p_{i, t} \in [0.0, 1.0]$):** Well-calibrated estimate of the likelihood of an adverse market movement over the prediction horizon.
3. **Risk Flag Category:** Coarse categorical tiering (e.g., *Low*, *Elevated*, *High*) for rapid triage in analyst dashboards.
4. **Model Diagnostics & Feature Attribution:** Preliminary local interpretability metrics (such as top contributing features or SHAP values) highlighting which market factors drove the risk score.

*Future Outputs (Phases 2+):* Natural language synthesis of underlying drivers, corroborated financial report citations, and supplier impact assessments.

## 11. Evaluation Metrics and Success Criteria
Because market-stress events are subject to label imbalance and false alerts impose an analytical triage cost, model performance cannot be measured by accuracy alone.

### Primary Evaluation Metrics
- **Precision (Positive Predictive Value):** Ensures that when the system issues a market-stress alert, it corresponds to an actual event a high fraction of the time, avoiding analyst alert fatigue.
- **Recall (Sensitivity):** Assesses the fraction of actual market-stress events detected by the model.
- **Precision-Recall Area Under the Curve (PR-AUC):** Primary discrimination metric suitable for class-imbalanced time-series targets.
- **F1 Score / $F_\beta$ Score:** Harmonized balance between precision and recall, configurable based on whether missing an event is more penalized than a false alarm.
- **Brier Score & Reliability Diagrams:** Evaluates probability calibration, ensuring reported probabilities reflect true historical event frequencies.

### Success Criteria Philosophy
Specific numerical threshold targets (e.g., minimum precision or PR-AUC levels) will not be fabricated in advance. Instead, success criteria will be formally defined relative to **heuristic baselines** (e.g., rolling historical frequency, momentum baselines, and naive buy-and-hold benchmarks) following exploratory data analysis and initial baseline experiments.

## 12. Scope Boundaries

| Capability / Dimension | In Scope (Phase 1) | Future Phases |
| :--- | :--- | :--- |
| **Asset Universe** | 5 specific semiconductor equities (NVDA, AMD, INTC, TSM, Samsung) | Broad semiconductor ecosystem, adjacent tech sectors, cross-asset coverage |
| **Data Modalities** | Historical daily price, volume, and sector/market index series | Filings, transcripts, news feeds, supply chain relationship graphs |
| **Task Type** | Binary classification of candidate market-stress events | Multi-class severity estimation, multi-horizon forecasts, qualitative risk explanation |
| **Model Nature** | Supervised statistical and ML baseline models (Logistic Regression, LightGBM, Random Forest) | Multi-modal architectures, LLM reasoning agents, Graph Neural Networks |
| **Backtesting & Validation** | Walk-forward cross-validation strictly preventing look-ahead bias | Dynamic operational retraining with automated data pipeline updates |

## 13. Out-of-Scope Objectives
To maintain rigor and avoid scope creep, the initial implementation explicitly excludes:
- Real-time intraday tick streaming or sub-daily execution signals.
- Automated algorithmic trade execution, portfolio optimization, or capital allocation.
- Ingestion and NLP processing of unstructured news or social sentiment.
- Graph-based propagation of supply chain disruption.
- Prediction of structural business insolvency, corporate default, or forensic accounting anomalies.
- Creation of automated investment advice or regulatory financial recommendations.

## 14. Assumptions
The initial research and engineering effort is built upon the following provisional assumptions:
1. **Market Efficiency & Information Diffusion:** Observable historical market pricing and volume anomalies exhibit serial dependence or volatility clustering that provides modest, exploitable predictive signal for near-term drawdowns.
2. **Data Availability & Quality:** Reliable, split- and dividend-adjusted daily historical price and volume data are accessible for the selected tickers.
3. **Point-in-Time Integrity:** All feature transformations can be computed strictly with data available as of the market close on date $t$, precluding look-ahead bias.
4. **Generalizability Across Universe:** The selected semiconductor companies share sufficient sector dynamics that joint or cross-validated modeling yields meaningful insights, despite differences in primary listing exchanges and reporting currencies (e.g., US ADRs vs. Korean Won).

## 15. Limitations
An objective assessment of technical and practical constraints includes:
- **Proxy Disconnect:** Market-stress events reflect public equity sentiment, liquidity shifts, and macroeconomic rates; they do not systematically reflect fundamental corporate solvency or business stability.
- **Macro Dominance:** Broad market shocks (e.g., sudden interest rate announcements, geopolitical escalations) can cause drawdowns across all equities irrespective of individual company health, creating irreproducible or exogenous target events.
- **Survivorship and Regime Shift Bias:** Market dynamics in semiconductor stocks have shifted markedly across different technological and macroeconomic eras (e.g., the crypto mining cycles, the post-2022 AI acceleration); models trained on past regimes may degrade under new market regimes.
- **Class Imbalance & Sample Size:** In bull market regimes, genuine 5% drawdowns within 10 trading days may occur infrequently, limiting the number of positive training exemplars.

## 16. Risks
- **Data Leakage & Look-Ahead Bias:** Accidental inclusion of future information during scaling, technical indicator calculation, or cross-validation fold splitting will produce unrealistically high backtest scores that fail out-of-sample.
- **Overfitting to Volatile Regimes:** High-capacity non-linear models could overfit noise in volatile stocks (e.g., NVDA, AMD) while failing to generalize to more stable or mature equities (e.g., INTC, Samsung).
- **False Alarm Fatigue:** Low precision would lead to frequent false alarms, quickly degrading user trust and practical adoption by market intelligence analysts.
- **Currency and Exchange Misalignment:** Comparing US-traded equities with non-US primary listings (e.g., Samsung on KRX, TSMC on TWSE vs. US ADR) involves differing trading calendars, time zones, and FX fluctuations that must be normalized carefully.

## 17. Unresolved Decisions
The following open questions must be resolved through empirical analysis before locking the pipeline specification:
1. **Target Price Selection:** Should the candidate 5% drawdown be evaluated against the forward intraday low ($P_{low}$) or the forward closing price ($P_{close}$)?
2. **Dynamic vs. Fixed Threshold:** Should the candidate 5% threshold remain a fixed absolute percentage, or be standardized against rolling historical volatility (e.g., $k \times \text{ATR}$ or rolling standard deviation)?
3. **Ticker Universe Normalization:** For Samsung and TSMC, should the model evaluate their primary local currency exchange listings or their US dollar-denominated ADR equivalents?
4. **Overlap Handling in Cross-Validation:** Since 10-day forward prediction horizons create overlapping evaluation periods, what purging and embargoing scheme will be implemented in walk-forward cross-validation to prevent serial dependency leakage?
5. **Baseline Benchmark Definition:** What constitutes the minimum viable benchmark that the ML model must outperform to justify continued development (e.g., simple moving average crossover vs. logistic momentum regression)?
