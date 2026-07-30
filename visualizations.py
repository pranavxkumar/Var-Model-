import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def plot_cumulative_returns(drawdown_df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=drawdown_df.index, y=drawdown_df['Cumulative Return'], 
                             mode='lines', name='Portfolio Value', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=drawdown_df.index, y=drawdown_df['High Water Mark'], 
                             mode='lines', name='High Water Mark', line=dict(color='rgba(127, 127, 127, 0.5)', width=2, dash='dash')))
    fig.update_layout(title="Cumulative Portfolio Growth", xaxis_title="Date", yaxis_title="Growth of $1", 
                      template="plotly_white", hovermode="x unified", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    return fig

def plot_drawdowns(drawdown_df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=drawdown_df.index, y=drawdown_df['Drawdown'], fill='tozeroy',
                             mode='lines', name='Drawdown', line=dict(color='red', width=1), fillcolor='rgba(255, 0, 0, 0.2)'))
    fig.update_layout(title="Portfolio Drawdowns", xaxis_title="Date", yaxis_title="Drawdown (%)",
                      template="plotly_white", hovermode="x unified", yaxis_tickformat='.1%')
    return fig

def plot_return_distribution(port_returns: pd.Series, var_pct: float, es_pct: float, var_label: str):
    fig = px.histogram(port_returns, nbins=50, title="Daily Return Distribution",
                       labels={'value': 'Daily Return'}, opacity=0.7, color_discrete_sequence=['#4287f5'])
    
    # VaR Line
    fig.add_vline(x=-var_pct, line_dash="dash", line_color="orange", 
                  annotation_text=f"{var_label}: {-var_pct:.2%}", annotation_position="top left")
    # ES Line
    fig.add_vline(x=-es_pct, line_dash="solid", line_color="red", 
                  annotation_text=f"ES: {-es_pct:.2%}", annotation_position="bottom left")
    
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig

def plot_correlation_heatmap(corr_matrix: pd.DataFrame):
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        hoverinfo="text"
    ))
    fig.update_layout(title="Asset Correlation Matrix", template="plotly_white", width=600, height=600)
    return fig

def plot_rolling_volatility(port_returns: pd.Series, window=30):
    rolling_vol = port_returns.rolling(window=window).std() * np.sqrt(252)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol, mode='lines', name='Rolling Volatility', line=dict(color='purple')))
    fig.update_layout(title=f"Rolling {window}-Day Annualized Volatility", xaxis_title="Date", yaxis_title="Annualized Vol",
                      template="plotly_white", hovermode="x unified", yaxis_tickformat='.1%')
    return fig