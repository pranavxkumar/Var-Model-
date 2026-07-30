import streamlit as st
import numpy as np
from datetime import datetime, timedelta
from risk_engine import RiskEngine
import visualizations as viz
from report_generator import generate_pdf_report, generate_csv

st.set_page_config(page_title="Risk Analytics Engine", layout="wide", page_icon="📈")

def main():
    st.title("Multi-Asset Portfolio Risk Analytics")
    st.markdown("Enterprise-grade risk dashboard calculating Value at Risk (VaR), Expected Shortfall (CVaR), and core portfolio metrics.")

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("Portfolio Configuration")
    
    # Asset Selection
    default_tickers = "SPY, QQQ, GLD, IEF"
    tickers_input = st.sidebar.text_input("Assets (Comma separated)", value=default_tickers)
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    # Weights
    default_weights = ", ".join([str(round(1.0/len(tickers), 4))] * len(tickers))
    weights_input = st.sidebar.text_input("Weights (Comma separated)", value=default_weights)
    
    try:
        weights = [float(w.strip()) for w in weights_input.split(",") if w.strip()]
        if len(weights) != len(tickers):
            st.sidebar.error(f"Mismatch: {len(tickers)} assets and {len(weights)} weights.")
            st.stop()
        if not np.isclose(sum(weights), 1.0):
            st.sidebar.warning(f"Weights sum to {sum(weights):.2f}, normalizing to 1.0.")
            weights = [w / sum(weights) for w in weights]
    except ValueError:
        st.sidebar.error("Invalid weights format. Use numbers separated by commas.")
        st.stop()

    # Timeframe & Value
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start Date", datetime.today() - timedelta(days=365*5))
    end_date = col2.date_input("End Date", datetime.today())
    port_val = st.sidebar.number_input("Portfolio Value ($)", min_value=1000, value=1000000, step=10000)
    
    # Risk Settings
    st.sidebar.header("Risk Parameters")
    conf_level = st.sidebar.selectbox("Confidence Level", [0.95, 0.99], format_func=lambda x: f"{x*100:.0f}%")
    var_method = st.sidebar.selectbox("VaR Methodology", ["Historical Simulation", "Parametric (Variance-Covariance)"])

    generate_btn = st.sidebar.button("Run Risk Engine", use_container_width=True, type="primary")

    # --- MAIN EXECUTION ---
    if generate_btn:
        with st.spinner("Fetching market data and calculating risk matrices..."):
            try:
                engine = RiskEngine(tickers, weights, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), port_val)
                engine.fetch_and_process_data()
                
                stats = engine.get_portfolio_stats()
                risk = engine.calculate_var_es(confidence_level=conf_level)
                drawdowns = engine.calculate_drawdowns()
                max_drawdown = drawdowns['Drawdown'].min()
                
            except Exception as e:
                st.error(f"Data processing error: {e}")
                st.stop()

        # --- DASHBOARD METRICS ---
        st.subheader("Performance & Risk Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Expected Annual Return", f"{stats['annual_return']:.2%}")
        m2.metric("Annualized Volatility", f"{stats['annual_volatility']:.2%}")
        m3.metric("Sharpe Ratio", f"{stats['sharpe_ratio']:.2f}")
        m4.metric("Maximum Drawdown", f"{max_drawdown:.2%}")

        st.markdown("---")
        
        # Risk Metrics Cards
        var_pct = risk['hist_var_pct'] if "Historical" in var_method else risk['param_var_pct']
        var_usd = risk['hist_var_usd'] if "Historical" in var_method else risk['param_var_usd']
        
        rc1, rc2 = st.columns(2)
        with rc1:
            st.info(f"**{var_method} VaR ({conf_level*100:.0f}%)**")
            st.metric("Max Expected Daily Loss", f"${var_usd:,.2f}", f"{var_pct:.2%}", delta_color="inverse")
            st.caption("The threshold loss amount that will not be exceeded with the chosen confidence level.")
            
        with rc2:
            st.error(f"**Expected Shortfall (CVaR) ({conf_level*100:.0f}%)**")
            st.metric("Average Tail Loss", f"${risk['es_usd']:,.2f}", f"{risk['es_pct']:,.2%}", delta_color="inverse")
            st.caption("The expected daily loss on the worst days that exceed the VaR threshold.")

        # --- CHARTS TABS ---
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Risk Distribution", "Correlations", "Drawdowns & Volatility"])
        
        with tab1:
            st.plotly_chart(viz.plot_cumulative_returns(drawdowns), use_container_width=True)
            
        with tab2:
            var_label = "Hist. VaR" if "Historical" in var_method else "Param. VaR"
            st.plotly_chart(viz.plot_return_distribution(engine.port_returns, var_pct, risk['es_pct'], var_label), use_container_width=True)
            
        with tab3:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.plotly_chart(viz.plot_correlation_heatmap(stats['corr_matrix']), use_container_width=True)
            with col_b:
                st.markdown("### Diversification Insight")
                st.write("Assets with correlations near **1.0** move perfectly together, offering little diversification.")
                st.write("Assets with **negative** correlations (often Gold or Treasuries vs Equities) provide a natural hedge, reducing overall portfolio volatility.")
                
        with tab4:
            st.plotly_chart(viz.plot_drawdowns(drawdowns), use_container_width=True)
            st.plotly_chart(viz.plot_rolling_volatility(engine.port_returns), use_container_width=True)

        # --- EXPORT SECTION ---
        st.markdown("---")
        st.subheader("Data Export")
        dl_col1, dl_col2 = st.columns(2)
        
        # PDF Generation
        pdf_bytes = generate_pdf_report(tickers, weights, start_date, end_date, port_val, conf_level, stats, risk)
        dl_col1.download_button(label="📄 Download Executive PDF Report", 
                                data=pdf_bytes, file_name="Risk_Report.pdf", mime="application/pdf")
        
        # CSV Generation
        csv_bytes = generate_csv(drawdowns)
        dl_col2.download_button(label="📊 Download Timeseries Data (CSV)", 
                                data=csv_bytes, file_name="Portfolio_Data.csv", mime="text/csv")

if __name__ == "__main__":
    main()