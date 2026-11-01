import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import DataLoader
from utils.insights import BusinessInsights
from config.db_config import get_db_config

st.set_page_config(page_title='Sales & Profit Analytics Dashboard', layout='wide', initial_sidebar_state='expanded')

st.title('Sales & Profit Analytics Dashboard')
st.markdown('---')

@st.cache_data(ttl=300)
def load_data():
    try:
        loader = DataLoader()
        df = loader.load_data()
        return df, None, loader.source_label
    except Exception as e:
        return pd.DataFrame(), str(e), 'N/A'

# DB status
with st.sidebar.expander('Database Status', expanded=False):
    try:
        db = get_db_config()
        ok, msg = db.test_connection()
        if ok:
            st.success(msg)
        else:
            st.warning(f'DB not connected: {msg}')
            st.caption('App will use CSV data from data/ folder.')
    except Exception as e:
        st.warning(f'DB check failed: {e}')
        st.caption('App will use CSV data from data/ folder.')

df, error, data_source = load_data()

if error:
    st.error(f'Error loading data: {error}')
    st.info('Ensure data/sample_sales.csv exists. You can also place your own CSV/Excel in data/ folder.')
    st.stop()

if df.empty:
    st.warning('Dataset is empty after cleaning.')
    st.stop()

st.sidebar.caption(f'Data source: {data_source}')

# Sidebar filters
st.sidebar.header('Filters')
if 'OrderDate' not in df.columns:
    st.error('OrderDate column missing from data.')
    st.stop()
min_date = df['OrderDate'].min().date()
max_date = df['OrderDate'].max().date()
date_range = st.sidebar.date_input('Select Date Range', [min_date, max_date], min_value=min_date, max_value=max_date)
if not (isinstance(date_range, (list, tuple)) and len(date_range) == 2):
    st.info('Please select both a start date and an end date in the sidebar.')
    st.stop()
regions = ['All'] + sorted([r for r in df['Region'].dropna().unique().tolist() if str(r).strip() != ''])
categories = ['All'] + sorted([c for c in df['Category'].dropna().unique().tolist() if str(c).strip() != ''])
sel_region = st.sidebar.selectbox('Select Region', regions)
sel_category = st.sidebar.selectbox('Select Product Category', categories)

# Apply filters
filtered_df = df.copy()
try:
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_d, end_d = date_range[0], date_range[1]
        filtered_df = filtered_df[(filtered_df['OrderDate'].dt.date >= start_d) & (filtered_df['OrderDate'].dt.date <= end_d)]
    if sel_region != 'All' and 'Region' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Region'] == sel_region]
    if sel_category != 'All' and 'Category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Category'] == sel_category]
except Exception as e:
    st.error(f'Error applying filters: {e}')
    st.stop()

if filtered_df.empty:
    st.warning('No data available for selected filters.')
    st.stop()

# KPI Cards (calculated from actual data)
col1, col2, col3, col4, col5 = st.columns(5)
try:
    total_sales = filtered_df['SalesAmount'].sum() if 'SalesAmount' in filtered_df.columns else 0
    total_profit = filtered_df['Profit'].sum() if 'Profit' in filtered_df.columns else 0
    total_orders = filtered_df['OrderID'].nunique() if 'OrderID' in filtered_df.columns else len(filtered_df)
    total_customers = filtered_df['CustomerID'].nunique() if 'CustomerID' in filtered_df.columns else 0
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    avg_order_value = (total_sales / total_orders) if total_orders > 0 else 0
    col1.metric('Total Sales', f'${total_sales:,.2f}')
    col2.metric('Total Profit', f'${total_profit:,.2f}')
    col3.metric('Profit Margin', f'{profit_margin:.2f}%')
    col4.metric('Avg Order Value', f'${avg_order_value:,.2f}')
    col5.metric('Total Orders / Customers', f'{total_orders:,} / {total_customers:,}')
except Exception as e:
    st.error(f'Error calculating KPIs: {e}')
    st.stop()

st.markdown('---')

# Monthly trend
st.subheader('Monthly Sales and Profit Trend')
try:
    trend = filtered_df.copy()
    trend['Month'] = trend['OrderDate'].dt.to_period('M').astype(str)
    monthly = trend.groupby('Month')[['SalesAmount', 'Profit']].sum().reset_index()
    fig_trend = px.line(monthly, x='Month', y=['SalesAmount', 'Profit'], markers=True, title='Monthly Sales and Profit Trend')
    st.plotly_chart(fig_trend, use_container_width=True)
except Exception as e:
    st.warning(f'Could not display monthly trend: {e}')

# Category and Region
col_cat, col_reg = st.columns(2)
with col_cat:
    st.subheader('Category-wise Sales and Profit')
    try:
        cat = filtered_df.groupby('Category')[['SalesAmount', 'Profit']].sum().reset_index()
        fig_cat = px.bar(cat, x='Category', y=['SalesAmount', 'Profit'], barmode='group')
        st.plotly_chart(fig_cat, use_container_width=True)
    except Exception as e:
        st.warning(f'Could not display category analysis: {e}')
with col_reg:
    st.subheader('Region-wise Sales Analysis')
    try:
        reg = filtered_df.groupby('Region')['SalesAmount'].sum().reset_index()
        fig_reg = px.pie(reg, values='SalesAmount', names='Region', hole=0.4)
        st.plotly_chart(fig_reg, use_container_width=True)
    except Exception as e:
        st.warning(f'Could not display region analysis: {e}')

# Top 10 products
st.subheader('Top 10 Best-Selling Products')
try:
    top_prod = filtered_df.groupby('Product')['SalesAmount'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_top = px.bar(top_prod, x='SalesAmount', y='Product', orientation='h', title='Top 10 Products by Sales Amount')
    st.plotly_chart(fig_top, use_container_width=True)
except Exception as e:
    st.warning(f'Could not display top products: {e}')

# Customer performance
st.subheader('Customer Performance Analysis (Top 10)')
try:
    cust_perf = filtered_df.groupby(['CustomerID', 'CustomerName'])[['SalesAmount', 'Profit']].sum().sort_values('SalesAmount', ascending=False).head(10).reset_index()
    st.dataframe(cust_perf, use_container_width=True)
except Exception as e:
    st.warning(f'Could not display customer performance: {e}')

# Data table
st.subheader('Sales Records')
try:
    display_df = filtered_df.sort_values('OrderDate', ascending=False)
    st.dataframe(display_df, use_container_width=True)
    st.caption(f'Showing {len(display_df):,} records')
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Filtered Data as CSV', csv, 'sales_filtered.csv', 'text/csv')
except Exception as e:
    st.warning(f'Could not display data table: {e}')

# Data Quality Summary
st.markdown('---')
st.subheader('Data Quality Summary')
try:
    dq_cols = st.columns(4)
    dq_cols[0].metric('Total Rows (Loaded)', f'{len(df):,}')
    dq_cols[1].metric('Rows After Filters', f'{len(filtered_df):,}')
    missing = df.isnull().sum().sum()
    dq_cols[2].metric('Missing Values (Loaded)', f'{missing:,}')
    dup = df.duplicated().sum() if len(df) > 0 else 0
    dq_cols[3].metric('Duplicate Rows (Loaded)', f'{dup:,}')
except Exception as e:
    st.warning(f'Could not display data quality summary: {e}')

# Insights
st.markdown('---')
st.subheader('Automatic Business Insights & Recommendations')
try:
    insights = BusinessInsights(filtered_df).generate_insights()
    for i in insights:
        st.write(f'- {i}')
except Exception as e:
    st.warning(f'Could not generate insights: {e}')

st.markdown('---')
st.caption('Sales & Profit Analytics Dashboard | Built with Streamlit, Pandas, Plotly, MySQL | KPIs calculated from actual dataset | No hardcoded values')

