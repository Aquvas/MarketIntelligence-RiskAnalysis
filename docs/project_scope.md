# Project Scope

## 1. Executive Summary & Vision

The **AI-Powered Market Intelligence and Predictive Business Risk Analysis Platform** is designed to provide actionable intelligence to market and business analysts. The long-term vision encompasses continuous ingestion of quantitative market data, corporate filings, news streams, and supply-chain/competitor relationships to evaluate comprehensive market and business risks.

However, realizing this vision requires an incremental, phased engineering approach. The initial scope focuses exclusively on building and rigorously validating a **market-stress classification** model for a targeted group of companies in the semiconductor sector.

---

## 2. MVP Definition

### 2.1 What the MVP Will Do
The Minimum Viable Product (MVP) implements an end-to-end historical machine learning pipeline for binary market-stress classification across five key semiconductor equities:
- **NVIDIA (NVDA)**
- **AMD (AMD)**
- **Intel (INTC)**
- **TSMC (TSM)**
- **Samsung Electronics (005930.KS / SMSN.IL)**

The system will ingest daily historical price and volume data, extract technical and statistical features, train classical machine learning models alongside baseline benchmarks, and evaluate performance using chronological splits and imbalance-aware metrics.

### 2.2 What the MVP Will NOT Do
The initial MVP explicitly excludes:
- Real-time or streaming inference
- Ingestion or processing of unstructured news or text data
- Supply chain knowledge graphs or graph neural networks (GNNs)
- Large Language Model (LLM) explanations or Retrieval-Augmented Generation (RAG)
- Multi-industry or cross-sector expansion
- Automated trade execution or buy/sell recommendations

---

## 3. Core Features (MVP)

1. **Historical Market Data Ingestion Pipeline**
   - Automated ingestion of daily open, high, low, close, and volume (OHLCV) data for the 5 target semiconductor companies over a multi-year historical span.
   - Validation checks for trading day alignment, corporate actions (splits, dividends), and missing data.

2. **Feature Engineering**
   - Computation of price returns across multiple lookback windows (e.g., 1-day, 5-day, 20-day).
   - Volatility indicators (historical standard deviation, Average True Range).
   - Momentum and trend indicators (simple and exponential moving averages, moving average convergence/divergence).
   - Volume metrics (volume moving averages, volume rate of change).
   - Strict adherence to point-in-time calculation to eliminate look-ahead bias and data leakage.

3. **Binary Market-Stress Classification**
   - **Label Definition**: A binary target indicating whether a stock experiences a peak-to-trough decline meeting or exceeding a *provisional candidate threshold* of 5% over a *prediction horizon* of 10 trading days.
   - *Note*: Both the 5% decline threshold and the 10-day prediction horizon are provisional candidate parameters subject to rigorous empirical validation.

4. **Rigorous Train / Validation / Test Splitting**
   - Enforce strict chronological (time-series) cross-validation and splits to reflect real-world forecasting conditions. Random k-fold cross-validation is strictly forbidden.

5. **Baseline Comparison Models**
   - Naive majority-class classifier (always predict no-stress).
   - Rule-based heuristics (e.g., moving average crossover, momentum drop).
   - Logistic Regression as a linear benchmark.

6. **Classical ML Model Exploration**
   - Tree-based models suited for tabular time-series features (Random Forest, Gradient Boosting / LightGBM / XGBoost).

7. **Comprehensive Evaluation Metrics**
   - Primary evaluation on precision, recall, F1-score, and Precision-Recall Area Under Curve (PR-AUC) given class imbalance.
   - Evaluation conducted both in aggregate and disaggregated per company.

8. **Threshold Sensitivity Analysis**
   - Explicit documentation evaluating performance sensitivity across alternative candidate thresholds (e.g., 3%, 5%, 7%, 10%) and prediction horizons (e.g., 5, 10, 20 trading days).

---

## 4. Market-Stress Prediction vs. Business-Risk Analysis

A critical conceptual requirement of this project is avoiding the conflation of market-stress classification with holistic business-risk analysis:

| Dimension | Market-Stress Classification (Initial Model) | Business-Risk Analysis (Long-Term Platform) |
| :--- | :--- | :--- |
| **Focus** | Short-term equity price decline ($\ge 5\%$ over 10 trading days). | Structural operational, financial, and strategic risks. |
| **Inputs** | Daily historical OHLCV data (price, volume, volatility). | SEC 10-K/10-Q filings, earnings transcripts, supply-chain links, macro indicators. |
| **Scope of Insight** | Market dynamics, investor sentiment, and trading pressure. | Solvency, revenue trajectory, customer concentration, competitive disruption. |
| **Methodology** | Classical time-series feature engineering and classification. | Multimodal RAG, Knowledge Graphs, NLP, fundamental financial modeling. |

### Why Conflation is Misleading
A sharp decline in stock price does not automatically imply operational failure, customer defection, or earnings contraction. Equities frequently drop due to broader macroeconomic shifts, sector-wide multiple compression, interest rate changes, or short-term liquidity shocks while underlying business operations remain sound. Conversely, a company may face severe operational or balance-sheet deterioration long before it is reflected in sharp short-term equity price volatility.

The MVP is strictly a **market-stress classification** system. It does not provide full-spectrum business-risk analysis.

---

## 5. Technology Stack Roadmap

The platform adopts a staged technology progression:

| Component | MVP Stage | Future Phases |
| :--- | :--- | :--- |
| **Core Languages** | Python, SQL | Python, SQL |
| **Storage & Data** | Flat files / Local SQLite | PostgreSQL, Time-series DB |
| **Machine Learning** | Scikit-learn, LightGBM / XGBoost | PyTorch / TensorFlow (deep sequence models) |
| **NLP & Semantics** | *None* | Hugging Face Transformers, News Sentiment pipelines |
| **Graph Analysis** | *None* | NetworkX, PyTorch Geometric (GNNs for supply chains) |
| **AI Orchestration** | *None* | LangGraph, RAG frameworks, LLMs |
| **Serving & UI** | Python CLI / Evaluation scripts | FastAPI, React dashboard |
| **Infrastructure** | Local environments, Git | Docker, MLflow, CI/CD pipelines |

---

## 6. Phased Implementation Roadmap

- **Phase 1: MVP - Data Pipeline and Baseline Models**
  - Historical data ingestion for NVDA, AMD, INTC, TSM, Samsung.
  - Feature engineering and chronological splitting.
  - Baselines, tree models, and PR-AUC/F1 evaluation with threshold sensitivity documentation.

- **Phase 2: Sector-Level Features & Benchmark Indices**
  - Incorporation of macroeconomic benchmarks (e.g., SOX index, S&P 500) and relative strength features.

- **Phase 3: NLP-Based News Sentiment Features**
  - Ingestion of financial news streams, sentiment classification, and topic extraction mapped to company tickers.

- **Phase 4: Financial Report & Filing Analysis**
  - Automated parsing of 10-K/10-Q filings, fundamental ratios, and MD&A section analysis.

- **Phase 5: Knowledge Graphs & GNN-Based Relationship Modeling**
  - Mapping tier-1/tier-2 suppliers, customer exposure, and geographic manufacturing dependencies using Graph Neural Networks.

- **Phase 6: RAG & LLM-Powered Explanations**
  - Contextual synthesis of quantitative signals with unstructured evidence to generate analyst-ready risk briefings.

- **Phase 7: Full API & Analyst Frontend**
  - Modular FastAPI service backed by PostgreSQL and an interactive React-based analyst interface.

- **Phase 8: Production Deployment, MLflow & CI/CD**
  - Model registry, experiment tracking with MLflow, containerized deployments via Docker, and automated retraining pipelines.

---

## 7. Explicit Non-Goals

To maintain focus and avoid misaligned expectations, the following are explicitly designated as non-goals:
1. **Automated Trading Recommendations**: The platform will not generate buy/sell signals or execute orders.
2. **Real-Time / Streaming Prediction**: The initial phases do not target tick-level or sub-minute streaming infrastructure.
3. **Revenue / Earnings Forecasting**: The model does not attempt to predict quarterly revenue or EPS figures.
4. **Bankruptcy / Corporate Failure Prediction**: The models are not calibrated to predict corporate solvency or default events.
5. **Portfolio Optimization**: The platform will not construct or balance investment portfolios.
6. **Replacing Human Analyst Judgment**: The system is designed strictly as an intelligence-augmentation tool, not an autonomous analyst.
7. **Broad Multi-Industry Coverage in Initial Release**: Initial scope is restricted strictly to the 5 designated semiconductor equities.
8. **Guaranteed Prediction Accuracy**: Stock market movements are inherently noisy; no guarantees of positive predictive value or edge are made. All models require empirical validation before any operational use.
