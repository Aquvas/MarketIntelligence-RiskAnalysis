# Data Requirements

## 1. Overview
This document specifies the data requirements and ingestion strategy for the **AI-Powered Market Intelligence and Predictive Business Risk Analysis Platform**.

The platform is designed to assist market and business intelligence analysts by proactively identifying impending market-stress events in the semiconductor industry. The initial machine learning task focuses on a binary classification problem: predicting whether a semiconductor stock will experience a significant downturn—provisionally parameterized as a **$\ge$ 5% decline over the subsequent 10 trading days**—evaluated at daily market close.

To maintain engineering discipline, high predictive reliability, and verifiable reproducibility, the Minimum Viable Product (MVP) data scope is restricted exclusively to historical daily price and volume data alongside core market and sector benchmarks. All advanced, unstructured, and fundamental sources are formally cataloged as future enhancements. A rigorous point-in-time design is enforced across the pipeline to prevent look-ahead bias.

---

## 2. Required Historical Price and Volume Data

### 2.1 Target Asset Coverage
The MVP focuses on five major semiconductor companies representing distinct segments of the semiconductor value chain (fabless design, integrated device manufacturing, pure-play foundry, and memory/conglomerate):
- **NVIDIA Corporation (NVDA)** — US listed (NASDAQ)
- **Advanced Micro Devices, Inc. (AMD)** — US listed (NASDAQ)
- **Intel Corporation (INTC)** — US listed (NASDAQ)
- **Taiwan Semiconductor Manufacturing Company (TSM)** — US-listed American Depositary Receipt (ADR) on NYSE; primary listing on TWSE (2330.TW)
- **Samsung Electronics Co., Ltd. (005930.KS)** — Korea Exchange (KRX); Global Depositary Receipts (GDRs) trade on OTC/LSE

### 2.2 Core OHLCV Fields and Adjusted Prices
Accurate price return calculations and volatility measures require both unadjusted trading data (for true intraday ranges and trade volumes) and corporate-action-adjusted prices (for continuous return series without artificial gaps from splits or cash dividends).

| Field | Description | Purpose |
|---|---|---|
| `Date` | Trading date (ISO 8601: `YYYY-MM-DD`) | Primary temporal index |
| `Open` | Regular-session opening price | Intraday range and gap features (Open vs. previous Close) |
| `High` | Highest traded price during regular session | True range, high-low volatility, and technical breakout indicators |
| `Low` | Lowest traded price during regular session | True range, downside volatility, and tail-risk indicators |
| `Close` | Official regular-session closing price | Intraday price movement and baseline for raw returns |
| `Adj Close` | Closing price adjusted for stock splits and dividend distributions | Accurate, continuous multi-day return and drawdown calculation |
| `Volume` | Total number of shares traded during regular session | Liquidity tracking, volume surges, and volume-weighted indicators |

### 2.3 History Window Tradeoffs
Selecting the historical training and evaluation window involves critical tradeoffs:

- **Extended History (e.g., 15–20+ Years):**
  - *Pros:* Captures multiple complete macroeconomic and market cycles (2008 Global Financial Crisis, 2018 tech/crypto cyclical pullback, 2020 COVID-19 shock, 2022 inflationary drawdown), providing more instances of rare market-stress events for model training.
  - *Cons:* Structural industry shifts reduce older data relevance. The semiconductor sector in 2005 had vastly different competitive dynamics, gross margin structures, and valuation regimes compared to the modern AI/hyperscale-driven landscape. Moreover, corporate restructuring (e.g., AMD spinning off GlobalFoundries) alters company risk profiles fundamentally.
- **Moderate History (e.g., 5–10 Years):**
  - *Pros:* Preserves regime relevance to modern semiconductor architectures, supply-chain dependencies, and geopolitical tensions while retaining sufficient sample sizes across multiple bull and bear cycles.
  - *Cons:* Relatively few systemic downturn cycles, potentially leading to class imbalance or overfitting to specific recent shocks.
- **MVP Target Recommendation:** A baseline window of **7 to 10 years** of daily data provides an optimal compromise between sample diversity across stress regimes and domain relevance.

---

## 3. Market and Sector Benchmarks

Individual semiconductor equities exhibit substantial co-movement with the broader market and sector-specific risk factors. Incorporating benchmark time series allows models to differentiate idiosyncratic (company-specific) operational stress from systematic (macro or sector-wide) market downturns.

| Benchmark | Ticker / Identifier | Category | Purpose in Model |
|---|---|---|---|
| **S&P 500 Index** | `SPY` (ETF) or `^GSPC` (Index) | Broad Market | Captures overall market beta, macro market sentiment, and equity risk premium |
| **Philadelphia Semiconductor Index** | `^SOX` (Index) or `SOXX` (ETF) | Industry Benchmark | Isolates sector-wide cyclical supply/demand shocks from individual company risk |
| **Cboe Volatility Index** | `^VIX` | Market Volatility | Serves as an aggregate market-wide "fear gauge" and implied volatility indicator |

### Analytic Purpose:
1. **Relative Strength & Beta Decomposition:** Enables calculation of market-adjusted excess returns ($\alpha$) and relative volume surges.
2. **Stress Attribution:** A 5% drop in INTC when the `^SOX` index drops 6% indicates broad industry pressure, whereas a 5% drop when `^SOX` gains 1% signals firm-specific vulnerability.

---

## 4. Future Data Sources (NOT for MVP)

To preserve focus and manage data engineering complexity during MVP development, unstructured, fundamental, and alternative datasets are explicitly deferred to post-MVP development phases.

> [!NOTE]
> The platform team currently makes **no claim of verified API access, commercial licenses, or active subscriptions** for the sources listed below. They represent potential roadmap integration targets.

- **News Headlines and Articles:** Real-time and archival news feeds (Reuters, Bloomberg, Dow Jones) for NLP sentiment analysis, event extraction, and anomaly alerting.
- **SEC Filings & Periodic Reports:** 10-K (annual), 10-Q (quarterly), and 8-K (material events) filings for US issuers, alongside equivalent regulatory disclosures for foreign filers (Form 20-F for TSMC; KRX regulatory filings via DART for Samsung).
- **Earnings Call Transcripts:** Audio recordings and text transcripts for natural language processing of executive tone, forward guidance shifts, and Q&A analyst sentiment.
- **Supply-Chain & Partnership Graph Data:** Multi-tier supplier/customer relationship networks (e.g., ASML lithography equipment dependencies, hyperscaler customer concentrations) for systemic shock propagation modeling.
- **Analyst Ratings and Consensus Estimates:** Upgrades/downgrades, price target revisions, and earnings-per-share (EPS)/revenue consensus variance.
- **Macro-Economic Indicators:** Interest rate benchmarks (Federal Reserve policy rate, 10-year US Treasury yield), foreign exchange rates (USD/TWD, USD/KRW), and semiconductor sales index statistics (e.g., SIA monthly reports).

---

## 5. Proposed Data Fields Summary

The following table provides a comprehensive overview of both MVP and candidate future data fields, categorizing their availability tier and analytical purpose.

| Field Name | Category | Scope Tier | Ingestion Frequency | Analytical Purpose |
|---|---|---|---|---|
| `date` | Market (OHLCV) | MVP | Daily | Temporal index and chronological ordering |
| `open` | Market (OHLCV) | MVP | Daily | Overnight price gap and range calculations |
| `high` | Market (OHLCV) | MVP | Daily | Intraday peak volatility and resistance levels |
| `low` | Market (OHLCV) | MVP | Daily | Intraday trough volatility and support breakdown |
| `close` | Market (OHLCV) | MVP | Daily | Unadjusted closing price for baseline trade metrics |
| `adj_close` | Market (OHLCV) | MVP | Daily | Base for multi-day return and label construction |
| `volume` | Market (OHLCV) | MVP | Daily | Liquidity levels and volume-weighted indicators |
| `sp500_adj_close` | Market Benchmark | MVP | Daily | Macro systematic return baseline |
| `sox_adj_close` | Sector Benchmark | MVP | Daily | Industry sector return baseline |
| `vix_close` | Market Volatility | MVP | Daily | Market-wide risk aversion and volatility regime |
| `news_headline_sentiment` | Unstructured (NLP) | Future | Intra-day / Daily | Quantified tone of public media coverage |
| `sec_filing_risk_factors` | Regulatory / Filings | Future | Quarterly / Annual | Semantic shifts in reported business risk disclosures |
| `earnings_call_tone` | Unstructured (NLP) | Future | Quarterly | Executive confidence and guidance sentiment |
| `supplier_dependency_score` | Graph / Supply Chain | Future | Monthly / Quarterly | Network vulnerability and single-point-of-failure risk |
| `analyst_rating_consensus` | Consensus / Estimates | Future | Daily / Weekly | Market expectation drift and surprise vulnerability |
| `us_10y_yield` | Macroeconomic | Future | Daily | Cost of capital and discount rate pressure |
| `fx_rate_usd_twd` | Macroeconomic (FX) | Future | Daily | Currency impact on TSMC international revenues |
| `fx_rate_usd_krw` | Macroeconomic (FX) | Future | Daily | Currency impact on Samsung international revenues |

---

## 6. Data Availability and Licensing

### 6.1 Data Sources & Access Caveats
- **Free / Community Endpoints (e.g., Yahoo Finance via unofficial packages):**
  - *Feasibility:* Useful for rapid local prototyping and exploratory proof-of-concept modeling.
  - *Risks & Caveats:* Unofficial scrapers and free APIs lack service-level agreements (SLAs), are subject to unannounced rate-limiting or schema breakage, and frequently carry strict Terms of Service (ToS) prohibiting commercial or production usage. No verified corporate API access is assumed.
- **Commercial Market Data Feeds (e.g., Polygon.io, Financial Modeling Prep, Refinitiv, Bloomberg):**
  - *Feasibility:* Provides documented REST/WebSocket APIs, historical corporate action adjustments, and licensing clarity.
  - *Constraints:* Incur ongoing recurring subscription fees; institutional-grade tick or fundamental feeds require significant commercial budgets.

### 6.2 International & Dual-Listing Nuances
- **Samsung Electronics (`005930.KS`):**
  - Trades primarily on the Korea Exchange (KRX) in South Korean Won (KRW).
  - Obtaining clean, reliable free-tier daily data matching US formatting standards can be challenging due to ticker symbology differences and local exchange reporting rules. ADRs/GDRs on European or OTC venues frequently suffer from thin liquidity and wide spreads, making primary KRX data preferred despite internationalization friction.
- **TSMC Dual-Listing (`TSM` vs. `2330.TW`):**
  - TSMC's primary shares trade on the Taiwan Stock Exchange (`2330.TW`) in New Taiwan Dollars (TWD), while its ADRs (`TSM`) trade on the New York Stock Exchange (NYSE) in USD.
  - For consistency with US-listed peers (NVDA, AMD, INTC) in the MVP, the **NYSE ADR (`TSM`)** is recommended as the default asset. However, analysts must recognize that ADR pricing can reflect premium/discount variations and currency fluctuations relative to the underlying TWSE listing.

### 6.3 Licensing & Redistribution Compliance
Data ingested into the platform must strictly respect redistribute rights:
- Derived features (e.g., normalized 14-day RSI, volatility indices) may be stored internally, but raw redistributions of licensed time-series feeds to external clients or public repositories are prohibited under standard retail data licenses.

---

## 7. Data Quality Considerations

Data quality directly governs model fidelity and signal reliability. The ingestion pipeline must manage several specific phenomena:

1. **Missing Values, Trading Halts, and Holidays:**
   - Trading halts due to regulatory scrutiny or pending material news releases create gaps in continuous time series.
   - Distinct national holidays (e.g., US Thanksgiving vs. Korean Chuseok vs. Taiwanese Lunar New Year) result in calendar mismatches where some target stocks trade while others are closed.
2. **Corporate Actions & Dividends:**
   - Stock splits (such as NVIDIA's 10-for-1 split in June 2024 or 4-for-1 split in July 2021) create artificial order-of-magnitude price drops if unadjusted.
   - Raw `Close` must never be used for continuous percentage return calculation across corporate action boundaries; split- and dividend-adjusted series must be strictly verified.
3. **Survivorship Bias:**
   - The current selection of five leading semiconductor firms (NVDA, AMD, INTC, TSM, Samsung) represents market survivors with multi-decade resilience.
   - Models trained strictly on successful incumbent mega-caps may overestimate recovery potential and underestimate tail-risk failure modes compared to broader industry cross-sections.
4. **Time Zone Divergences:**
   - Samsung trades in Korea Standard Time (KST, UTC+9).
   - TSMC primary shares trade in Taiwan Standard Time (TST, UTC+8), whereas TSM ADRs trade in Eastern Time (ET, UTC-5/UTC-4).
   - US stocks trade in Eastern Time (ET).
   - *Impact:* KST trading concludes before the US regular session begins on the same calendar day. Using Samsung's Monday close as a co-feature for NVIDIA's Monday close involves asynchronous market information arrival that must be clearly documented.
5. **Data Frequency Alignment:**
   - Daily bars represent the aggregate of different trading hours across exchanges. Standardizing calendar timestamps across time zones without corrupting sequence causality is required for unified feature matrices.

---

## 8. Timestamp and Look-Ahead Bias Prevention

Preventing data leakage (look-ahead bias) is the foremost architectural requirement for the predictive analytics platform.

### 8.1 Strict Prediction Cutoff Discipline
All feature engineering functions applied at time $t$ must operate strictly on information available at or before cutoff timestamp $T_{\text{cutoff}}(t)$:
$$\mathcal{F}_t = f(X_{\le T_{\text{cutoff}}(t)})$$
For daily close prediction:
- $T_{\text{cutoff}}(t)$ is defined as the official regular-market close of day $t$ (e.g., 16:00 ET for US equities).
- Under no circumstances may features incorporate $t+1$ Open, volume, or intraday statistics.

### 8.2 Label Isolation
The provisional target label:
$$Y_t = \mathbb{I}\left(\min_{k \in [1, 10]} \left(\frac{\text{AdjClose}_{t+k} - \text{AdjClose}_t}{\text{AdjClose}_t}\right) \le -0.05\right)$$
is fundamentally forward-looking.
- **Rule:** The target vector $Y$ must be constructed separately from the feature matrix $\mathbf{X}$ and must strictly never be fed, lagged, or normalized alongside input features.
- Cross-validation splits must strictly employ temporal splitting (e.g., expanding-window or rolling-window time-series splits), never randomized K-fold cross-validation.

### 8.3 Point-in-Time Correctness of Adjustments
- Historical adjusted prices published by financial providers adjust past prices retroactively whenever a split or dividend occurs.
- *Risk:* A feature calculated in 2022 using 2024's adjusted price table utilizes a split adjustment factor that was unknown to the market in 2022. While pure price ratios and percentage returns are invariant to split scaling, nominal price-level thresholds (e.g., "price below \$100") would suffer severe distortion.
- *Mitigation:* The pipeline will focus on scale-invariant return, volatility, and volume ratios rather than raw nominal price levels.

### 8.4 Future Data Timestamp Verification
When integrating future unstructured data (news, SEC filings):
- Filings must be stamped with the official public dissemination timestamp (EDGAR acceptance timestamp), not the fiscal period end date.
- News articles must use first-publication timestamps, verifying that updates or post-hoc corrections do not introduce future information into historical evaluation.

---

## 9. Missing Data Strategy

Due to differing international exchange schedules and occasional missing observations, a systematic missing-data protocol is defined:

### 9.1 Multi-Exchange Calendar Reconciliation
- **Baseline Calendar:** The US equity trading calendar (NYSE/NASDAQ) is designated as the primary reference timeline for the MVP model evaluation.
- **Foreign Market Holidays:** When a foreign asset (e.g., Samsung on KRX) is closed on a US trading day:
  - *Strategy:* **Forward Fill (Last Observation Carried Forward - LOCF)** of adjusted closing prices for feature computation, accompanied by a boolean indicator (`is_market_holiday = True`) and a zero-volume marker (`volume = 0`) to prevent false activity signals.
  - Backward filling is strictly prohibited as it constitutes look-ahead leakage.
- **US Market Holidays:** Days when US markets are closed are excluded from the primary prediction dataset, as US targets cannot be evaluated.

### 9.2 History Availability Differences
- If historical data for an asset or benchmark has differing inception dates, the training set must either:
  1. Restrict the initial model training window to the intersection period where all target assets have verified records, or
  2. Train company-specific models using individual ticker history, using global benchmark features only where available.

### 9.3 Imputation vs. Exclusion Policy
- **Price Series:** Never impute missing prices with mean, median, or spline interpolation across multi-day gaps. Use forward-fill only for non-trading days, or exclude corrupted records.
- **Volume Series:** For market holidays where price is carried forward, volume is set to 0. For trading days with missing volume telemetry, forward-fill median volume over a rolling 5-day window or exclude the record if quality thresholds fail.
- **Unrecoverable Gaps:** If an equity has more than 5 consecutive missing trading days without a verified corporate suspension, the entire sequence must be flagged for manual analyst review rather than automated statistical imputation.
