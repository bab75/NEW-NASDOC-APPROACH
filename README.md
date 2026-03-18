# 📈 TradeEdge Pro — Intraday Stock Intelligence Platform

A beautiful, full-featured Streamlit application for intraday trading analysis.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 📂 How to Use

### Get Today's NASDAQ Data
1. Go to: https://www.nasdaq.com/market-activity/stocks/screener?page=1&rows_per_page=25
2. Click **Download** (top right of the screener table)
3. Upload the downloaded `.xlsx` file in the **sidebar** of the app

### Features

| Tab | What It Does |
|-----|-------------|
| 🏠 Dashboard | Overview of all filtered stocks, momentum scores, sector heatmap |
| 🔬 Stock Analyzer | Deep-dive any symbol — candlestick charts, fundamentals, AI signals |
| 📊 Day Comparison | Upload today + yesterday's files to compare performance |
| 📰 Market News | Live news feed with AI sentiment badges |
| 📅 Earnings Calendar | Upcoming earnings + volume anomaly detector |

---

## 🔍 Key Filters (Sidebar)
- **Price Range Slider** — e.g. $10–$50
- **Manual Min/Max** — type exact values
- **Min Volume** — filter out low-liquidity stocks
- **Min % Change** — focus on movers
- **Sector Filter** — auto-populated from your data

---

## 🤖 AI & Analytics Features
- **Momentum Score** (0–100) — composite of % change + volume signals
- **RSI (14-period)** — overbought/oversold signals
- **Volume Anomaly Detection** — IQR-based statistical outlier detection
- **News Sentiment** — VADER NLP model scores each headline
- **Volume Signal** — compares current volume vs 10-period rolling average

---

## 📡 Data Sources (All Free)
| Source | Used For |
|--------|----------|
| NASDAQ Screener | Daily stock universe |
| Yahoo Finance (yfinance) | Fundamentals, charts, news |
| Finviz | Stock-specific news |
| Yahoo Finance RSS | Market news feed |
| CBOE VIX (via yfinance) | Market mood indicator |

---

## 🛠️ Tech Stack
- **Streamlit** — UI framework
- **yfinance** — Yahoo Finance data
- **Plotly** — Interactive charts with hover
- **VADER Sentiment** — News sentiment NLP
- **Feedparser** — RSS news feeds
- **BeautifulSoup** — Finviz news scraping
- **Pandas / NumPy** — Data processing
- **scikit-learn** — ML foundation (extensible)
