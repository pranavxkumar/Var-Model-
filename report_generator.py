from fpdf import FPDF
import pandas as pd

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Institutional Portfolio Risk Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(tickers, weights, start, end, port_val, conf_level, stats, risk) -> bytes:
    pdf = PDFReport()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Portfolio Specifications", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Assets: {', '.join(tickers)}", 0, 1)
    weight_str = ", ".join([f"{t}: {w:.1%}" for t, w in zip(tickers, weights)])
    pdf.cell(0, 8, f"Weights: {weight_str}", 0, 1)
    pdf.cell(0, 8, f"Time Horizon: {start} to {end}", 0, 1)
    pdf.cell(0, 8, f"Current Value: ${port_val:,.2f}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Return & Volatility Metrics (Annualized)", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Expected Return: {stats['annual_return']:.2%}", 0, 1)
    pdf.cell(0, 8, f"Volatility: {stats['annual_volatility']:.2%}", 0, 1)
    pdf.cell(0, 8, f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"3. Risk Metrics ({conf_level*100:.0f}% Confidence)", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Parametric VaR: {risk['param_var_pct']:.2%} (${risk['param_var_usd']:,.2f})", 0, 1)
    pdf.cell(0, 8, f"Historical VaR: {risk['hist_var_pct']:.2%} (${risk['hist_var_usd']:,.2f})", 0, 1)
    pdf.cell(0, 8, f"Expected Shortfall (CVaR): {risk['es_pct']:.2%} (${risk['es_usd']:,.2f})", 0, 1)
    
    # Explicitly cast the output buffer to standard bytes for Streamlit
    return bytes(pdf.output())

def generate_csv(drawdown_df: pd.DataFrame) -> bytes:
    return drawdown_df.to_csv().encode('utf-8')
