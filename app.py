import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Superstore BI Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Superstore Business Intelligence Dashboard")
st.markdown("### Sales, Profit & Customer Insights | 2014 - 2017")

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
regions = st.sidebar.multiselect("Region", options=df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Category", options=df['Category'].unique(), default=df['Category'].unique())
segments = st.sidebar.multiselect("Segment", options=df['Segment'].unique(), default=df['Segment'].unique())

# Filter the data
filtered_df = df[
    (df['Region'].isin(regions)) &
    (df['Category'].isin(categories)) &
    (df['Segment'].isin(segments))
]

# ====================== KPIs ======================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
with col2:
    st.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
with col3:
    margin = (filtered_df['Profit'].sum() / filtered_df['Sales'].sum() * 100) if filtered_df['Sales'].sum() > 0 else 0
    st.metric("Profit Margin", f"{margin:.1f}%")
with col4:
    st.metric("Total Orders", len(filtered_df))

# ====================== CHARTS ======================
tab1, tab2, tab3 = st.tabs(["📈 Trends", "📊 Performance", "🔝 Top Performers"])

with tab1:
    st.subheader("Sales & Profit Trend")
    monthly = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly['Order Date'] = monthly['Order Date'].astype(str)
    
    fig = px.line(monthly, x='Order Date', y=['Sales', 'Profit'], 
                  title="Monthly Sales vs Profit Trend", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales by Region")
        fig_region = px.bar(filtered_df.groupby('Region')['Sales'].sum().reset_index(), 
                            x='Region', y='Sales', color='Region')
        st.plotly_chart(fig_region, use_container_width=True)
    
    with col2:
        st.subheader("Profit by Category")
        fig_cat = px.bar(filtered_df.groupby('Category')['Profit'].sum().reset_index(), 
                         x='Category', y='Profit', color='Category')
        st.plotly_chart(fig_cat, use_container_width=True)

with tab3:
    st.subheader("Top 10 Most Profitable Products")
    top_products = filtered_df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10)
    fig_top = px.bar(top_products.reset_index(), x='Product Name', y='Profit', orientation='h')
    st.plotly_chart(fig_top, use_container_width=True)

st.caption("Superstore BI Dashboard | Built with Streamlit & Plotly | By Ochieng Felix")
