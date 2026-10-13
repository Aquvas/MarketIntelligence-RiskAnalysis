# Technology Stack

## 1. Overview

This document outlines the technology strategy and component stack for the **AI-Powered Market Intelligence and Predictive Business Risk Analysis Platform**.

The platform is designed with a clear architectural principle: **start simple and justify complexity**. Rather than building an over-engineered architecture upfront, the stack is partitioned into an immediate **MVP Phase** focused on robust baseline models and reproducible tabular pipelines, and sequential **Future Phases** where advanced technologies (deep learning, NLP, knowledge graphs, LLMs, and enterprise deployment tools) are adopted strictly when measurable performance or functional requirements demand them.

---

## 2. Technology Stack Table

| Technology / AI Field | Proposed Role | Why It May Be Useful | Phase |
|---|---|---|---|
| Python | Core programming language | Industry standard for ML/data science ecosystem and rapid iteration | MVP |
| SQL / PostgreSQL | Data storage and querying | Structured storage of historical prices, engineered features, and model run outputs | MVP |
| pandas / NumPy | Data manipulation and numerical computation | Standard, high-performance tabular feature engineering and numerical pipelines | MVP |
| Scikit-learn | Classical ML models | Fast, interpretable baselines (logistic regression, random forest, gradient boosting) & evaluation utilities | MVP |
| matplotlib / seaborn | Data visualization | Exploratory data analysis, diagnostic plots, ROC/PR curves, and threshold sensitivity analysis | MVP |
| TensorFlow or PyTorch | Deep learning / time-series models | Sequential time-series architectures (LSTM/Transformer) for complex temporal dynamics | Future (Phase 2–3) |
| NLP libraries (spaCy, Hugging Face Transformers) | News sentiment analysis | Extract sentiment and risk signals from unstructured financial headlines and filings | Future (Phase 3) |
| Knowledge Graphs (Neo4j or similar) | Company relationship modeling | Explicitly represent supply-chain dependencies, competitive relationships, and partner networks | Future (Phase 5) |
| Graph Neural Networks (GNNs) | Relationship-aware prediction | Propagate upstream/downstream risk signals across interconnected industry entities | Future (Phase 5) |
| RAG + LLMs | Evidence-grounded explanations | Generate natural-language analyst summaries grounded in cited news articles and filings | Future (Phase 6) |
| LangGraph | AI workflow orchestration | Coordinate multi-agent reasoning, validation loops, and structured risk synthesis | Future (Phase 6+) |
| FastAPI | Backend REST API | Expose high-throughput endpoints for predictions, backtest results, and data access | Future (Phase 7) |
| React | Frontend UI | Interactive analyst dashboard for risk alerts, charts, and audit trails | Future (Phase 7) |
| Docker | Containerization | Ensure reproducible runtimes across development, testing, and production | Future (Phase 8) |
| MLflow | Model lifecycle management | Track hyperparameters, metrics, model artifacts, and registry versioning | Future (Phase 8) |
| CI/CD (GitHub Actions or similar) | Automated testing and deployment | Enforce test coverage, linting, data validation, and deployment gates | Future (Phase 8) |

---

## 3. MVP Technology Justification

Each MVP technology is selected to address core requirements with minimal operational overhead:

- **Python**: Serves as the unifying lingua franca for data science, machine learning, and automation. Its ecosystem provides mature interfaces to all numerical and analytical libraries needed for market analysis.
- **SQL / PostgreSQL**: Guarantees ACID compliance, structured schemas, and efficient indexing for time-series equity records (OHLCV), engineered feature snapshots, and experiment predictions. Prevents data fragmentation caused by raw flat files.
- **pandas / NumPy**: Provides vectorized, optimized tabular manipulation essential for calculating rolling indicators (e.g., ATR, RSI, moving averages), lag features, and forward returns without look-ahead bias.
- **Scikit-learn**: Offers battle-tested implementations of foundational classification algorithms (Logistic Regression, Random Forest, HistGradientBoostingClassifier) along with rigorous cross-validation (TimeSeriesSplit), calibration tools (CalibratedClassifierCV), and standard scoring metrics (Precision, Recall, PR-AUC, Brier Score).
- **matplotlib / seaborn**: Delivers reliable, scriptable charting capabilities required for exploratory data analysis (EDA), residual analysis, precision-recall tradeoff visualization, and parameter sensitivity reporting.

---

## 4. Future Technology Justification

Advanced technologies solve specific shortcomings of MVP tools but introduce technical complexity, compute cost, and maintenance burden. They are scheduled for later phases and gated by empirical triggers:

- **TensorFlow or PyTorch**
  - *Problem solved*: Classical feature engineering cannot easily capture long-range, non-linear sequence dependencies or raw tick-level temporal patterns.
  - *Adoption trigger*: Classical tree-based and regularized linear models hit a performance ceiling (e.g., PR-AUC plateaus) and error analysis proves long-term sequential memory is lacking.
  - *Why not premature*: High compute/training cost, risk of overfitting on noisy financial price series, and opaque hyperparameter tuning.
- **NLP Libraries (spaCy, Hugging Face Transformers)**
  - *Problem solved*: Quantitative market prices often lag qualitative disclosures, breaking news, or regulatory filings.
  - *Adoption trigger*: Baseline price-only models fail to anticipate sudden market-stress events triggered by exogenous news shocks.
  - *Why not premature*: News processing requires continuous scraping, deduplication, timestamp alignment, and heavy token inference infrastructure.
- **Knowledge Graphs (Neo4j or similar)**
  - *Problem solved*: Relational tables poorly model multi-hop entity interdependencies (e.g., TSMC wafer yield affecting NVIDIA chip supply).
  - *Adoption trigger*: Need to trace multi-tier supply chain vulnerabilities and cross-entity risk contagion explicitly.
  - *Why not premature*: High curation and maintenance overhead to keep supply chain graphs accurate and up to date.
- **Graph Neural Networks (GNNs)**
  - *Problem solved*: Graph structure alone does not compute predictive feature embeddings across connected node neighborhoods.
  - *Adoption trigger*: A validated knowledge graph is operational and single-entity risk prediction proves insufficient for industry-wide contagion.
  - *Why not premature*: GNN training is complex, sensitive to graph topology sparsity, and unnecessary without a verified graph database.
- **RAG + LLMs**
  - *Problem solved*: Raw model probability scores lack qualitative, contextual narrative explanations needed by non-technical risk officers.
  - *Adoption trigger*: Analysts require verifiable citations and structured executive briefings linking news items to model probability alerts.
  - *Why not premature*: LLM hallucination risks, high token inference latency/costs, and dependency on stable underlying data pipelines.
- **LangGraph**
  - *Problem solved*: Linear scripts cannot handle cyclical multi-step reasoning, automated fact-checking, or agentic retrieval loops.
  - *Adoption trigger*: Qualitative explanation and verification workflows require multi-agent orchestration and dynamic branching.
  - *Why not premature*: Adds orchestration complexity before individual analytical tasks and RAG pipelines are stabilized.
- **FastAPI & React**
  - *Problem solved*: Command-line scripts and static notebooks do not support multi-user real-time interaction or system integration.
  - *Adoption trigger*: Platform moves from exploratory research to operational analyst workflows.
  - *Why not premature*: Building UI and API contracts prematurely locks in exploratory data structures before model schemas stabilize.
- **Docker, MLflow, CI/CD**
  - *Problem solved*: Environment drift, unversioned models, and manual testing failure risks.
  - *Adoption trigger*: Codebase transitions from initial prototype experimentation to collaborative multi-developer delivery.
  - *Why not premature*: Heavy infrastructure setup detracts focus from verifying whether the core predictive signal exists.

---

## 5. Technology Selection Principles

1. **Start simple, add complexity only when justified by measurable improvement**: Baseline models (e.g., Logistic Regression or Gradient Boosting) must be established first.
2. **Each technology must solve a specific, identified problem**: No framework is adopted without an explicit operational or statistical requirement that existing components cannot satisfy.
3. **Avoid resume-driven development**: Prioritize delivery speed, interpretability, and reliability over novelty.
4. **Prefer well-supported, mature libraries**: Rely on stable open-source ecosystems with active communities, comprehensive documentation, and long-term support.
5. **Advanced models must outperform simpler baselines**: Any deep learning, graph, or generative architecture must clearly beat simpler baselines on out-of-sample metrics (PR-AUC, F1-score, Brier score) to justify its ongoing computational and maintenance costs.

---

## 6. Open Decisions

| Decision | Alternatives | Evaluation Criteria |
|---|---|---|
| **Deep Learning Framework** | PyTorch vs. TensorFlow | Community adoption for time-series transformers, ease of debugging, and ecosystem integration. |
| **NLP Pipeline Choice** | spaCy + lightweight sentiment vs. FinBERT / Hugging Face | Domain specificity of financial sentiment vs. latency, compute footprint, and GPU requirements. |
| **Graph Database Choice** | Neo4j vs. AWS Neptune vs. NetworkX (in-memory) | Scale requirements, cost of managed cloud services vs. local embedded graph processing. |
| **Relational Storage Deployment** | Local PostgreSQL instance vs. Managed Cloud RDS | Initial development velocity vs. operational cloud hosting overhead. |
