# RiskPulse: Credit Portfolio Intelligence

RiskPulse is a Streamlit web service for credit portfolio monitoring. It allows a user to upload a CSV file with client or contract-level data and automatically receives portfolio metrics, risk segmentation, interactive charts, a list of top risky contracts, and an executive summary.

## Why this service is useful

In bank analytics, many portfolio reviews are still prepared manually in Excel, SQL scripts, and presentations. RiskPulse automates the first analytical layer: data validation, portfolio metrics, risk scoring, visualization, and management-level interpretation.

## Demo data

The application includes synthetic sample data. No real bank data is required.

## Required CSV columns

- client_id
- contract_id
- segment
- region
- debt
- monthly_income
- profitability
- days_past_due
- credit_score
- collateral_value

## Local launch

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, `sample_credit_portfolio.csv`, `README.md`, and `one_pager.md`.
3. Open Streamlit Community Cloud.
4. Connect the GitHub repository.
5. Select `app.py` as the main file.
6. Deploy the application and copy the public URL.

## Technical features

- CSV upload and validation
- Synthetic portfolio generation
- Rule-based credit risk scoring
- Portfolio-level KPIs
- Segment and regional risk analytics
- Interactive Plotly charts
- Executive summary generation
- Downloadable scored portfolio
