import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="RiskPulse | Credit Portfolio Intelligence",
    page_icon="📊",
    layout="wide",
)

REQUIRED_COLUMNS = {
    "client_id",
    "contract_id",
    "segment",
    "region",
    "debt",
    "monthly_income",
    "profitability",
    "days_past_due",
    "credit_score",
    "collateral_value",
}


def generate_sample_data(n: int = 800, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    segments = rng.choice(
        ["Mass", "Premium", "SME", "Mortgage", "Car loans"],
        size=n,
        p=[0.35, 0.18, 0.17, 0.18, 0.12],
    )
    regions = rng.choice(
        ["Moscow", "Saint Petersburg", "Volga", "Ural", "Siberia", "South", "Far East"],
        size=n,
        p=[0.24, 0.13, 0.18, 0.13, 0.13, 0.13, 0.06],
    )

    monthly_income = rng.lognormal(mean=11.1, sigma=0.45, size=n).round(0)
    debt_multiplier = rng.uniform(1.5, 12.5, size=n)
    debt = (monthly_income * debt_multiplier).round(0)

    dpd_base = rng.choice([0, 0, 0, 3, 7, 15, 31, 45, 60, 90], size=n)
    dpd_noise = rng.integers(0, 8, size=n)
    days_past_due = np.maximum(0, dpd_base + dpd_noise - rng.integers(0, 5, size=n))

    credit_score = rng.normal(loc=690, scale=85, size=n).clip(300, 850).round(0)
    collateral_ratio = rng.uniform(0.0, 1.6, size=n)
    collateral_value = (debt * collateral_ratio).round(0)

    # Profitability is synthetic and intentionally depends on risk drivers.
    profitability = (
        debt * rng.uniform(0.015, 0.075, size=n)
        - days_past_due * rng.uniform(250, 1100, size=n)
        + (credit_score - 650) * rng.uniform(40, 120, size=n)
    ).round(0)

    df = pd.DataFrame(
        {
            "client_id": [f"C{100000 + i}" for i in range(n)],
            "contract_id": [f"K{700000 + i}" for i in range(n)],
            "segment": segments,
            "region": regions,
            "debt": debt,
            "monthly_income": monthly_income,
            "profitability": profitability,
            "days_past_due": days_past_due,
            "credit_score": credit_score,
            "collateral_value": collateral_value,
        }
    )
    return df


def validate_columns(df: pd.DataFrame) -> list[str]:
    missing = sorted(list(REQUIRED_COLUMNS - set(df.columns)))
    return missing


def add_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["debt_to_income"] = result["debt"] / result["monthly_income"].replace(0, np.nan)
    result["collateral_coverage"] = result["collateral_value"] / result["debt"].replace(0, np.nan)

    score = np.zeros(len(result))

    score += np.where(result["days_past_due"] > 60, 45, 0)
    score += np.where((result["days_past_due"] > 30) & (result["days_past_due"] <= 60), 35, 0)
    score += np.where((result["days_past_due"] > 0) & (result["days_past_due"] <= 30), 18, 0)

    score += np.where(result["debt_to_income"] > 10, 25, 0)
    score += np.where((result["debt_to_income"] > 6) & (result["debt_to_income"] <= 10), 15, 0)

    score += np.where(result["credit_score"] < 550, 25, 0)
    score += np.where((result["credit_score"] >= 550) & (result["credit_score"] < 650), 12, 0)

    score += np.where(result["profitability"] < 0, 20, 0)
    score += np.where(result["collateral_coverage"] < 0.5, 10, 0)

    result["risk_score"] = np.clip(score, 0, 100).round(0)

    result["risk_level"] = pd.cut(
        result["risk_score"],
        bins=[-1, 29, 59, 100],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    result["risk_reason"] = result.apply(explain_risk, axis=1)
    return result


def explain_risk(row: pd.Series) -> str:
    reasons = []
    if row["days_past_due"] > 30:
        reasons.append("significant overdue payments")
    elif row["days_past_due"] > 0:
        reasons.append("minor overdue payments")
    if row["debt_to_income"] > 10:
        reasons.append("very high debt-to-income ratio")
    elif row["debt_to_income"] > 6:
        reasons.append("elevated debt-to-income ratio")
    if row["credit_score"] < 550:
        reasons.append("low credit score")
    elif row["credit_score"] < 650:
        reasons.append("below-average credit score")
    if row["profitability"] < 0:
        reasons.append("negative profitability")
    if row["collateral_coverage"] < 0.5:
        reasons.append("low collateral coverage")
    return "; ".join(reasons) if reasons else "stable payment profile"


def format_money(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def generate_executive_summary(df: pd.DataFrame) -> str:
    total_debt = df["debt"].sum()
    high_risk_share = (df["risk_level"] == "High").mean() * 100
    negative_profit_share = (df["profitability"] < 0).mean() * 100
    avg_dti = df["debt_to_income"].mean()

    worst_segment = (
        df.groupby("segment")["risk_score"].mean().sort_values(ascending=False).index[0]
    )
    worst_region = (
        df.groupby("region")["risk_score"].mean().sort_values(ascending=False).index[0]
    )

    return (
        f"Portfolio contains {len(df):,} contracts with total debt of {format_money(total_debt)}. "
        f"High-risk clients represent {high_risk_share:.1f}% of the portfolio, while "
        f"{negative_profit_share:.1f}% of contracts have negative profitability. "
        f"The average debt-to-income ratio is {avg_dti:.2f}. "
        f"The most vulnerable segment is {worst_segment}, and the region with the highest average risk score is {worst_region}. "
        "Recommended action: prioritize high-risk contracts with overdue payments, negative profitability, and weak collateral coverage."
    )


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


st.title("RiskPulse: Credit Portfolio Intelligence")
st.caption(
    "A mini Bloomberg-style analytical service for credit portfolio monitoring, risk segmentation, and executive insights."
)

with st.sidebar:
    st.header("Data input")
    uploaded_file = st.file_uploader("Upload credit portfolio CSV", type=["csv"])
    st.write("Required columns:")
    st.code(", ".join(sorted(REQUIRED_COLUMNS)))

    use_sample = st.toggle("Use built-in sample data", value=True)
    st.divider()
    st.header("Filters")

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
elif use_sample:
    df_raw = generate_sample_data()
else:
    st.info("Upload a CSV file or turn on built-in sample data.")
    st.stop()

missing_columns = validate_columns(df_raw)
if missing_columns:
    st.error("The uploaded file is missing required columns: " + ", ".join(missing_columns))
    st.stop()

for col in ["debt", "monthly_income", "profitability", "days_past_due", "credit_score", "collateral_value"]:
    df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

df_raw = df_raw.dropna(subset=list(REQUIRED_COLUMNS - {"client_id", "contract_id", "segment", "region"}))
df = add_risk_features(df_raw)

with st.sidebar:
    selected_segments = st.multiselect(
        "Segment", sorted(df["segment"].unique()), default=sorted(df["segment"].unique())
    )
    selected_regions = st.multiselect(
        "Region", sorted(df["region"].unique()), default=sorted(df["region"].unique())
    )
    selected_risk = st.multiselect(
        "Risk level", ["Low", "Medium", "High"], default=["Low", "Medium", "High"]
    )

filtered = df[
    df["segment"].isin(selected_segments)
    & df["region"].isin(selected_regions)
    & df["risk_level"].isin(selected_risk)
].copy()

if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

st.subheader("Portfolio overview")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Contracts", f"{len(filtered):,}")
col2.metric("Total debt", format_money(filtered["debt"].sum()))
col3.metric("Avg profitability", format_money(filtered["profitability"].mean()))
col4.metric("High-risk share", f"{(filtered['risk_level'] == 'High').mean() * 100:.1f}%")
col5.metric("Avg DTI", f"{filtered['debt_to_income'].mean():.2f}")

st.subheader("Executive summary")
st.info(generate_executive_summary(filtered))

left, right = st.columns(2)

with left:
    risk_counts = filtered["risk_level"].value_counts().reset_index()
    risk_counts.columns = ["risk_level", "contracts"]
    fig_risk = px.pie(
        risk_counts,
        names="risk_level",
        values="contracts",
        title="Risk distribution",
        hole=0.35,
    )
    st.plotly_chart(fig_risk, use_container_width=True)

with right:
    fig_segment = px.bar(
        filtered.groupby("segment", as_index=False)
        .agg(avg_risk_score=("risk_score", "mean"), total_debt=("debt", "sum"))
        .sort_values("avg_risk_score", ascending=False),
        x="segment",
        y="avg_risk_score",
        hover_data=["total_debt"],
        title="Average risk score by segment",
    )
    st.plotly_chart(fig_segment, use_container_width=True)

left, right = st.columns(2)

with left:
    fig_profit = px.scatter(
        filtered,
        x="debt_to_income",
        y="profitability",
        color="risk_level",
        size="debt",
        hover_data=["client_id", "contract_id", "segment", "days_past_due", "credit_score"],
        title="Profitability vs debt-to-income ratio",
    )
    st.plotly_chart(fig_profit, use_container_width=True)

with right:
    fig_region = px.bar(
        filtered.groupby("region", as_index=False)
        .agg(total_debt=("debt", "sum"), high_risk_contracts=("risk_level", lambda s: (s == "High").sum()))
        .sort_values("total_debt", ascending=False),
        x="region",
        y="total_debt",
        hover_data=["high_risk_contracts"],
        title="Debt exposure by region",
    )
    st.plotly_chart(fig_region, use_container_width=True)

st.subheader("Top risky contracts")
top_risky = filtered.sort_values(
    ["risk_score", "days_past_due", "debt"], ascending=[False, False, False]
).head(20)

st.dataframe(
    top_risky[
        [
            "client_id",
            "contract_id",
            "segment",
            "region",
            "debt",
            "monthly_income",
            "profitability",
            "days_past_due",
            "credit_score",
            "debt_to_income",
            "collateral_coverage",
            "risk_score",
            "risk_level",
            "risk_reason",
        ]
    ],
    use_container_width=True,
)

st.subheader("Full scored portfolio")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    label="Download scored portfolio as CSV",
    data=dataframe_to_csv_bytes(filtered),
    file_name=f"riskpulse_scored_portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)

st.divider()
st.markdown(
    """
    **How the risk score works:** the prototype uses transparent rule-based scoring. 
    It increases risk for overdue payments, high debt-to-income ratio, low credit score, negative profitability, and weak collateral coverage. 
    In a production version, this layer can be replaced by a calibrated ML model trained on default and recovery history.
    """
)
