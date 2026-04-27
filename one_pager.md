# RiskPulse: Credit Portfolio Intelligence

**Prototype link:** _insert Streamlit link here_

## 1. Problem

Credit portfolio analysis in banks often requires analysts to manually combine SQL queries, Excel files, dashboards, and written comments for management. This creates several problems: the analysis is slow, the methodology is not always transparent, repetitive reporting consumes analyst time, and risky segments may be identified too late.

The problem is especially relevant for portfolio monitoring, profitability analysis, and retail risk management. Analysts need to quickly answer questions such as: which segments are becoming riskier, where negative profitability is concentrated, which clients require attention, and what actions should be prioritized.

## 2. Solution

RiskPulse is a web service for automated credit portfolio intelligence. The user uploads a CSV file with client or contract-level data, and the service automatically calculates portfolio metrics, assigns risk levels to contracts, builds interactive visualizations, identifies the riskiest clients, and generates a short executive summary.

The prototype works with synthetic data, so it can be demonstrated without using confidential bank information.

## 3. Target users

The service is designed for:

- credit risk analysts;
- portfolio managers;
- product teams in banking;
- team leads and managers who need a fast overview of portfolio quality.

## 4. Main functionality

RiskPulse includes the following features:

1. CSV upload with validation of required columns.
2. Automatic calculation of portfolio KPIs:
   - number of contracts;
   - total debt;
   - average profitability;
   - share of high-risk contracts;
   - average debt-to-income ratio.
3. Rule-based risk scoring for each contract.
4. Risk segmentation into Low, Medium, and High risk groups.
5. Interactive charts:
   - risk distribution;
   - average risk score by segment;
   - profitability vs. debt-to-income ratio;
   - debt exposure by region.
6. Table with the top risky contracts and explanations of risk drivers.
7. Executive summary that explains the main portfolio issues in business language.
8. Export of the scored portfolio to CSV.

## 5. Motivation for implementation

The service improves the analytical workflow by reducing the amount of manual work needed for first-level credit portfolio review. Instead of preparing separate SQL extracts, Excel calculations, charts, and written comments, an analyst can upload data and immediately receive a structured portfolio overview.

This can reduce reporting time, improve consistency of risk classification, make portfolio monitoring more transparent, and help management react faster to negative changes in portfolio quality.

## 6. Technical complexity

The prototype is not a static website. It includes several technical components:

- data ingestion through file upload;
- validation of input schema;
- feature engineering, including debt-to-income ratio and collateral coverage;
- transparent rule-based risk scoring;
- portfolio aggregation and KPI calculation;
- interactive visual analytics with Plotly;
- automatic generation of an executive summary;
- downloadable analytical output.

The current risk model is rule-based for transparency. In a production version, it could be replaced with a machine learning model trained on historical default, delinquency, and recovery data.

## 7. Technology stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

## 8. Future development

Potential extensions include:

- integration with a database or data warehouse;
- historical trend monitoring;
- ML-based probability of default model;
- alerts for portfolio deterioration;
- user authentication;
- PDF report generation;
- API for integration with internal bank systems.
