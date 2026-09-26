import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Setup Page
st.set_page_config(page_title="Magnificent Seven Viewer", layout="wide")
st.title("Magnificent Seven Stock Viewer")
st.markdown("Select a ticker and a time period to view historical stock prices and trading volume.")

# 2. User Inputs (Dropdowns side-by-side)
col1, col2 = st.columns(2)
with col1:
    selected_ticker = st.selectbox("Select a Ticker", ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META'])
with col2:
    selected_period = st.selectbox("Select Time Period", ['Last 3 Months', 'Last 6 Months', 'YTD', '1 Year', '3 Years', '5 Years', 'Max'])

# 3. Data Downloading (using st.cache_data to speed up the app)
@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, start='2000-01-01', end=datetime.date.today())
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# Load data for the chosen ticker
df_subset = load_data(selected_ticker)

# 4. Filter by Time Period
max_date = df_subset['Date'].max()
if selected_period == 'Last 3 Months':
    start_date = max_date - pd.DateOffset(months=3)
elif selected_period == 'Last 6 Months':
    start_date = max_date - pd.DateOffset(months=6)
elif selected_period == 'YTD':
    start_date = pd.to_datetime(f'{max_date.year}-01-01')
elif selected_period == '1 Year':
    start_date = max_date - pd.DateOffset(years=1)
elif selected_period == '3 Years':
    start_date = max_date - pd.DateOffset(years=3)
elif selected_period == '5 Years':
    start_date = max_date - pd.DateOffset(years=5)
else: # 'Max'
    start_date = df_subset['Date'].min()

df_subset = df_subset[df_subset['Date'] >= start_date]

# 5. Build the Plotly Figure
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
fig.add_trace(go.Scatter(x=df_subset['Date'], y=df_subset['Close'], name='Close Price', line=dict(color='#1f77b4')), row=1, col=1)
fig.add_trace(go.Bar(x=df_subset['Date'], y=df_subset['Volume'], name='Volume', marker_color='#7f7f7f'), row=2, col=1)
fig.update_layout(height=600, showlegend=False, margin=dict(l=50, r=50, t=50, b=50))
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
fig.update_yaxes(title_text="Price (USD)", row=1, col=1, showgrid=True, gridwidth=1, gridcolor='LightGray')
fig.update_yaxes(title_text="Volume", row=2, col=1, showgrid=True, gridwidth=1, gridcolor='LightGray')

# 6. Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
