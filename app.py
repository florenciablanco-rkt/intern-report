"""
app.py — Space: Health Check Dashboard · Rocket Lab Space style
"""

import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from datetime import date, timedelta
import calendar

st.set_page_config(
    page_title="Space: Health Check · Rocket Lab",
    page_icon="🚀",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #f0eff5 !important;
    color: #1a1927 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 24px 28px !important; max-width: 1400px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #14131a !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    min-width: 230px !important; max-width: 230px !important;
}
section[data-testid="stSidebar"] * { color: #9997b3 !important; font-family: 'Inter', sans-serif !important; }
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #fff !important; font-size: 11px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.7px !important; margin-bottom: 8px !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #1e1d28 !important; border: 1px solid #252336 !important;
    color: #fff !important; border-radius: 6px !important; font-size: 12px !important;
}
section[data-testid="stSidebar"] .stSelectbox label {
    color: #5a5878 !important; font-size: 10px !important;
    font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.7px !important;
}
section[data-testid="stSidebar"] .stDateInput input {
    background-color: #1e1d28 !important; border: 1px solid #252336 !important;
    color: #fff !important; border-radius: 6px !important; font-size: 12px !important;
}
section[data-testid="stSidebar"] .stDateInput label {
    color: #5a5878 !important; font-size: 10px !important;
    font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.7px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #7c3aed !important; color: #fff !important; border: none !important;
    border-radius: 6px !important; font-size: 12px !important; font-weight: 600 !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: #6d28d9 !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }
section[data-testid="stSidebar"] .stCaption { color: #5a5878 !important; font-size: 10px !important; }
section[data-testid="stSidebar"] .stRadio > div { gap: 6px !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 12px !important; color: #9997b3 !important; }

/* Page title */
h1 { font-size: 20px !important; font-weight: 700 !important; letter-spacing: -0.4px !important; color: #1a1927 !important; margin-bottom: 2px !important; }
h2 { font-size: 14px !important; font-weight: 600 !important; color: #1a1927 !important; margin: 0 !important; }
h3 { font-size: 12px !important; font-weight: 600 !important; color: #9997b3 !important;
     text-transform: uppercase !important; letter-spacing: 0.6px !important; margin: 0 0 12px 0 !important; }

/* Cards */
.card {
    background: #fff; border: 1px solid #e4e2ee; border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06); padding: 16px 18px; margin-bottom: 12px;
}
.card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 12px; border-bottom: 1px solid #f0eff5; margin-bottom: 14px;
}

/* Product badge */
.product-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 4px;
    font-size: 11px; font-weight: 600; white-space: nowrap;
}
.badge-asa    { background: #f5f3ff; color: #7c3aed; }
.badge-net    { background: #eff6ff; color: #2563eb; }
.badge-dsp    { background: #ecfdf5; color: #059669; }
.badge-pai    { background: #fff7ed; color: #ea580c; }
.badge-oemd   { background: #faf5ff; color: #9333ea; }

/* Stat cards */
.stat-grid { display: grid; gap: 10px; margin-bottom: 14px; }
.stat-card {
    background: #fff; border: 1px solid #e4e2ee; border-radius: 8px;
    padding: 12px 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    border-top: 3px solid #e4e2ee;
}
.stat-card.green  { border-top-color: #059669; }
.stat-card.purple { border-top-color: #7c3aed; }
.stat-card.blue   { border-top-color: #2563eb; }
.stat-card.amber  { border-top-color: #d97706; }
.stat-card.red    { border-top-color: #dc2626; }
.stat-card.gray   { border-top-color: #9997b3; }

.stat-label {
    font-size: 10.5px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.6px; color: #9997b3; margin-bottom: 4px;
}
.stat-value { font-size: 20px; font-weight: 700; letter-spacing: -0.4px; color: #1a1927; }
.stat-delta { font-size: 11px; margin-top: 3px; }
.delta-pos  { color: #059669; }
.delta-neg  { color: #dc2626; }
.delta-neu  { color: #9997b3; }

/* Section divider */
.section-divider {
    font-size: 10.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.7px;
    color: #9997b3; padding: 6px 0; border-bottom: 1px solid #e4e2ee; margin: 18px 0 14px;
}

/* Table */
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th {
    background: #f0eff5; padding: 8px 12px; text-align: left;
    font-size: 10.5px; font-weight: 600; color: #9997b3;
    text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e4e2ee;
    white-space: nowrap;
}
td { padding: 8px 12px; border-bottom: 1px solid #f5f3fb; color: #1a1927; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #faf9ff; }

/* Spinner */
.stSpinner > div { border-top-color: #7c3aed !important; }

/* Alert */
.stAlert { border-radius: 6px !important; font-size: 12px !important; }
.stInfo { background: #f5f3ff !important; border-left-color: #7c3aed !important; color: #4c1d95 !important; }

div[data-testid="stAppViewContainer"] { background-color: #f0eff5 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
BQ_PROJECT = "prod-data-461409"
SCOPES = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform",
]

PRODUCT_CONFIG = {
    "Apple Ads": {
        "label":       "ASA",
        "badge_class": "badge-asa",
        "kpis": ["avg_daily_spend", "delivery_pct", "margin_pct",
                 "var_spend", "var_cpc", "var_cpi"],
    },
    "Reach Beyond": {
        "label":       "NET",
        "badge_class": "badge-net",
        "kpis": ["avg_daily_spend", "delivery_pct", "margin_pct",
                 "var_spend", "var_cpi",
                 "clicks", "var_clicks", "q_attr", "var_q_attr",
                 "ctatt", "var_ctatt",
                 "fraud_pct", "var_fraud_pct"],
    },
    "Programmatic Ads": {
        "label":       "DSP",
        "badge_class": "badge-dsp",
        "kpis": ["avg_daily_spend", "delivery_pct", "margin_pct",
                 "var_spend", "var_cpm", "var_cpc", "var_cpi",
                 "q_attr", "var_q_attr",
                 "fraud_pct", "var_fraud_pct",
                 "vta_share", "cta_share"],
    },
    "PAI": {
        "label":       "PAI",
        "badge_class": "badge-pai",
        "kpis": ["avg_daily_spend", "delivery_pct", "margin_pct",
                 "var_spend", "installs", "var_installs"],
    },
    "First Impact Ads": {
        "label":       "OEM Disp",
        "badge_class": "badge-oemd",
        "kpis": ["avg_daily_spend", "delivery_pct", "margin_pct",
                 "var_spend", "var_cpc", "var_cpi",
                 "q_attr", "var_q_attr",
                 "fraud_pct", "var_fraud_pct"],
    },
}

KPI_META = {
    "avg_daily_spend": {"label": "Avg Daily Spend",   "color": "purple", "fmt": "currency"},
    "spend_usd":       {"label": "Spend USD",         "color": "purple", "fmt": "currency"},
    "margin_pct":      {"label": "Margin %",           "color": "green",  "fmt": "pct"},
    "delivery_pct":    {"label": "Delivery %",         "color": "blue",   "fmt": "pct"},
    "var_spend":       {"label": "Δ Spend vs prev",    "color": "gray",   "fmt": "pct_delta"},
    "var_cpc":         {"label": "Δ CPC vs prev",      "color": "gray",   "fmt": "pct_delta"},
    "var_cpi":         {"label": "Δ CPI vs prev",      "color": "gray",   "fmt": "pct_delta"},
    "var_cpm":         {"label": "Δ CPM vs prev",      "color": "gray",   "fmt": "pct_delta"},
    "clicks":          {"label": "Clicks",             "color": "blue",   "fmt": "number"},
    "var_clicks":      {"label": "Δ Clicks vs prev",   "color": "gray",   "fmt": "pct_delta"},
    "q_attr":          {"label": "Q Attr",             "color": "blue",   "fmt": "number"},
    "var_q_attr":      {"label": "Δ Q Attr vs prev",   "color": "gray",   "fmt": "pct_delta"},
    "ctatt":           {"label": "CTAtt ($/attr)",    "color": "blue",   "fmt": "currency"},
    "var_ctatt":       {"label": "Δ CTAtt vs prev",    "color": "gray",   "fmt": "pct_delta"},
    "fraud_pct":       {"label": "% Fraude",           "color": "amber",  "fmt": "pct"},
    "var_fraud_pct":   {"label": "Δ % Fraude vs prev", "color": "gray",   "fmt": "pct_delta"},
    "installs":        {"label": "Installs",           "color": "blue",   "fmt": "number"},
    "var_installs":    {"label": "Δ Installs vs prev", "color": "gray",   "fmt": "pct_delta"},
    "vta_share":       {"label": "VTA Share",          "color": "blue",   "fmt": "pct"},
    "cta_share":       {"label": "CTA Share",          "color": "blue",   "fmt": "pct"},
}

# ── Auth ───────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_bq_client():
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    return bigquery.Client(project=BQ_PROJECT, credentials=creds)

# ── Queries ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_clients():
    bq = get_bq_client()
    q = f"""
        SELECT DISTINCT client_id, client_name
        FROM `{BQ_PROJECT}.marts.space_events_extra_info`
        WHERE date >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY))
          AND client_name IS NOT NULL
        ORDER BY client_name
    """
    return bq.query(q).to_dataframe()

@st.cache_data(ttl=300)
def fetch_health_data(client_id: int, d_start: str, d_end: str, d_prev_start: str, d_prev_end: str):
    bq = get_bq_client()
    q = f"""
    WITH managers AS (
      SELECT
        a.id             AS client_id,
        cs.name          AS cs_manager,
        ops.name         AS ops_manager
      FROM `{BQ_PROJECT}.stg.stg_advertisers` a
      LEFT JOIN `{BQ_PROJECT}.stg.lk_customers_success_managers` cs  ON cs.id  = a.customer_success_manager_id
      LEFT JOIN `{BQ_PROJECT}.stg.lk_adops_managers`             ops ON ops.id = a.adops_manager_id
      WHERE a.deleted_at IS NULL
    ),

    raw AS (
      SELECT
        date,
        agg.client_id,
        agg.client_name,
        agg.product,
        agg.campaign_name,
        SUM(CASE WHEN event_name = 'clicks'      THEN event_count END)                    AS clicks,
        SUM(CASE WHEN event_name = 'impressions' THEN event_count END)                    AS impressions,
        SUM(CASE WHEN event_name = 'install'     THEN event_count END)                    AS installs,
        SUM(CASE WHEN event_name NOT IN ('install','clicks','impressions') THEN event_count END) AS q_attr,
        SUM(client_revenue_usd)   AS revenue_usd,
        SUM(client_spend_usd)     AS spend_usd,
        SUM(budget_pr_usd)        AS budget_pr_usd,
        m.ops_manager,
        m.cs_manager,
        CASE
          WHEN date >= TIMESTAMP('{d_start}') AND date < TIMESTAMP(DATE_ADD(DATE '{d_end}',   INTERVAL 1 DAY)) THEN 'current'
          WHEN date >= TIMESTAMP('{d_prev_start}') AND date < TIMESTAMP(DATE_ADD(DATE '{d_prev_end}', INTERVAL 1 DAY)) THEN 'prev'
        END AS period
      FROM `{BQ_PROJECT}.marts.space_events_extra_info` agg
      LEFT JOIN managers m ON m.client_id = agg.client_id
      WHERE agg.client_id = {client_id}
        AND (
          (date >= TIMESTAMP('{d_start}')      AND date < TIMESTAMP(DATE_ADD(DATE '{d_end}',      INTERVAL 1 DAY)))
          OR (date >= TIMESTAMP('{d_prev_start}') AND date < TIMESTAMP(DATE_ADD(DATE '{d_prev_end}', INTERVAL 1 DAY)))
        )
      GROUP BY ALL
    )

    SELECT
      period,
      product,
      campaign_name,
      ops_manager,
      cs_manager,
      SUM(spend_usd)       AS spend_usd,
      SUM(revenue_usd)     AS revenue_usd,
      SUM(budget_pr_usd)   AS budget_pr_usd,
      SUM(clicks)        AS clicks,
      SUM(impressions)   AS impressions,
      SUM(installs)      AS installs,
      SUM(q_attr)        AS q_attr
    FROM raw
    WHERE period IS NOT NULL
    GROUP BY ALL
    """
    return bq.query(q).to_dataframe()

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_value(val, fmt):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if fmt == "currency":
        return f"${val:,.0f}"
    if fmt == "pct":
        return f"{val:.1f}%"
    if fmt == "pct_delta":
        sign = "+" if val > 0 else ""
        return f"{sign}{val:.1f}%"
    if fmt == "number":
        return f"{val:,.0f}"
    return str(val)

def delta_class(val, fmt, invert=False):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "delta-neu"
    if fmt not in ("pct_delta",):
        return "delta-neu"
    positive_is_good = not invert
    if val > 0:
        return "delta-pos" if positive_is_good else "delta-neg"
    if val < 0:
        return "delta-neg" if positive_is_good else "delta-pos"
    return "delta-neu"

def pct_change(curr, prev):
    if prev and prev != 0:
        return (curr - prev) / abs(prev) * 100
    return None

def compute_kpis(curr_df, prev_df, product, d_start, d_end):
    def s(df, col):
        if col not in df.columns or df.empty:
            return 0
        val = df[col].sum()
        return 0 if pd.isna(val) else val

    n_days = max((d_end - d_start).days + 1, 1)

    c_spend    = s(curr_df, "spend_usd")
    p_spend    = s(prev_df, "spend_usd")
    c_rev      = s(curr_df, "revenue_usd")
    c_budget   = s(curr_df, "budget_pr_usd")
    c_clicks   = s(curr_df, "clicks")
    p_clicks   = s(prev_df, "clicks")
    c_impr     = s(curr_df, "impressions")
    c_inst     = s(curr_df, "installs")
    p_inst     = s(prev_df, "installs")
    c_qattr    = s(curr_df, "q_attr")
    p_qattr    = s(prev_df, "q_attr")

    def safe_div(a, b):
        try:
            b_val = float(b)
            if b_val != 0 and not pd.isna(b_val):
                return float(a) / b_val
        except Exception:
            pass
        return None

    margin     = safe_div((c_rev - c_spend) * 100, c_rev)
    delivery   = safe_div(c_spend * 100, c_budget)
    avg_daily  = c_spend / n_days

    cpc_curr   = safe_div(c_spend, c_clicks)
    cpc_prev   = safe_div(p_spend, p_clicks)
    cpi_curr   = safe_div(c_spend, c_inst)
    cpi_prev   = safe_div(p_spend, p_inst)
    cpm_curr   = safe_div(c_spend * 1000, c_impr)
    cpm_prev   = safe_div(p_spend * 1000, s(prev_df, "impressions"))

    # CTatt = spend / q_attr (cost per attributed event)
    ctatt_curr = safe_div(c_spend, c_qattr)
    ctatt_prev = safe_div(p_spend, p_qattr)

    return {
        "avg_daily_spend": avg_daily,
        "spend_usd":       c_spend,
        "margin_pct":      margin,
        "delivery_pct":    delivery,
        "var_spend":       pct_change(c_spend, p_spend),
        "var_cpc":         pct_change(cpc_curr, cpc_prev),
        "var_cpi":         pct_change(cpi_curr, cpi_prev),
        "var_cpm":         pct_change(cpm_curr, cpm_prev),
        "clicks":          c_clicks,
        "var_clicks":      pct_change(c_clicks, p_clicks),
        "q_attr":          c_qattr,
        "var_q_attr":      pct_change(c_qattr, p_qattr),
        "ctatt":           ctatt_curr,
        "var_ctatt":       pct_change(ctatt_curr, ctatt_prev),
        "fraud_pct":       None,
        "var_fraud_pct":   None,
        "installs":        c_inst,
        "var_installs":    pct_change(c_inst, p_inst),
        "vta_share":       None,
        "cta_share":       None,
    }

def render_product_block(product, curr_df, prev_df, d_start, d_end):
    cfg    = PRODUCT_CONFIG.get(product, {})
    label  = cfg.get("label", product)
    badge  = cfg.get("badge_class", "badge-asa")
    kpis   = cfg.get("kpis", [])
    values = compute_kpis(curr_df, prev_df, product, d_start, d_end)

    n_campaigns = curr_df["campaign_name"].nunique() if not curr_df.empty else 0

    header_html = f"""
    <div class="card-header">
      <div style="display:flex;align-items:center;gap:10px">
        <span class="product-badge {badge}">{label}</span>
        <span style="font-size:12px;color:#6b6887">{n_campaigns} campaign{'s' if n_campaigns != 1 else ''}</span>
      </div>
    </div>
    """

    # Stat cards
    cols_per_row = min(len(kpis), 7)
    stat_html = f'<div class="stat-grid" style="grid-template-columns: repeat({cols_per_row}, 1fr)">'
    for k in kpis:
        meta  = KPI_META.get(k, {"label": k, "color": "gray", "fmt": "number"})
        val   = values.get(k)
        invert = k in ("var_cpc", "var_cpi", "var_cpm", "fraud_pct", "var_fraud_pct")
        color = meta["color"]
        # Override color for delta based on direction
        if meta["fmt"] == "pct_delta" and val is not None:
            good_up = k not in ("var_cpc", "var_cpi", "var_cpm", "var_fraud_pct")
            if val > 0:
                color = "green" if good_up else "red"
            elif val < 0:
                color = "red" if good_up else "green"
            else:
                color = "gray"

        stat_html += f"""
        <div class="stat-card {color}">
          <div class="stat-label">{meta['label']}</div>
          <div class="stat-value">{fmt_value(val, meta['fmt'])}</div>
        </div>"""
    stat_html += "</div>"

    # Margin disclaimer if revenue data is unavailable
    margin_disclaimer = ""
    if values.get("margin_pct") is None:
        margin_disclaimer = """
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:14px;
                    padding:8px 12px;background:#fffbeb;border:1px solid #fde68a;
                    border-radius:6px;font-size:11px;color:#92400e;">
          <span>⚠</span>
          <span><strong>Margin %</strong> is unavailable for this client — it requires revenue data that is not currently reported.</span>
        </div>"""

    # Campaign table — all KPI columns including var_ deltas per campaign
    if not curr_df.empty:
        agg_cols = ["spend_usd", "budget_pr_usd", "clicks", "impressions", "installs", "q_attr", "revenue_usd"]
        grp_curr = curr_df.groupby("campaign_name")[[c for c in agg_cols if c in curr_df.columns]].sum().reset_index()
        grp_prev = prev_df.groupby("campaign_name")[[c for c in agg_cols if c in prev_df.columns]].sum().reset_index() if not prev_df.empty else pd.DataFrame(columns=["campaign_name"] + agg_cols)
        grp = grp_curr.merge(grp_prev, on="campaign_name", how="left", suffixes=("", "_prev"))

        n_days_tbl = max((d_end - d_start).days + 1, 1)

        def safe_tbl_div(a, b):
            try:
                b_val = float(b)
                if b_val != 0 and not __import__("math").isnan(b_val):
                    return float(a) / b_val
            except Exception:
                pass
            return None

        def pct_chg(curr_val, prev_val):
            v = safe_tbl_div((float(curr_val or 0) - float(prev_val or 0)) * 100, float(prev_val or 0))
            if v is None:
                return "—"
            sign = "+" if v > 0 else ""
            return f"{sign}{v:.1f}%"

        def tbl_val(row, k):
            sp   = float(row.get("spend_usd") or 0)
            bud  = float(row.get("budget_pr_usd") or 0)
            cl   = float(row.get("clicks") or 0)
            ins  = float(row.get("installs") or 0)
            qa   = float(row.get("q_attr") or 0)
            rv   = float(row.get("revenue_usd") or 0)
            sp_p = float(row.get("spend_usd_prev") or 0)
            cl_p = float(row.get("clicks_prev") or 0)
            ins_p= float(row.get("installs_prev") or 0)
            qa_p = float(row.get("q_attr_prev") or 0)
            imp  = float(row.get("impressions") or 0)
            imp_p= float(row.get("impressions_prev") or 0)

            cpc      = safe_tbl_div(sp,   cl)
            cpc_p    = safe_tbl_div(sp_p, cl_p)
            cpi      = safe_tbl_div(sp,   ins)
            cpi_p    = safe_tbl_div(sp_p, ins_p)
            cpm      = safe_tbl_div(sp * 1000,   imp)
            cpm_p    = safe_tbl_div(sp_p * 1000, imp_p)
            ctatt    = safe_tbl_div(sp,   qa)
            ctatt_p  = safe_tbl_div(sp_p, qa_p)

            if k == "avg_daily_spend":
                return f"${sp/n_days_tbl:,.0f}"
            if k == "delivery_pct":
                v = safe_tbl_div(sp * 100, bud)
                return f"{v:.1f}%" if v is not None else "—"
            if k == "margin_pct":
                v = safe_tbl_div((rv - sp) * 100, rv)
                return f"{v:.1f}%" if v is not None else "—"
            if k == "clicks":
                return f"{int(cl):,}" if cl else "—"
            if k == "installs":
                return f"{int(ins):,}" if ins else "—"
            if k == "q_attr":
                return f"{int(qa):,}" if qa else "—"
            if k == "ctatt":
                return f"${ctatt:,.2f}" if ctatt is not None else "—"
            if k == "var_spend":
                return pct_chg(sp, sp_p)
            if k == "var_clicks":
                return pct_chg(cl, cl_p)
            if k == "var_installs":
                return pct_chg(ins, ins_p)
            if k == "var_q_attr":
                return pct_chg(qa, qa_p)
            if k == "var_cpc":
                return pct_chg(cpc, cpc_p)
            if k == "var_cpi":
                return pct_chg(cpi, cpi_p)
            if k == "var_cpm":
                return pct_chg(cpm, cpm_p)
            if k == "var_ctatt":
                return pct_chg(ctatt, ctatt_p)
            if k in ("fraud_pct", "var_fraud_pct", "vta_share", "cta_share"):
                return "—"
            return "—"

        th_html = "<th>Space Campaign</th>" + "".join(
            f"<th>{KPI_META.get(k, {}).get('label', k)}</th>" for k in kpis
        )
        tbl_rows = ""
        for _, row in grp.iterrows():
            tds = f"<td>{row['campaign_name']}</td>" + "".join(
                f"<td>{tbl_val(row, k)}</td>" for k in kpis
            )
            tbl_rows += f"<tr>{tds}</tr>"

        table_html = f"""
        <div class="section-divider">By Campaign</div>
        <div style="overflow-x:auto">
        <table>
          <thead><tr>{th_html}</tr></thead>
          <tbody>{tbl_rows}</tbody>
        </table>
        </div>"""
    else:
        table_html = ""

    st.markdown(f'<div class="card">{header_html}{stat_html}{margin_disclaimer}{table_html}</div>', unsafe_allow_html=True)

# ── Period helpers ─────────────────────────────────────────────────────────────
def get_preset_range(preset: str):
    today = date.today()
    if preset == "This month":
        start = today.replace(day=1)
        end   = today
    elif preset == "Last month":
        first = today.replace(day=1)
        end   = first - timedelta(days=1)
        start = end.replace(day=1)
    elif preset == "Last 7 days":
        start = today - timedelta(days=6)
        end   = today
    elif preset == "Last 30 days":
        start = today - timedelta(days=29)
        end   = today
    else:
        start = today.replace(day=1)
        end   = today
    return start, end

def get_prev_range(start: date, end: date):
    delta = (end - start).days + 1
    prev_end   = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=delta - 1)
    return prev_start, prev_end

# ── Main ─────────────────────────────────────────────────────────────────────

# Top header
st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
  <div style="width:30px;height:30px;background:#7c3aed;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0">RL</div>
  <div>
    <div style="font-size:18px;font-weight:700;letter-spacing:-0.4px;color:#1a1927;line-height:1.2">Space: Health Check</div>
    <div style="font-size:11px;color:#9997b3">Client performance overview</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Load clients
clients_df = pd.DataFrame()
try:
    with st.spinner("Loading..."):
        clients_df = fetch_clients()
except Exception as e:
    st.error(f"BQ error: {e}")

# Build client options
client_options = {"— select —": None}
if not clients_df.empty:
    client_options.update({r["client_name"]: r["client_id"] for _, r in clients_df.iterrows()})

# ── Filter bar (dark background)


# Inject CSS to style the filter columns block as a dark card
st.markdown("""
<style>
[data-testid="stHorizontalBlock"]:first-of-type {
    background: #14131a;
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 8px;
}
[data-testid="stHorizontalBlock"]:first-of-type label,
[data-testid="stHorizontalBlock"]:first-of-type p {
    color: #5a5878 !important;
}
[data-testid="stHorizontalBlock"]:first-of-type [data-baseweb="select"] > div {
    background-color: #1e1d28 !important;
    border-color: #252336 !important;
}
[data-testid="stHorizontalBlock"]:first-of-type [data-baseweb="select"] span,
[data-testid="stHorizontalBlock"]:first-of-type [data-baseweb="select"] div {
    color: #ffffff !important;
}
[data-testid="stHorizontalBlock"]:first-of-type svg { fill: #9997b3 !important; }
</style>
""", unsafe_allow_html=True)

f1, f2, f3, f4, f5, f6 = st.columns([2, 1.4, 1.4, 1.2, 1.4, 0.7])

with f1:
    st.markdown('<p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:#5a5878;margin:0 0 4px">Client</p>', unsafe_allow_html=True)
    selected_name = st.selectbox("Client", options=list(client_options.keys()), label_visibility="collapsed", key="sel_client")
    selected_id   = client_options[selected_name]

# If client selected, filter managers to that client only
if selected_id is not None and not clients_df.empty:
    client_row    = clients_df[clients_df["client_id"] == selected_id]
    cs_managers   = ["All"] + [v for v in client_row["cs_manager"].dropna().unique().tolist() if v]
    ops_managers  = ["All"] + [v for v in client_row["ops_manager"].dropna().unique().tolist() if v]
else:
    cs_managers  = ["All"] + sorted(clients_df["cs_manager"].dropna().unique().tolist())  if not clients_df.empty and "cs_manager"  in clients_df.columns else ["All"]
    ops_managers = ["All"] + sorted(clients_df["ops_manager"].dropna().unique().tolist()) if not clients_df.empty and "ops_manager" in clients_df.columns else ["All"]

with f2:
    st.markdown('<p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:#5a5878;margin:0 0 4px">CS Manager</p>', unsafe_allow_html=True)
    selected_cs = st.selectbox("CS Manager", options=cs_managers, label_visibility="collapsed", key="sel_cs")

with f3:
    st.markdown('<p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:#5a5878;margin:0 0 4px">Ops Manager</p>', unsafe_allow_html=True)
    selected_ops = st.selectbox("Ops Manager", options=ops_managers, label_visibility="collapsed", key="sel_ops")

with f4:
    st.markdown('<p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:#5a5878;margin:0 0 4px">Time Frame</p>', unsafe_allow_html=True)
    preset = st.selectbox("Time Frame", ["This month", "Last month", "Last 7 days", "Last 30 days", "Custom"], label_visibility="collapsed", key="sel_preset")

with f5:
    if preset == "Custom":
        st.markdown('<p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:#5a5878;margin:0 0 4px">From / To</p>', unsafe_allow_html=True)
        c_from, c_to = st.columns(2)
        with c_from:
            d_start = st.date_input("From", value=date.today().replace(day=1), label_visibility="collapsed", key="d_from")
        with c_to:
            d_end = st.date_input("To", value=date.today(), label_visibility="collapsed", key="d_to")
    else:
        d_start, d_end = get_preset_range(preset)
        d_prev_start, d_prev_end = get_prev_range(d_start, d_end)
        st.markdown(f'<p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:#5a5878;margin:0 0 4px">Period</p><p style="font-size:12px;font-weight:500;color:#fff;margin:0">{d_start.strftime("%b %d")} – {d_end.strftime("%b %d, %Y")}</p><p style="font-size:10px;color:#5a5878;margin:2px 0 0">vs {d_prev_start.strftime("%b %d")} – {d_prev_end.strftime("%b %d")}</p>', unsafe_allow_html=True)

with f6:
    st.markdown('<p style="font-size:10px;margin:0 0 4px">&nbsp;</p>', unsafe_allow_html=True)
    run = st.button("Run", type="primary", use_container_width=True)



d_prev_start, d_prev_end = get_prev_range(d_start, d_end)

# ── Validation
if selected_id is None and selected_cs == "All" and selected_ops == "All":
    st.markdown("""
    <div style="background:#fff;border:1px solid #e4e2ee;border-radius:8px;padding:40px;text-align:center;margin-top:8px">
      <div style="font-size:28px;margin-bottom:8px">📊</div>
      <div style="font-size:14px;font-weight:600;color:#1a1927">Select a client or manager to start</div>
      <div style="font-size:12px;color:#9997b3;margin-top:4px">Use the filters above and click Run.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not run and "last_df" not in st.session_state:
    st.markdown('<div style="background:#fff;border:1px solid #e4e2ee;border-radius:8px;padding:32px;text-align:center;margin-top:8px"><p style="font-size:12px;color:#9997b3;margin:0">Set your filters above and click <strong>Run</strong> to load data.</p></div>', unsafe_allow_html=True)
    st.stop()

if run:
    client_ids_to_query = []
    if selected_id is not None:
        client_ids_to_query = [selected_id]
    else:
        filtered = clients_df.copy()
        if selected_cs != "All":
            filtered = filtered[filtered["cs_manager"] == selected_cs]
        if selected_ops != "All":
            filtered = filtered[filtered["ops_manager"] == selected_ops]
        client_ids_to_query = filtered["client_id"].tolist()

    if not client_ids_to_query:
        st.warning("No clients match the selected filters.")
        st.stop()

    with st.spinner("Querying BigQuery..."):
        try:
            frames = [fetch_health_data(cid, str(d_start), str(d_end), str(d_prev_start), str(d_prev_end)) for cid in client_ids_to_query]
            df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
            st.session_state["last_df"]    = df
            st.session_state["last_range"] = (d_start, d_end, d_prev_start, d_prev_end)
        except Exception as e:
            st.error(f"Query error: {e}")
            st.stop()

df   = st.session_state["last_df"]
curr = df[df["period"] == "current"]
prev = df[df["period"] == "prev"]

if curr.empty:
    st.warning("No data found for the selected filters and period.")
    st.stop()

# ── Info strip
client_name_display = selected_name if selected_id else (f"CS: {selected_cs}" if selected_cs != "All" else f"Ops: {selected_ops}")
ops_display = curr["ops_manager"].dropna().iloc[0] if not curr["ops_manager"].dropna().empty else "—"
cs_display  = curr["cs_manager"].dropna().iloc[0]  if not curr["cs_manager"].dropna().empty  else "—"

st.markdown(f"""
<div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
  <div style="background:#fff;border:1px solid #e4e2ee;border-radius:6px;padding:8px 14px">
    <div style="color:#9997b3;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px">Client</div>
    <div style="font-weight:600;color:#1a1927;font-size:12px;margin-top:2px">{client_name_display}</div>
  </div>
  <div style="background:#fff;border:1px solid #e4e2ee;border-radius:6px;padding:8px 14px">
    <div style="color:#9997b3;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px">Ops Manager</div>
    <div style="font-weight:500;color:#1a1927;font-size:12px;margin-top:2px">{ops_display}</div>
  </div>
  <div style="background:#fff;border:1px solid #e4e2ee;border-radius:6px;padding:8px 14px">
    <div style="color:#9997b3;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px">CS Manager</div>
    <div style="font-weight:500;color:#1a1927;font-size:12px;margin-top:2px">{cs_display}</div>
  </div>
  <div style="background:#fff;border:1px solid #e4e2ee;border-radius:6px;padding:8px 14px">
    <div style="color:#9997b3;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px">Period</div>
    <div style="font-weight:500;color:#1a1927;font-size:12px;margin-top:2px">{d_start.strftime("%b %d")} – {d_end.strftime("%b %d, %Y")}</div>
  </div>
  <div style="background:#fff;border:1px solid #e4e2ee;border-radius:6px;padding:8px 14px">
    <div style="color:#9997b3;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px">Compare to</div>
    <div style="font-weight:500;color:#1a1927;font-size:12px;margin-top:2px">{d_prev_start.strftime("%b %d")} – {d_prev_end.strftime("%b %d, %Y")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Products
products_in_data = curr["product"].dropna().unique().tolist()
ordered_products = [p for p in PRODUCT_CONFIG if p in products_in_data]
ordered_products += [p for p in products_in_data if p not in PRODUCT_CONFIG]

if not ordered_products:
    st.warning("No product data found for this client.")
    st.stop()

for product in ordered_products:
    curr_p = curr[curr["product"] == product]
    prev_p = prev[prev["product"] == product]
    render_product_block(product, curr_p, prev_p, d_start, d_end)
