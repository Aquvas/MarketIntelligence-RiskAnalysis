# Phase 0 Decisions

## 1. Overview
The purpose of this document is to formally capture all Phase 0 architectural, analytical, and scoping decisions, working assumptions, unresolved open questions, and foundational risks for the **AI-Powered Market Intelligence and Predictive Business Risk Analysis Platform**. 

Phase 0 is restricted strictly to documentation, framework formulation, and planning. Crucially, this initiative delineates near-term quantitative market-stress event classification from longer-term structural business-risk assessment: a short-term equity price decline reflects market sentiment and trading dynamics, not necessarily intrinsic operational or business failure.

---

## 2. Confirmed Decisions
The following foundational decisions are established and firm for Phase 0:

- **Domain Focus**: Semiconductor manufacturing and design industry.
- **Target Companies (5 Entities)**:
  - NVIDIA Corporation (`NVDA` - NASDAQ)
  - Advanced Micro Devices, Inc. (`AMD` - NASDAQ)
  - Intel Corporation (`INTC` - NASDAQ)
  - Taiwan Semiconductor Manufacturing Company (`TSM` - NYSE ADR)
  - Samsung Electronics Co., Ltd. (`005930.KS` - KRX)
- **ML Formulation**: Supervised binary classification of market-stress events.
- **Initial Data Modality**: Historical daily price and trading volume data (OHLCV).
- **Evaluation Methodology**: Strict chronological (time-based) train/validation/test splitting combined with benchmark and naive baselines to rigorously prevent data leakage and look-ahead bias.
- **Intended End-User**: Market and business intelligence analysts requiring early-warning situational awareness.
- **Phase 0 Scope Boundary**: Pure documentation, problem structuring, and research planning—no production code, training scripts, or pipeline implementation in this phase.
- **Scope Distinction**: The initial system performs empirical **market-stress classification**, NOT comprehensive **business-risk analysis**. Advanced modalities (unstructured news NLP, supply-chain knowledge graphs, GNNs, RAG/LLM synthesizers) represent roadmap phases, not MVP deliverables.

---

## 3. Provisional Assumptions
The following decisions serve as working hypotheses subject to empirical testing and validation during Phase 1:

- **Prediction Horizon (10 Trading Days)**: *[PROVISIONAL]* Formulated as predicting an event occurrence across a forward window of 10 trading days. Requires validation against event frequency, labeling density, and performance comparisons with shorter (e.g., 5-day) or longer (e.g., 20-day) horizons.
- **Stress Threshold (5% Decline)**: *[PROVISIONAL]* Defined as a forward drawdown or cumulative decline of $\ge 5\%$. Provisional until empirical historical event frequency and volatility distributions are computed across all five tickers; may be recalibrated (e.g., to 3%, 7%, or dynamic volatility-adjusted thresholds).
- **Feature Set Sufficiency**: *[PROVISIONAL]* Technical features derived solely from OHLCV data (momentum, trend, volatility, volume patterns) are assumed sufficient to establish a meaningful baseline model before integrating macroeconomic indicators or alternative data.
- **Data Sourcing**: *[PROVISIONAL]* Freely accessible public market data APIs (e.g., Yahoo Finance via `yfinance`) are assumed adequate for baseline modeling, though corporate action adjustments and cross-border data quality remain to be validated.
- **Class Labeling Architecture**: *[PROVISIONAL]* A single binary threshold label is assumed for MVP simplicity, pending exploration of multi-class severity categories or continuous return/drawdown regressions.

---

## 4. Unresolved Questions
All items below are active open issues designated for resolution during Phase 1:

- **[Open]** What is the historical frequency of 5% decline events for each company? Is it sufficient for training without severe class imbalance collapse?
- **[Open]** Should Samsung Electronics be represented via its native Korean-listed ordinary shares (`005930.KS`), a European GDR, or an OTC ADR? What are the currency conversion and data availability implications?
- **[Open]** How much historical data is required (e.g., 5 years vs. 10–15 years)? What is the exact tradeoff between sample size expansion and historical structural/regime change?
- **[Open]** Should the system train dedicated per-company models or a unified pooled/global model across all five companies (with company identifiers or embeddings)?
- **[Open]** What is the operational analyst's specific tolerance and cost matrix regarding False Positives (alert fatigue) versus False Negatives (missed drawdown events)?
- **[Open]** Should inference run on a fixed daily rolling schedule for all active assets, or be triggered conditionally by market anomaly filters?
- **[Open]** How should overlapping 10-day forward windows be handled in feature computation, label creation, and cross-validation to prevent autocorrelation leakage and target redundancy?
- **[Open]** Is 5% the optimal operational threshold, or should the platform support multi-tier thresholds (e.g., moderate vs. severe stress) or volatility-normalized drawdowns?
- **[Open]** Should the downstream model output discrete binary decisions, well-calibrated posterior probabilities, or a combined risk score?
- **[Open]** What minimum statistical performance thresholds (e.g., Precision, Recall, PR-AUC over naive class-prior baseline) are required for the system to deliver practical utility to an analyst?
- **[Open]** How should the data ingestion and modeling pipeline handle calendar discrepancies when international exchanges have mismatched trading days, market holidays, and non-overlapping timezones?

---

## 5. Risks Requiring Investigation

| Risk | Description | Potential Impact | Investigation Required |
| :--- | :--- | :--- | :--- |
| **Insufficient Positive Examples** | Severe downward price moves ($\ge 5\%$) may occur infrequently during prolonged semiconductor bull cycles. | High class imbalance, model convergence failure, or degenerate majority-class predictions. | Run empirical event-frequency analysis across multiple lookback windows (3, 5, 10 years) and evaluate precision-recall curves and resampling techniques. |
| **Market Regime Change** | Macroeconomic shifts (interest rate cycles, export restrictions, AI capex booms) alter underlying asset dynamics. | Models trained on prior regimes may degrade rapidly when deployed into novel market conditions. | Backtest performance across segmented macro regimes (e.g., 2018–2019 downturn, 2020–2021 surge, 2022 contraction, 2023–2024 AI wave). |
| **Data Quality & Split Adjustments** | Public data sources (e.g., Yahoo Finance) may contain unadjusted splits, dividend distortions, or volume gaps. | Synthetic anomalies, inaccurate price differentials, and distorted feature calculations. | Cross-validate historical series against secondary commercial sources and audit known corporate action dates. |
| **Samsung Cross-Border Discrepancies** | Samsung trades on KRX (KRW currency, KST timezone) while peers trade on US exchanges (USD, EST). | Asynchronous market opens, non-aligned trading calendars, and currency fluctuations confounding cross-company analysis. | Evaluate whether to analyze in native currency vs. USD-hedged, and design a timezone/holiday alignment matrix. |
| **Overfitting on Small Universe** | Developing features and tuning hyper-parameters across only 5 assets increases risk of fitting noise. | Poor out-of-sample generalization and deceptive backtest results. | Enforce strict chronological out-of-sample testing, nested cross-validation, and avoid overly complex deep architectures for MVP. |
| **Look-Ahead Bias & Feature Leakage** | Normalization, windowing, or label generation inadvertently incorporating $t+k$ data into step $t$. | Artificially inflated backtest accuracy that collapses in live inference. | Audit pipeline transformations to ensure all scalers, rolling indicators, and statistics use expanding or backward-looking rolling windows only. |
| **Conflation of Market Stress & Business Risk** | Stakeholders may conflate an algorithmic market-stress warning with fundamental solvency or operational distress. | Misinformed strategic decisions and loss of trust in predictive intelligence. | Explicitly enforce disclaimers, clear interface taxonomy, and documented scoping separating price stress from enterprise health. |
| **Threshold Sensitivity** | Minor shifts in threshold (e.g., 4.5% vs 5.0% vs 5.5%) could cause drastic swings in label distribution. | Fragile models that exhibit erratic performance when market volatility shifts. | Conduct multi-threshold sensitivity matrices across 3%, 5%, 7%, and 10% during exploratory data analysis. |
| **Benchmark Comparison Deficit** | Evaluating models in isolation without simple reference baselines obscures true value-add. | Inability to prove whether ML adds signal beyond a simple momentum rule or index beta. | Establish clear benchmark baselines: dummy majority classifier, rolling volatility threshold, semiconductor ETF (`SOXX`/`SMH`) beta baseline. |

---

## 6. Phase 0 Completion Criteria
Phase 0 is formally concluded and signed off only when all the following prerequisites are met:

1. **Documentation Complete**: All six foundational documentation files are fully drafted, verified, and internally cross-referenced:
   - `docs/problem_definition.md`
   - `docs/project_scope.md`
   - `docs/technology_stack.md`
   - `docs/data_requirements.md`
   - `docs/evaluation_plan.md`
   - `docs/phase_0_decisions.md`
2. **Clear Problem Differentiation**: The problem statement unequivocally distinguishes market-stress classification from comprehensive corporate credit/business-risk analysis.
3. **Rigorous Evaluation Plan**: The evaluation strategy mandates strict chronological splitting, explicit leakage prevention safeguards, and baseline model comparisons.
4. **Provisional Status Transparency**: Working hypotheses (specifically the 5% drawdown threshold and 10-day prediction horizon) are explicitly cataloged as requiring empirical validation.
5. **Open Question Governance**: All unresolved technical, business, and operational questions are documented with designated Phase 1 resolution milestones.
6. **Strict Scope Delineation**: MVP scope boundaries are cleanly demarcated from post-MVP enhancements (unstructured NLP, knowledge graphs, GNNs, LLM/RAG).
7. **Technology Justification**: Every component in the proposed technology stack is explicitly justified against project constraints.
8. **Data Auditing Blueprint**: Ingestion prerequisites identify required fields, available free sources, and international harmonization uncertainties.
9. **Stakeholder Approval**: The designated stakeholder (user/analyst) has reviewed and signed off on the Phase 0 deliverables.

---

## 7. Phase 1 Preview
Phase 1 focuses on empirical data acquisition, exploratory data analysis, and baseline validation. Without initiating execution in Phase 0, Phase 1 tasks comprise:

1. **Data Acquisition & Harmonization**: Retrieve historical daily OHLCV data for `NVDA`, `AMD`, `INTC`, `TSM`, `005930.KS`, and semiconductor benchmark indices/ETFs (`SOXX`, `SMH`, `^GSPC`).
2. **Exploratory Data Analysis (EDA)**: Profile return distributions, volatility profiles, missing-value incidence, stationarity properties, and exchange holiday overlaps.
3. **Event Frequency & Threshold Sensitivity**: Compute historical event frequencies across candidate decline thresholds (3%, 5%, 7%, 10%) and candidate forward horizons (5, 10, 15, 20 trading days) to empirically resolve provisional assumptions.
4. **Chronological Split Implementation**: Construct train, validation, and out-of-sample test splits respecting historical market cycles and eliminating look-ahead bias.
5. **Baseline Feature Pipeline**: Implement reproducible, point-in-time technical and volume feature transformations (e.g., returns, moving average divergences, RSI, ATR, volume ratios).
6. **Model Baseline Benchmarking**: Train and evaluate initial naive and standard ML baselines (majority class, logistic regression, gradient boosting) on precision, recall, PR-AUC, and calibration.
7. **Decision Log Updates**: Resolve Phase 0 open questions, update provisional assumptions with empirical findings, and finalize the modeling architecture for subsequent phases.
