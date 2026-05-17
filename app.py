import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import json
import time
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeEdge Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0e1a;
    color: #e2e8f0;
  }

  .main { background-color: #0a0e1a; }

  h1, h2, h3 { font-family: 'Space Mono', monospace; }

  /* Header */
  .app-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f2027 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .app-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .app-subtitle { color: #64748b; font-size: 0.85rem; margin-top: 4px; }

  /* Metric cards */
  .metric-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #38bdf8; }
  .metric-value { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; }
  .metric-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }

  /* Stock table */
  .stock-row-up { color: #34d399 !important; }
  .stock-row-down { color: #f87171 !important; }

  /* Pill badges */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .badge-green { background: #052e16; color: #34d399; border: 1px solid #166534; }
  .badge-red { background: #2d0b0b; color: #f87171; border: 1px solid #7f1d1d; }
  .badge-blue { background: #0c1a3a; color: #38bdf8; border: 1px solid #1e3a5f; }

  /* Section headers */
  .section-header {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 8px;
    margin: 20px 0 16px 0;
  }

  /* News cards */
  .news-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-left: 3px solid #38bdf8;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: border-left-color 0.2s;
  }
  .news-card:hover { border-left-color: #818cf8; }
  .news-title { font-weight: 600; font-size: 0.9rem; color: #e2e8f0; }
  .news-meta { color: #475569; font-size: 0.75rem; margin-top: 4px; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e293b;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #1e40af);
    color: white;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #6d28d9);
    border-color: #818cf8;
    transform: translateY(-1px);
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #64748b;
  }
  .stTabs [aria-selected="true"] { color: #38bdf8 !important; }

  /* Slider */
  .stSlider [data-baseweb="slider"] { padding: 0; }

  /* File uploader */
  [data-testid="stFileUploader"] {
    border: 1px dashed #1e3a5f !important;
    border-radius: 12px;
    background: #0d1117;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
  }

  /* Info/warning boxes */
  .stAlert { border-radius: 8px; }

  /* Score bar */
  .score-bar-bg {
    background: #1e293b;
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
  }
  .score-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #38bdf8, #34d399);
  }

  /* Hide streamlit branding */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_yahoo_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5d", interval="1d")
        intraday = ticker.history(period="1d", interval="5m")
        return info, hist, intraday
    except Exception as e:
        return {}, pd.DataFrame(), pd.DataFrame()


@st.cache_data(ttl=600)
def fetch_news_rss(query="stock market"):
    articles = []
    feeds = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={query}&region=US&lang=en-US",
        "https://feeds.finance.yahoo.com/rss/2.0/headline?region=US&lang=en-US",
        "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    ]
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", "#"),
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", "Yahoo Finance")
                })
        except:
            pass
    return articles[:20]


@st.cache_data(ttl=900)
def fetch_finviz_news(symbol=""):
    articles = []
    try:
        url = f"https://finviz.com/quote.ashx?t={symbol}" if symbol else "https://finviz.com/news.ashx"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("tr.cursor-pointer") or soup.select(".nn-tab-link")
        for row in rows[:10]:
            a = row.find("a")
            if a:
                articles.append({
                    "title": a.get_text(strip=True),
                    "link": a.get("href", "#"),
                    "published": "",
                    "source": "Finviz"
                })
    except:
        pass
    return articles


@st.cache_data(ttl=3600)
def fetch_earnings_calendar():
    try:
        # Use yfinance for next week's earnings
        today = datetime.today()
        earnings = []
        # Fetch popular tickers earnings
        popular = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "GS", "BAC"]
        for sym in popular:
            try:
                t = yf.Ticker(sym)
                cal = t.calendar
                if cal is not None and not (isinstance(cal, pd.DataFrame) and cal.empty):
                    if isinstance(cal, pd.DataFrame) and "Earnings Date" in cal.index:
                        ed = cal.loc["Earnings Date"].values[0] if len(cal.columns) > 0 else None
                        if ed:
                            earnings.append({"Symbol": sym, "Earnings Date": str(ed)[:10], "EPS Est": cal.loc["EPS Estimate"].values[0] if "EPS Estimate" in cal.index else "N/A"})
                    elif isinstance(cal, dict):
                        ed = cal.get("Earnings Date", [None])[0] if isinstance(cal.get("Earnings Date"), list) else cal.get("Earnings Date")
                        if ed:
                            earnings.append({"Symbol": sym, "Earnings Date": str(ed)[:10], "EPS Est": cal.get("EPS Estimate", "N/A")})
            except:
                pass
        return pd.DataFrame(earnings) if earnings else pd.DataFrame(columns=["Symbol", "Earnings Date", "EPS Est"])
    except:
        return pd.DataFrame(columns=["Symbol", "Earnings Date", "EPS Est"])


def parse_nasdaq_excel(uploaded_file):
    try:
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception:
        uploaded_file.seek(0)   # ← reset pointer before CSV fallback
        try:
            df = pd.read_csv(uploaded_file)
        except pd.errors.EmptyDataError:
            st.error("The uploaded file appears to be empty or unreadable. Please re-download it from NASDAQ and try again.")
            st.stop()
        except Exception as e:
            st.error(f"Could not parse file: {e}")
            st.stop()
    
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    
    # Standardize common column name variants
    rename_map = {}
    for col in df.columns:
        cl = col.lower()
        if "last sale" in cl or "price" in cl or "last" == cl: rename_map[col] = "Last Sale"
        elif "net change" in cl or "change" == cl: rename_map[col] = "Net Change"
        elif "% change" in cl or "pct" in cl: rename_map[col] = "% Change"
        elif "market cap" in cl: rename_map[col] = "Market Cap"
        elif "volume" in cl: rename_map[col] = "Volume"
        elif "symbol" in cl: rename_map[col] = "Symbol"
        elif "name" in cl: rename_map[col] = "Name"
        elif "country" in cl: rename_map[col] = "Country"
        elif "ipo" in cl: rename_map[col] = "IPO Year"
        elif "sector" in cl: rename_map[col] = "Sector"
        elif "industry" in cl: rename_map[col] = "Industry"
    df.rename(columns=rename_map, inplace=True)

    # Clean price column
    for col in ["Last Sale", "Net Change"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("[$,]", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean % Change
    if "% Change" in df.columns:
        df["% Change"] = df["% Change"].astype(str).str.replace("[%,]", "", regex=True)
        df["% Change"] = pd.to_numeric(df["% Change"], errors="coerce")

    # Clean Volume
    if "Volume" in df.columns:
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

    # Clean Market Cap
    if "Market Cap" in df.columns:
        df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors="coerce")

    df.dropna(subset=["Symbol"], inplace=True)
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    return df


def compute_momentum_score(row):
    score = 0
    pct = row.get("% Change", 0) or 0
    vol = row.get("Volume", 0) or 0

    # % change contribution (0-40 points)
    score += min(max(pct * 4, -40), 40)

    # Volume contribution (0-30 points) — raw heuristic
    if vol > 5_000_000: score += 30
    elif vol > 1_000_000: score += 20
    elif vol > 500_000: score += 10
    elif vol > 100_000: score += 5

    # Positive change bonus
    if pct > 5: score += 20
    elif pct > 2: score += 10
    elif pct > 0: score += 5

    # Normalize 0-100
    score = min(max(score, 0), 100)
    return round(score, 1)


def format_market_cap(val):
    try:
        val = float(val)
        if val >= 1e12: return f"${val/1e12:.2f}T"
        if val >= 1e9: return f"${val/1e9:.2f}B"
        if val >= 1e6: return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"
    except:
        return "N/A"


def color_pct(val):
    try:
        v = float(val)
        if v > 0: return f"🟢 +{v:.2f}%"
        if v < 0: return f"🔴 {v:.2f}%"
        return f"⬜ 0.00%"
    except:
        return "—"


# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 TradeEdge Pro")
    st.markdown("*Intraday Intelligence Platform*")
    st.markdown("---")

    st.markdown("### 📂 Today's Data")
    today_file = st.file_uploader(
        "Upload Today's NASDAQ Excel",
        type=["xlsx", "csv"],
        key="today_upload",
        help="Download from nasdaq.com/market-activity/stocks/screener"
    )

    st.markdown("### 📂 Previous Day (Optional)")
    prev_file = st.file_uploader(
        "Upload Yesterday's NASDAQ Excel",
        type=["xlsx", "csv"],
        key="prev_upload",
        help="For day-over-day comparison"
    )

    st.markdown("---")
    st.markdown("### 🔍 Price Filter")
    price_range = st.slider("Price Range ($)", 0.0, 500.0, (10.0, 50.0), step=0.5)
    
    col1, col2 = st.columns(2)
    with col1:
        manual_min = st.number_input("Min $", value=price_range[0], step=1.0)
    with col2:
        manual_max = st.number_input("Max $", value=price_range[1], step=1.0)

    effective_min = manual_min
    effective_max = manual_max

    st.markdown("---")
    st.markdown("### ⚙️ Filters")
    min_volume = st.number_input("Min Volume", value=100_000, step=50_000, format="%d")
    min_change = st.slider("Min % Change", -20.0, 20.0, -100.0)
    
    sectors_available = []
    selected_sectors = []

    st.markdown("---")
    st.markdown("### 🕐 Auto Refresh")
    auto_refresh = st.checkbox("Auto-refresh every 5 min", value=False)
    if auto_refresh:
        time.sleep(300)
        st.rerun()

    st.markdown("---")
    st.caption("Data: Yahoo Finance • NASDAQ • Finviz\nFree & Open Source Stack")


# ─── MAIN HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div>
    <div class="app-title">📈 TradeEdge Pro</div>
    <div class="app-subtitle">Intraday Stock Intelligence · Powered by Yahoo Finance & NASDAQ</div>
  </div>
  <div style="text-align:right; color:#475569; font-family:'Space Mono',monospace; font-size:0.8rem;">
    """ + datetime.now().strftime("%A, %B %d %Y  |  %H:%M") + """
  </div>
</div>
""", unsafe_allow_html=True)


# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠  Dashboard",
    "🔬  Stock Analyzer",
    "📊  Day Comparison",
    "📰  Market News",
    "📅  Earnings Calendar"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if today_file is None:
        st.markdown("""
        <div style="text-align:center; padding:60px 0;">
          <div style="font-size:3rem; margin-bottom:16px;">📂</div>
          <div style="font-family:'Space Mono',monospace; font-size:1.2rem; color:#38bdf8; margin-bottom:8px;">Upload Today's NASDAQ Excel to Begin</div>
          <div style="color:#475569; font-size:0.9rem;">Download from: nasdaq.com/market-activity/stocks/screener</div>
          <br/>
          <div style="color:#475569; font-size:0.8rem;">Supports .xlsx and .csv formats</div>
        </div>
        """, unsafe_allow_html=True)

        # Show live market indices while waiting
        st.markdown('<div class="section-header">📡 Live Market Pulse</div>', unsafe_allow_html=True)
        idx_cols = st.columns(4)
        indices = ["^GSPC", "^DJI", "^IXIC", "^VIX"]
        idx_names = ["S&P 500", "Dow Jones", "NASDAQ", "VIX"]
        
        for i, (sym, name) in enumerate(zip(indices, idx_names)):
            with idx_cols[i]:
                try:
                    t = yf.Ticker(sym)
                    hist = t.history(period="2d")
                    if len(hist) >= 2:
                        curr = hist["Close"].iloc[-1]
                        prev = hist["Close"].iloc[-2]
                        chg = ((curr - prev) / prev) * 100
                        color = "#34d399" if chg >= 0 else "#f87171"
                        st.markdown(f"""
                        <div class="metric-card">
                          <div class="metric-label">{name}</div>
                          <div class="metric-value" style="color:{color}">{curr:,.2f}</div>
                          <div style="color:{color}; font-size:0.8rem; font-family:'Space Mono',monospace;">
                            {'▲' if chg >= 0 else '▼'} {abs(chg):.2f}%
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                except:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">{name}</div><div style="color:#475569">Loading...</div></div>', unsafe_allow_html=True)
    else:
        # Parse uploaded file
        df = parse_nasdaq_excel(today_file)
        
        # Apply filters
        filtered = df.copy()
        if "Last Sale" in filtered.columns:
            filtered = filtered[
                (filtered["Last Sale"] >= effective_min) &
                (filtered["Last Sale"] <= effective_max)
            ]
        if "Volume" in filtered.columns:
            filtered = filtered[filtered["Volume"].fillna(0) >= min_volume]
        if "% Change" in filtered.columns and min_change > -100:
            filtered = filtered[filtered["% Change"].fillna(0) >= min_change]

        # Sector filter
        if "Sector" in df.columns:
            all_sectors = sorted(df["Sector"].dropna().unique().tolist())
            if all_sectors:
                st.sidebar.markdown("### 🏭 Sectors")
                selected_sectors = st.sidebar.multiselect("Filter Sectors", all_sectors, default=[])
                if selected_sectors:
                    filtered = filtered[filtered["Sector"].isin(selected_sectors)]

        # Compute momentum score
        filtered["Momentum Score"] = filtered.apply(compute_momentum_score, axis=1)
        filtered = filtered.sort_values("Momentum Score", ascending=False)

        # ── KPI METRICS
        st.markdown('<div class="section-header">📊 Today\'s Summary</div>', unsafe_allow_html=True)
        k1, k2, k3, k4, k5 = st.columns(5)
        
        total = len(filtered)
        gainers = len(filtered[filtered["% Change"].fillna(0) > 0]) if "% Change" in filtered.columns else 0
        losers = len(filtered[filtered["% Change"].fillna(0) < 0]) if "% Change" in filtered.columns else 0
        avg_chg = filtered["% Change"].fillna(0).mean() if "% Change" in filtered.columns else 0
        top_gainer = filtered.nlargest(1, "% Change").iloc[0]["Symbol"] if "% Change" in filtered.columns and len(filtered) > 0 else "—"

        for col, val, label, color in [
            (k1, str(total), "Stocks in Range", "#38bdf8"),
            (k2, str(gainers), "Gainers 🟢", "#34d399"),
            (k3, str(losers), "Losers 🔴", "#f87171"),
            (k4, f"{avg_chg:+.2f}%", "Avg % Change", "#34d399" if avg_chg >= 0 else "#f87171"),
            (k5, top_gainer, "Top Gainer", "#818cf8"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-label">{label}</div>
                  <div class="metric-value" style="color:{color}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # ── CHARTS ROW
        ch1, ch2 = st.columns([3, 2])

        with ch1:
            st.markdown('<div class="section-header">📈 % Change Distribution</div>', unsafe_allow_html=True)
            if "% Change" in filtered.columns and len(filtered) > 0:
                fig = go.Figure()
                chg_vals = filtered["% Change"].dropna()
                fig.add_trace(go.Histogram(
                    x=chg_vals,
                    nbinsx=40,
                    marker=dict(
                        color=chg_vals.apply(lambda x: "rgba(52,211,153,0.7)" if x >= 0 else "rgba(248,113,113,0.7)"),
                        line=dict(width=0.5, color="#0a0e1a")
                    ),
                    hovertemplate="Range: %{x:.1f}%<br>Count: %{y}<extra></extra>"
                ))
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="% Change",
                    yaxis_title="# Stocks",
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=0),
                    font=dict(family="DM Sans", color="#94a3b8"),
                    showlegend=False
                )
                fig.update_xaxes(gridcolor="#1e293b", zeroline=True, zerolinecolor="#334155")
                fig.update_yaxes(gridcolor="#1e293b")
                st.plotly_chart(fig, use_container_width=True)

        with ch2:
            st.markdown('<div class="section-header">🏭 Sector Breakdown</div>', unsafe_allow_html=True)
            if "Sector" in filtered.columns and len(filtered) > 0:
                sec_counts = filtered["Sector"].dropna().value_counts().head(8)
                fig2 = go.Figure(go.Bar(
                    x=sec_counts.values,
                    y=sec_counts.index,
                    orientation="h",
                    marker=dict(
                        color=sec_counts.values,
                        colorscale=[[0, "#1e3a5f"], [1, "#38bdf8"]],
                        showscale=False,
                    ),
                    hovertemplate="%{y}: %{x} stocks<extra></extra>"
                ))
                fig2.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=0),
                    font=dict(family="DM Sans", color="#94a3b8"),
                    yaxis=dict(autorange="reversed")
                )
                fig2.update_xaxes(gridcolor="#1e293b")
                fig2.update_yaxes(gridcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No sector data available.")

        # ── TOP MOVERS TABLE
        st.markdown('<div class="section-header">🚀 Top Performers (by Momentum Score)</div>', unsafe_allow_html=True)

        display_cols = [c for c in ["Symbol", "Name", "Last Sale", "% Change", "Net Change", "Volume", "Market Cap", "Sector", "Momentum Score"] if c in filtered.columns]
        top_display = filtered[display_cols].head(50).copy()

        if "% Change" in top_display.columns:
            top_display["Perf"] = top_display["% Change"].apply(color_pct)
        if "Market Cap" in top_display.columns:
            top_display["Mkt Cap"] = top_display["Market Cap"].apply(format_market_cap)
        if "Volume" in top_display.columns:
            top_display["Vol"] = top_display["Volume"].apply(lambda x: f"{x/1e6:.2f}M" if pd.notna(x) and x >= 1e6 else (f"{x/1e3:.0f}K" if pd.notna(x) else "—"))
        if "Last Sale" in top_display.columns:
            top_display["Price"] = top_display["Last Sale"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")

        show_cols = [c for c in ["Symbol", "Name", "Price", "Perf", "Vol", "Mkt Cap", "Sector", "Momentum Score"] if c in top_display.columns]
        st.dataframe(
            top_display[show_cols].reset_index(drop=True),
            use_container_width=True,
            height=420,
            column_config={
                "Momentum Score": st.column_config.ProgressColumn("Momentum", min_value=0, max_value=100, format="%.0f"),
                "Symbol": st.column_config.TextColumn("Symbol"),
                "Perf": st.column_config.TextColumn("% Change"),
            }
        )

        # Download
        csv_data = filtered.to_csv(index=False)
        st.download_button(
            "⬇️ Export Filtered Results (CSV)",
            data=csv_data,
            file_name=f"tradeedge_filtered_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

        # ── SECTOR HEATMAP
        if "Sector" in filtered.columns and "% Change" in filtered.columns:
            st.markdown('<div class="section-header">🗺️ Sector Performance Heatmap</div>', unsafe_allow_html=True)
            sec_perf = filtered.groupby("Sector")["% Change"].agg(["mean", "count"]).reset_index()
            sec_perf.columns = ["Sector", "Avg % Change", "# Stocks"]
            sec_perf = sec_perf.dropna()

            if len(sec_perf) > 0:
                fig3 = go.Figure(go.Treemap(
                    labels=sec_perf["Sector"],
                    values=sec_perf["# Stocks"],
                    parents=[""] * len(sec_perf),
                    customdata=sec_perf[["Avg % Change", "# Stocks"]],
                    texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
                    hovertemplate="<b>%{label}</b><br>Avg Change: %{customdata[0]:.2f}%<br>Stocks: %{customdata[1]}<extra></extra>",
                    marker=dict(
                    colors=sec_perf["Avg % Change"],
                    colorscale=[[0, "#7f1d1d"], [0.5, "#1e293b"], [1, "#052e16"]],
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Avg %", font=dict(color="#94a3b8")),
                        tickfont=dict(color="#94a3b8")
                    )
                )
                ))
                fig3.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=350,
                    margin=dict(l=0, r=0, t=10, b=0),
                    font=dict(family="DM Sans", color="#94a3b8")
                )
                st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — STOCK ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">🔬 Deep Dive Stock Analyzer</div>', unsafe_allow_html=True)
    
    sa_col1, sa_col2, sa_col3 = st.columns([2, 1, 1])
    with sa_col1:
        symbol_input = st.text_input("Enter Stock Symbol", placeholder="e.g. AAPL, TSLA, NVDA", value="").upper().strip()
    with sa_col2:
        period_choice = st.selectbox("Chart Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=1)
    with sa_col3:
        interval_map = {"1d": "5m", "5d": "15m", "1mo": "1d", "3mo": "1d", "6mo": "1wk", "1y": "1wk"}
        st.markdown("<br/>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze", use_container_width=True)

    if symbol_input and analyze_btn:
        with st.spinner(f"Fetching data for {symbol_input}..."):
            info, hist_daily, intraday = fetch_yahoo_fundamentals(symbol_input)

            try:
                ticker = yf.Ticker(symbol_input)
                chart_hist = ticker.history(period=period_choice, interval=interval_map.get(period_choice, "1d"))
            except:
                chart_hist = pd.DataFrame()

        if not chart_hist.empty:
            # ── FUNDAMENTALS ROW
            st.markdown(f"### {info.get('longName', symbol_input)} ({symbol_input})")
            st.markdown(f"*{info.get('sector', '')} · {info.get('industry', '')}*")
            
            curr_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            prev_close = info.get("previousClose", 0)
            day_chg = ((curr_price - prev_close) / prev_close * 100) if prev_close else 0
            
            f1, f2, f3, f4, f5, f6 = st.columns(6)
            metrics = [
                (f1, "Price", f"${curr_price:.2f}" if curr_price else "N/A", "#38bdf8"),
                (f2, "Day Change", f"{day_chg:+.2f}%", "#34d399" if day_chg >= 0 else "#f87171"),
                (f3, "P/E Ratio", str(round(info.get("trailingPE", 0) or 0, 1)), "#818cf8"),
                (f4, "Market Cap", format_market_cap(info.get("marketCap", 0)), "#94a3b8"),
                (f5, "52W High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}", "#34d399"),
                (f6, "52W Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}", "#f87171"),
            ]
            for col, label, val, color in metrics:
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                      <div class="metric-label">{label}</div>
                      <div class="metric-value" style="color:{color}; font-size:1.2rem">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # ── CANDLESTICK + VOLUME CHART
            fig_candle = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.75, 0.25]
            )

            fig_candle.add_trace(go.Candlestick(
                x=chart_hist.index,
                open=chart_hist["Open"],
                high=chart_hist["High"],
                low=chart_hist["Low"],
                close=chart_hist["Close"],
                name="Price",
                increasing=dict(fillcolor="#34d399", line=dict(color="#34d399")),
                decreasing=dict(fillcolor="#f87171", line=dict(color="#f87171")),
                hovertext=chart_hist["Close"].apply(lambda x: f"${x:.2f}"),
            ), row=1, col=1)

            # Add 20-period MA
            if len(chart_hist) > 20:
                ma20 = chart_hist["Close"].rolling(20).mean()
                fig_candle.add_trace(go.Scatter(
                    x=chart_hist.index, y=ma20,
                    mode="lines", name="MA20",
                    line=dict(color="#f59e0b", width=1.5, dash="dot"),
                    hovertemplate="MA20: $%{y:.2f}<extra></extra>"
                ), row=1, col=1)

            # Volume bars
            vol_colors = ["#34d399" if c >= o else "#f87171"
                         for c, o in zip(chart_hist["Close"], chart_hist["Open"])]
            fig_candle.add_trace(go.Bar(
                x=chart_hist.index,
                y=chart_hist["Volume"],
                name="Volume",
                marker_color=vol_colors,
                opacity=0.7,
                hovertemplate="Vol: %{y:,.0f}<extra></extra>"
            ), row=2, col=1)

            fig_candle.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(14,20,35,1)",
                height=520,
                margin=dict(l=0, r=0, t=30, b=0),
                font=dict(family="DM Sans", color="#94a3b8"),
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", y=1.05, x=0),
                title=dict(text=f"{symbol_input} — {period_choice.upper()} Chart", font=dict(family="Space Mono", color="#38bdf8"))
            )
            fig_candle.update_xaxes(gridcolor="#1e293b", showgrid=True)
            fig_candle.update_yaxes(gridcolor="#1e293b", showgrid=True)
            st.plotly_chart(fig_candle, use_container_width=True)

            # ── FUNDAMENTALS DETAIL
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.markdown('<div class="section-header">📋 Key Fundamentals</div>', unsafe_allow_html=True)
                fund_data = {
                    "EPS (TTM)": info.get("trailingEps", "N/A"),
                    "Forward P/E": info.get("forwardPE", "N/A"),
                    "PEG Ratio": info.get("pegRatio", "N/A"),
                    "Beta": info.get("beta", "N/A"),
                    "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get("dividendYield") else "N/A",
                    "Profit Margin": f"{info.get('profitMargins', 0) * 100:.1f}%" if info.get("profitMargins") else "N/A",
                    "Revenue (TTM)": format_market_cap(info.get("totalRevenue", 0)),
                    "Debt/Equity": round(info.get("debtToEquity", 0) or 0, 2),
                    "ROE": f"{info.get('returnOnEquity', 0) * 100:.1f}%" if info.get("returnOnEquity") else "N/A",
                    "Free Cash Flow": format_market_cap(info.get("freeCashflow", 0)),
                }
                fund_df = pd.DataFrame(list(fund_data.items()), columns=["Metric", "Value"])
                st.dataframe(fund_df, use_container_width=True, hide_index=True, height=350)

            with detail_col2:
                st.markdown('<div class="section-header">📰 Company News</div>', unsafe_allow_html=True)
                news = fetch_finviz_news(symbol_input)
                yf_news = []
                try:
                    yf_news_raw = yf.Ticker(symbol_input).news
                    for n in (yf_news_raw or [])[:6]:
                        title = n.get("title", "") if isinstance(n, dict) else ""
                        link = n.get("link", "#") if isinstance(n, dict) else "#"
                        if title:
                            yf_news.append({"title": title, "link": link, "source": "Yahoo Finance", "published": ""})
                except:
                    pass
                all_news = (yf_news + news)[:8]
                
                if all_news:
                    for article in all_news:
                        st.markdown(f"""
                        <div class="news-card">
                          <a href="{article['link']}" target="_blank" style="text-decoration:none">
                            <div class="news-title">{article['title'][:120]}...</div>
                          </a>
                          <div class="news-meta">{article['source']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No news found for this symbol.")

            # ── AI SENTIMENT ANALYSIS
            st.markdown('<div class="section-header">🤖 AI Sentiment & Signal Analysis</div>', unsafe_allow_html=True)
            
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            
            try:
                ai_col1, ai_col2, ai_col3 = st.columns(3)
                
                # Sentiment from news headlines
                headlines = [a["title"] for a in all_news if a.get("title")]
                if headlines:
                    compound_scores = [analyzer.polarity_scores(h)["compound"] for h in headlines]
                    avg_sentiment = np.mean(compound_scores)
                    sentiment_label = "BULLISH 📈" if avg_sentiment > 0.05 else ("BEARISH 📉" if avg_sentiment < -0.05 else "NEUTRAL ⬜")
                    sentiment_color = "#34d399" if avg_sentiment > 0.05 else ("#f87171" if avg_sentiment < -0.05 else "#94a3b8")
                else:
                    avg_sentiment, sentiment_label, sentiment_color = 0, "NEUTRAL ⬜", "#94a3b8"
                
                with ai_col1:
                    st.markdown(f"""
                    <div class="metric-card">
                      <div class="metric-label">News Sentiment</div>
                      <div class="metric-value" style="color:{sentiment_color}; font-size:1rem">{sentiment_label}</div>
                      <div style="color:#64748b; font-size:0.75rem">Score: {avg_sentiment:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # RSI Calculation
                if len(chart_hist) > 14:
                    delta = chart_hist["Close"].diff()
                    gain = delta.clip(lower=0).rolling(14).mean()
                    loss = (-delta.clip(upper=0)).rolling(14).mean()
                    rs = gain / loss
                    rsi = (100 - (100 / (1 + rs))).iloc[-1]
                    rsi_label = "OVERBOUGHT" if rsi > 70 else ("OVERSOLD" if rsi < 30 else "NEUTRAL")
                    rsi_color = "#f87171" if rsi > 70 else ("#34d399" if rsi < 30 else "#94a3b8")
                else:
                    rsi, rsi_label, rsi_color = 50, "N/A", "#94a3b8"

                with ai_col2:
                    st.markdown(f"""
                    <div class="metric-card">
                      <div class="metric-label">RSI (14)</div>
                      <div class="metric-value" style="color:{rsi_color}">{rsi:.1f}</div>
                      <div style="color:{rsi_color}; font-size:0.75rem">{rsi_label}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Volume signal
                if len(chart_hist) > 10:
                    avg_vol = chart_hist["Volume"].rolling(10).mean().iloc[-1]
                    curr_vol = chart_hist["Volume"].iloc[-1]
                    vol_ratio = curr_vol / avg_vol if avg_vol else 1
                    vol_signal = f"🔥 {vol_ratio:.1f}x Avg" if vol_ratio > 1.5 else ("Normal" if vol_ratio > 0.8 else "Low")
                    vol_color = "#f59e0b" if vol_ratio > 1.5 else "#94a3b8"
                else:
                    vol_signal, vol_color = "N/A", "#94a3b8"

                with ai_col3:
                    st.markdown(f"""
                    <div class="metric-card">
                      <div class="metric-label">Volume Signal</div>
                      <div class="metric-value" style="color:{vol_color}; font-size:1rem">{vol_signal}</div>
                      <div style="color:#64748b; font-size:0.75rem">vs 10-period avg</div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.warning(f"AI analysis error: {str(e)}")
        else:
            st.error(f"No data found for symbol: {symbol_input}. Please check the symbol and try again.")
    elif not analyze_btn:
        st.info("💡 Enter a stock symbol above and click **Analyze** to get a full deep-dive with fundamentals, charts, and AI signals.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DAY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">📊 Day-Over-Day Comparison</div>', unsafe_allow_html=True)
    
    if today_file is None or prev_file is None:
        st.markdown("""
        <div style="text-align:center; padding:40px 0; color:#64748b;">
          <div style="font-size:2.5rem; margin-bottom:12px;">📂</div>
          <div style="font-family:'Space Mono',monospace; color:#38bdf8; margin-bottom:8px;">Upload BOTH Excel files in the sidebar</div>
          <div>Today's file + Yesterday's file required for comparison</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_today = parse_nasdaq_excel(today_file)
        df_prev = parse_nasdaq_excel(prev_file)

        # Merge on Symbol
        merge_cols_t = [c for c in ["Symbol", "Name", "Last Sale", "% Change", "Volume", "Market Cap", "Sector"] if c in df_today.columns]
        merge_cols_p = [c for c in ["Symbol", "Last Sale", "% Change", "Volume"] if c in df_prev.columns]
        
        df_today_m = df_today[merge_cols_t].copy()
        df_prev_m = df_prev[merge_cols_p].copy()
        
        # Rename prev columns
        df_prev_m.rename(columns={
            "Last Sale": "Prev Sale",
            "% Change": "Prev % Change",
            "Volume": "Prev Volume"
        }, inplace=True)

        merged = pd.merge(df_today_m, df_prev_m, on="Symbol", how="inner")

        # Calculate comparison metrics
        if "Last Sale" in merged.columns and "Prev Sale" in merged.columns:
            merged["Price Δ"] = merged["Last Sale"] - merged["Prev Sale"]
            merged["Price Δ%"] = ((merged["Last Sale"] - merged["Prev Sale"]) / merged["Prev Sale"] * 100).round(2)

        if "Volume" in merged.columns and "Prev Volume" in merged.columns:
            merged["Vol Δ%"] = ((merged["Volume"] - merged["Prev Volume"]) / merged["Prev Volume"] * 100).round(1)
        
        # Apply same price filter
        if "Last Sale" in merged.columns:
            merged = merged[
                (merged["Last Sale"] >= effective_min) &
                (merged["Last Sale"] <= effective_max)
            ]

        # Summary
        comp_k1, comp_k2, comp_k3, comp_k4 = st.columns(4)
        for col, val, label, color in [
            (comp_k1, str(len(merged)), "Matched Stocks", "#38bdf8"),
            (comp_k2, str(len(merged[merged["Price Δ%"] > 0])) if "Price Δ%" in merged.columns else "—", "Up from Yesterday", "#34d399"),
            (comp_k3, str(len(merged[merged["Price Δ%"] < 0])) if "Price Δ%" in merged.columns else "—", "Down from Yesterday", "#f87171"),
            (comp_k4, f"{merged['Price Δ%'].mean():+.2f}%" if "Price Δ%" in merged.columns and len(merged) > 0 else "—", "Avg Price Change", "#818cf8"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-label">{label}</div>
                  <div class="metric-value" style="color:{color}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Charts
        if "Price Δ%" in merged.columns and len(merged) > 0:
            comp_c1, comp_c2 = st.columns(2)
            
            with comp_c1:
                st.markdown('<div class="section-header">🏆 Best Performers (2-Day)</div>', unsafe_allow_html=True)
                top10 = merged.nlargest(10, "Price Δ%")[["Symbol", "Last Sale", "Price Δ%", "Vol Δ%"]].copy() if "Price Δ%" in merged.columns else pd.DataFrame()
                if not top10.empty:
                    fig_top = go.Figure(go.Bar(
                        x=top10["Price Δ%"],
                        y=top10["Symbol"],
                        orientation="h",
                        marker=dict(color=top10["Price Δ%"], colorscale=[[0, "#1e3a5f"], [1, "#34d399"]], showscale=False),
                        hovertemplate="<b>%{y}</b><br>2-Day Change: +%{x:.2f}%<extra></extra>"
                    ))
                    fig_top.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=320,
                        margin=dict(l=0, r=0, t=10, b=0),
                        font=dict(family="DM Sans", color="#94a3b8"),
                        yaxis=dict(autorange="reversed")
                    )
                    st.plotly_chart(fig_top, use_container_width=True)

            with comp_c2:
                st.markdown('<div class="section-header">📉 Biggest Decliners (2-Day)</div>', unsafe_allow_html=True)
                bot10 = merged.nsmallest(10, "Price Δ%")[["Symbol", "Last Sale", "Price Δ%"]].copy() if "Price Δ%" in merged.columns else pd.DataFrame()
                if not bot10.empty:
                    fig_bot = go.Figure(go.Bar(
                        x=bot10["Price Δ%"],
                        y=bot10["Symbol"],
                        orientation="h",
                        marker=dict(color=bot10["Price Δ%"], colorscale=[[0, "#f87171"], [1, "#1e3a5f"]], showscale=False),
                        hovertemplate="<b>%{y}</b><br>2-Day Change: %{x:.2f}%<extra></extra>"
                    ))
                    fig_bot.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=320,
                        margin=dict(l=0, r=0, t=10, b=0),
                        font=dict(family="DM Sans", color="#94a3b8"),
                        yaxis=dict(autorange="reversed")
                    )
                    st.plotly_chart(fig_bot, use_container_width=True)

        # Full comparison table
        st.markdown('<div class="section-header">📋 Full Comparison Table</div>', unsafe_allow_html=True)
        show_comp = [c for c in ["Symbol", "Name", "Last Sale", "Prev Sale", "Price Δ", "Price Δ%", "% Change", "Prev % Change", "Vol Δ%", "Sector"] if c in merged.columns]
        st.dataframe(
            merged[show_comp].sort_values("Price Δ%", ascending=False) if "Price Δ%" in merged.columns else merged[show_comp],
            use_container_width=True,
            height=450,
            column_config={
                "Price Δ%": st.column_config.NumberColumn("Price Δ%", format="%.2f%%"),
                "Vol Δ%": st.column_config.NumberColumn("Vol Δ%", format="%.1f%%"),
            }
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MARKET NEWS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📰 Market Intelligence Feed</div>', unsafe_allow_html=True)
    
    news_col1, news_col2 = st.columns([1, 3])
    with news_col1:
        news_category = st.selectbox("Feed Source", ["Yahoo Finance", "General Market", "Tech Stocks", "Custom Symbol"])
    with news_col2:
        if news_category == "Custom Symbol":
            news_symbol = st.text_input("Symbol for News", placeholder="e.g. AAPL").upper()
        else:
            news_symbol = ""

    with st.spinner("Loading news..."):
        if news_category == "Custom Symbol" and news_symbol:
            articles = fetch_finviz_news(news_symbol)
            try:
                yf_news_raw = yf.Ticker(news_symbol).news or []
                yf_articles = [{"title": n.get("title",""), "link": n.get("link","#"), "source": "Yahoo Finance", "published": ""} for n in yf_news_raw if isinstance(n, dict) and n.get("title")]
                articles = yf_articles + articles
            except:
                pass
        else:
            query_map = {"Yahoo Finance": "", "General Market": "market", "Tech Stocks": "tech"}
            articles = fetch_news_rss(query_map.get(news_category, ""))

    if articles:
        n1, n2 = st.columns(2)
        for i, article in enumerate(articles[:20]):
            col = n1 if i % 2 == 0 else n2
            with col:
                title = article.get("title", "")
                link = article.get("link", "#")
                source = article.get("source", "")
                pub = article.get("published", "")

                # Quick sentiment
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                sa = SentimentIntensityAnalyzer()
                sentiment = sa.polarity_scores(title)["compound"]
                sent_badge = '<span class="badge badge-green">BULLISH</span>' if sentiment > 0.05 else ('<span class="badge badge-red">BEARISH</span>' if sentiment < -0.05 else '<span class="badge badge-blue">NEUTRAL</span>')

                if sentiment > 0.05:
                    badge_html = '<span style="display:inline-block;padding:2px 10px;border-radius:999px;font-size:0.75rem;font-weight:600;background:#052e16;color:#34d399;border:1px solid #166534;">BULLISH</span>'
                elif sentiment < -0.05:
                    badge_html = '<span style="display:inline-block;padding:2px 10px;border-radius:999px;font-size:0.75rem;font-weight:600;background:#2d0b0b;color:#f87171;border:1px solid #7f1d1d;">BEARISH</span>'
                else:
                    badge_html = '<span style="display:inline-block;padding:2px 10px;border-radius:999px;font-size:0.75rem;font-weight:600;background:#0c1a3a;color:#38bdf8;border:1px solid #1e3a5f;">NEUTRAL</span>'
                
                pub_html = f'<span>· {pub[:16]}</span>' if pub else ''
            
                st.markdown(f"""
                <div class="news-card">
                  <a href="{link}" target="_blank" style="text-decoration:none">
                    <div class="news-title">{title[:140]}</div>
                  </a>
                  <div class="news-meta" style="display:flex;align-items:center;gap:8px;margin-top:6px;">
                    <span>{source}</span>
                    {pub_html}
                    {badge_html}
                  </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No articles loaded. Check your internet connection.")

    # Fear & Greed alternative — VIX-based
    st.markdown('<div class="section-header">😱 Market Mood (VIX-based)</div>', unsafe_allow_html=True)
    try:
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="1d")
        if not vix_hist.empty:
            vix_val = vix_hist["Close"].iloc[-1]
            if vix_val < 15: mood, mood_color = "EXTREME GREED 🤑", "#34d399"
            elif vix_val < 20: mood, mood_color = "GREED 😊", "#86efac"
            elif vix_val < 25: mood, mood_color = "NEUTRAL 😐", "#94a3b8"
            elif vix_val < 30: mood, mood_color = "FEAR 😟", "#fbbf24"
            else: mood, mood_color = "EXTREME FEAR 😱", "#f87171"
            
            st.markdown(f"""
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:20px; text-align:center; max-width:400px; margin:0 auto;">
              <div style="color:#64748b; font-family:'Space Mono',monospace; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">VIX: {vix_val:.2f}</div>
              <div style="font-family:'Space Mono',monospace; font-size:1.8rem; color:{mood_color}; margin:8px 0;">{mood}</div>
              <div style="color:#475569; font-size:0.8rem;">Based on CBOE Volatility Index</div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("VIX data unavailable.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — EARNINGS CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📅 Earnings Calendar</div>', unsafe_allow_html=True)
    
    ec1, ec2 = st.columns([2, 1])
    with ec1:
        st.markdown("*Upcoming earnings for major stocks — click any symbol to jump to analyzer*")
    with ec2:
        custom_symbols = st.text_input("Add Symbols (comma separated)", placeholder="e.g. AAPL, TSLA, AMZN")

    watch_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "GS", "BAC", "NFLX", "AMD", "INTC", "CRM", "ORCL"]
    if custom_symbols:
        extras = [s.strip().upper() for s in custom_symbols.split(",") if s.strip()]
        watch_list = list(set(watch_list + extras))

    with st.spinner("Fetching earnings data..."):
        earnings_rows = []
        for sym in watch_list[:20]:
            try:
                t = yf.Ticker(sym)
                cal = t.calendar
                info_e = t.info
                
                # Parse calendar
                earnings_date = "N/A"
                eps_est = "N/A"
                rev_est = "N/A"
                
                if cal is not None:
                    if isinstance(cal, pd.DataFrame) and not cal.empty:
                        if "Earnings Date" in cal.index:
                            ed_vals = cal.loc["Earnings Date"].values
                            earnings_date = str(ed_vals[0])[:10] if len(ed_vals) > 0 else "N/A"
                        if "EPS Estimate" in cal.index:
                            eps_vals = cal.loc["EPS Estimate"].values
                            eps_est = f"${float(eps_vals[0]):.2f}" if len(eps_vals) > 0 and eps_vals[0] else "N/A"
                        if "Revenue Estimate" in cal.index:
                            rev_vals = cal.loc["Revenue Estimate"].values
                            rev_est = format_market_cap(rev_vals[0]) if len(rev_vals) > 0 else "N/A"
                    elif isinstance(cal, dict):
                        ed = cal.get("Earnings Date")
                        if isinstance(ed, list) and ed:
                            earnings_date = str(ed[0])[:10]
                        elif ed:
                            earnings_date = str(ed)[:10]
                        eps = cal.get("EPS Estimate")
                        if isinstance(eps, list) and eps:
                            eps_est = f"${float(eps[0]):.2f}" if eps[0] else "N/A"
                        elif eps:
                            eps_est = f"${float(eps):.2f}"
                        rev = cal.get("Revenue Estimate")
                        if isinstance(rev, list) and rev:
                            rev_est = format_market_cap(rev[0]) if rev[0] else "N/A"
                        elif rev:
                            rev_est = format_market_cap(rev)

                curr_p = info_e.get("currentPrice") or info_e.get("regularMarketPrice", 0)
                pe = info_e.get("trailingPE", "N/A")
                
                earnings_rows.append({
                    "Symbol": sym,
                    "Company": info_e.get("shortName", sym),
                    "Price": f"${curr_p:.2f}" if curr_p else "N/A",
                    "Earnings Date": earnings_date,
                    "EPS Estimate": eps_est,
                    "Revenue Estimate": rev_est,
                    "P/E": round(pe, 1) if isinstance(pe, (int, float)) else "N/A",
                    "Sector": info_e.get("sector", "N/A"),
                })
            except:
                earnings_rows.append({
                    "Symbol": sym, "Company": sym, "Price": "N/A",
                    "Earnings Date": "N/A", "EPS Estimate": "N/A",
                    "Revenue Estimate": "N/A", "P/E": "N/A", "Sector": "N/A"
                })

    if earnings_rows:
        earnings_df = pd.DataFrame(earnings_rows)
        st.dataframe(
            earnings_df,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config={
                "Symbol": st.column_config.TextColumn("Symbol"),
                "Company": st.column_config.TextColumn("Company"),
                "Earnings Date": st.column_config.TextColumn("Earnings Date"),
            }
        )
        
        # Earnings date visualization
        valid_dates = earnings_df[earnings_df["Earnings Date"] != "N/A"].copy()
        if not valid_dates.empty:
            try:
                valid_dates["Date"] = pd.to_datetime(valid_dates["Earnings Date"], errors="coerce")
                valid_dates = valid_dates.dropna(subset=["Date"])
                if not valid_dates.empty:
                    valid_dates["Days Until"] = (valid_dates["Date"] - pd.Timestamp.now()).dt.days
                    upcoming = valid_dates[valid_dates["Days Until"].between(-7, 90)].sort_values("Days Until")
                    
                    if not upcoming.empty:
                        st.markdown('<div class="section-header">📅 Upcoming Earnings Timeline</div>', unsafe_allow_html=True)
                        fig_earn = go.Figure()
                        fig_earn.add_trace(go.Scatter(
                            x=upcoming["Date"],
                            y=upcoming["Symbol"],
                            mode="markers+text",
                            marker=dict(size=14, color="#818cf8", symbol="diamond"),
                            text=upcoming["Symbol"],
                            textposition="middle right",
                            hovertemplate="<b>%{y}</b><br>Date: %{x|%b %d, %Y}<extra></extra>"
                        ))
                        fig_earn.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            height=300,
                            margin=dict(l=0, r=100, t=10, b=0),
                            font=dict(family="DM Sans", color="#94a3b8"),
                            xaxis=dict(gridcolor="#1e293b"),
                            yaxis=dict(gridcolor="#1e293b", autorange="reversed")
                        )
                        st.plotly_chart(fig_earn, use_container_width=True)
            except:
                pass
    else:
        st.info("No earnings data available.")

    # Volume anomaly detector (bonus AI feature)
    if today_file is not None:
        st.markdown('<div class="section-header">🔥 Volume Anomaly Detector (AI Signal)</div>', unsafe_allow_html=True)
        df_anom = parse_nasdaq_excel(today_file)
        if "Volume" in df_anom.columns and "Symbol" in df_anom.columns:
            df_anom["Volume"] = pd.to_numeric(df_anom["Volume"], errors="coerce")
            q75 = df_anom["Volume"].quantile(0.75)
            q25 = df_anom["Volume"].quantile(0.25)
            threshold = q75 + 1.5 * (q75 - q25)
            anomalies = df_anom[df_anom["Volume"] > threshold].copy()
            anomalies = anomalies.sort_values("Volume", ascending=False).head(15)
            
            if not anomalies.empty:
                disp_cols = [c for c in ["Symbol", "Name", "Last Sale", "% Change", "Volume", "Sector"] if c in anomalies.columns]
                st.markdown(f"*{len(anomalies)} stocks with unusually high volume detected (IQR outlier method)*")
                st.dataframe(anomalies[disp_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No volume anomalies detected in current data.")
