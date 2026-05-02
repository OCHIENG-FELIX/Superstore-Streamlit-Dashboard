import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="Superstore BI Dashboard", layout="wide")
st.title("🛒 Superstore Business Intelligence Dashboard")
st.markdown("### Comprehensive Sales, Profit & Customer Insights")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Sample - Superstore.csv", encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")
regions = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
segments = st.sidebar.multiselect("Segment", df['Segment'].unique(), default=df['Segment'].unique())

filtered_df = df[
    (df['Region'].isin(regions)) &
    (df['Category'].isin(categories)) &
    (df['Segment'].isin(segments))
]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
with col2:
    st.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
with col3:
    margin = (filtered_df['Profit'].sum() / filtered_df['Sales'].sum() * 100) if filtered_df['Sales'].sum() > 0 else 0
    st.metric("Profit Margin", f"{margin:.1f}%")
with col4:
    st.metric("Orders", len(filtered_df))

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Trends", "📍 Performance", "👥 RFM", "🏆 Top Performers"])

with tab1:
    st.subheader("Key Insights")
    st.write("Use the filters on the left to explore different segments.")

with tab2:
    st.subheader("Sales & Profit Trend")
    monthly = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly['Order Date'] = monthly['Order Date'].astype(str)
    
    fig = px.line(monthly, x='Order Date', y=['Sales', 'Profit'], title="Monthly Trend")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales by Region")
        fig_r = px.bar(filtered_df.groupby('Region')['Sales'].sum().reset_index(), x='Region', y='Sales')
        st.plotly_chart(fig_r, use_container_width=True)
    with col2:
        st.subheader("Profit by Category")
        fig_c = px.bar(filtered_df.groupby('Category')['Profit'].sum().reset_index(), x='Category', y='Profit')
        st.plotly_chart(fig_c, use_container_width=True)

with tab4:
    st.subheader("Customer Segmentation (RFM - Simple)")
    # Simple RFM based on Monetary
    rfm = filtered_df.groupby('Customer ID')['Sales'].sum().reset_index()
    rfm['Segment'] = pd.qcut(rfm['Sales'], 4, labels=['Low', 'Medium', 'High', 'VIP'])
    st.bar_chart(rfm['Segment'].value_counts())

with tab5:
    st.subheader("Top 10 Most Profitable Products")
    top = filtered_df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10)
    fig_top = px.bar(top.reset_index(), x='Product Name', y='Profit', orientation='h')
    st.plotly_chart(fig_top, use_container_width=True)

# Download Button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='superstore_filtered_data.csv',
    mime='text/csv'
)

st.caption("Superstore BI Dashboard | Built with Streamlit & Plotly | By Ochieng Felix")
