import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm

class RiskEngine:
    def __init__(self, tickers, weights, start_date, end_date, portfolio_value, risk_free_rate=0.02):
        self.tickers = [t.strip().upper() for t in tickers]
        self.weights = np.array(weights)
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio_value = portfolio_value
        self.risk_free_rate = risk_free_rate
        
        self.prices = pd.DataFrame()
        self.returns = pd.DataFrame()
        self.port_returns = pd.Series(dtype=float)
        
    def fetch_and_process_data(self):
        """Downloads data and computes log returns safely with multi-ticker support."""
        data = yf.download(self.tickers, start=self.start_date, end=self.end_date, auto_adjust=False)
        
        # Extract 'Adj Close' safely depending on yfinance return structure
        if isinstance(data.columns, pd.MultiIndex):
            if 'Adj Close' in data.columns.levels[0]:
                prices = data['Adj Close']
            else:
                prices = data['Close']
        else:
            prices = data[['Adj Close']] if 'Adj Close' in data.columns else data[['Close']]

        # Handle single ticker edge case or multi-column dataframes
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=self.tickers[0])
            
        self.prices = prices.ffill().dropna()
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna()
        
        # Ensure alignment between weights and return columns
        self.returns = self.returns[self.tickers]
        self.port_returns = self.returns.dot(self.weights)
        
    def get_portfolio_stats(self):
        """Calculates expected return, volatility, and Sharpe ratio."""
        TRADING_DAYS = 252
        annual_return = self.port_returns.mean() * TRADING_DAYS
        
        cov_matrix_daily = self.returns.cov()
        cov_matrix_annual = cov_matrix_daily * TRADING_DAYS
        port_variance = np.dot(self.weights.T, np.dot(cov_matrix_annual, self.weights))
        annual_volatility = np.sqrt(port_variance)
        
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility
        
        return {
            "annual_return": annual_return,
            "annual_volatility": annual_volatility,
            "sharpe_ratio": sharpe_ratio,
            "cov_matrix": cov_matrix_daily,
            "corr_matrix": self.returns.corr()
        }

    def calculate_var_es(self, confidence_level=0.95):
        """Calculates Parametric VaR, Historical VaR, and Expected Shortfall."""
        alpha = 1 - confidence_level
        mu = np.mean(self.port_returns)
        sigma = np.std(self.port_returns)
        
        z_score = norm.ppf(alpha)
        param_var_pct = -(mu + z_score * sigma)
        
        hist_var_pct = -np.percentile(self.port_returns, alpha * 100)
        
        tail_losses = self.port_returns[self.port_returns <= -hist_var_pct]
        es_pct = -tail_losses.mean() if len(tail_losses) > 0 else hist_var_pct
        
        return {
            "param_var_pct": param_var_pct,
            "param_var_usd": param_var_pct * self.portfolio_value,
            "hist_var_pct": hist_var_pct,
            "hist_var_usd": hist_var_pct * self.portfolio_value,
            "es_pct": es_pct,
            "es_usd": es_pct * self.portfolio_value
        }

    def calculate_drawdowns(self):
        """Calculates rolling drawdowns."""
        cumulative_returns = np.exp(self.port_returns.cumsum())
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        
        return pd.DataFrame({
            'Cumulative Return': cumulative_returns,
            'High Water Mark': running_max,
            'Drawdown': drawdown
        })
