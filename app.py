import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Superstore Customer 360", layout="wide")
st.title("🛒 Superstore Customer 360 Dashboard")
st.markdown("### Complete Customer & Sales Insights")

@st.cache_data
def load_data():
    df = pd.read_csv("Sample - Superstore.csv", encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
    return df

df = load_data()

# Sidebar
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())

filtered_df = df[(df['Region'].isin(regions)) & (df['Category'].isin(categories))]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
with col2: st.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
with col3: 
    margin = (filtered_df['Profit'].sum() / filtered_df['Sales'].sum() * 100) if filtered_df['Sales'].sum() > 0 else 0
    st.metric("Profit Margin", f"{margin:.1f}%")
with col4: st.metric("Orders", len(filtered_df))

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Performance", "👥 RFM", "🏆 Top"])

with tab1:
    monthly = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).agg({'Sales':'sum','Profit':'sum'}).reset_index()
    monthly['Order Date'] = monthly['Order Date'].astype(str)
    st.plotly_chart(px.line(monthly, x='Order Date', y=['Sales','Profit'], title="Sales & Profit Trend"), use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(filtered_df.groupby('Region')['Sales'].sum().reset_index(), x='Region', y='Sales'), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(filtered_df.groupby('Category')['Profit'].sum().reset_index(), x='Category', y='Profit'), use_container_width=True)

with tab3:
    st.subheader("RFM Customer Segmentation")
    latest = filtered_df['Order Date'].max()
    rfm = filtered_df.groupby('Customer ID').agg({
        'Order Date': lambda x: (latest - x.max()).days,
        'Order ID': 'nunique',
        'Sales': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    rfm['Segment'] = pd.qcut(rfm['Monetary'], 4, labels=['Low', 'Medium', 'High', 'VIP'])
    st.bar_chart(rfm['Segment'].value_counts())

with tab4:
    st.subheader("Top 10 Products by Profit")
    top = filtered_df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10)
    st.plotly_chart(px.bar(top.reset_index(), x='Product Name', y='Profit', orientation='h'), use_container_width=True)

# Download
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False).encode('utf-8'), "superstore_data.csv", "text/csv")

st.caption("Superstore Customer 360 Dashboard | By Ochieng Felix")
