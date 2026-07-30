# Institutional Risk Analytics Dashboard

## Project Objective
A complete, interactive web application built in Python (Streamlit) designed to act as a production-quality financial risk engine. It calculates essential downside risk metrics—Value at Risk (VaR) and Expected Shortfall (CVaR)—and provides institutional-grade visualizations to analyze portfolio diversification and tail risk.

## Methodology
- **Data Engine**: Automated ETL pipeline utilizing `yfinance` to source daily adjusted closing prices.
- **Risk Math**: 
  - Calculates daily logarithmic returns.
  - Generates annualized covariance and correlation matrices.
  - Implements **Parametric VaR** (Variance-Covariance) leveraging normal distribution Z-scores.
  - Implements **Historical Simulation VaR** using empirical historical quantiles.
  - Implements **Expected Shortfall (CVaR)** to measure the average magnitude of losses beyond the VaR threshold.
- **Frontend Architecture**: Streamlit for reactive UI state management; Plotly for interactive, hoverable data visualizations.

## How to Run Locally

1. **Clone the repository and navigate to the folder:**
   ```bash
   git clone <your-repo-link>
   cd risk_dashboard