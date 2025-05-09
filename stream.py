import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Title
st.title("Dashboard Analisis Data E-Commerce")

# Sidebar
st.sidebar.title("Navigasi")
view = st.sidebar.radio("Pilih dataset:", ("Pelanggan", "Geolokasi"))

# Load data
@st.cache_data
def load_data():
    customer_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/E-commerce-public-dataset/E-Commerce%20Public%20Dataset/customers_dataset.csv"
    geo_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/E-commerce-public-dataset/E-Commerce%20Public%20Dataset/geolocation_dataset.csv"
    order_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/E-commerce-public-dataset/E-Commerce%20Public%20Dataset/orders_dataset.csv"

    customer = pd.read_csv(customer_url)
    geolocation = pd.read_csv(geo_url)
    orders = pd.read_csv(order_url)
    return customer, geolocation, orders

customer_df, geo_df, orders_df = load_data()

# Display dataset
if view == "Pelanggan":
    st.subheader("Data Pelanggan")
    st.dataframe(customer_df.head())
    st.markdown(f"Jumlah baris: {customer_df.shape[0]}, Kolom: {customer_df.shape[1]}")

    # Statistik kota pelanggan
    if "customer_city" in customer_df.columns:
        st.subheader("Distribusi Kota Pelanggan")
        city_count = customer_df["customer_city"].value_counts().head(10)
        fig = px.bar(city_count, x=city_count.index, y=city_count.values, labels={"x": "Kota", "y": "Jumlah"})
        st.plotly_chart(fig)

elif view == "Geolokasi":
    st.subheader("Data Geolokasi")
    st.dataframe(geo_df.head())
    st.markdown(f"Jumlah baris: {geo_df.shape[0]}, Kolom: {geo_df.shape[1]}")

    if 'geolocation_lat' in geo_df.columns and 'geolocation_lng' in geo_df.columns:
        st.subheader("Distribusi Lokasi Geografis")
        fig = px.scatter_mapbox(
            geo_df.sample(1000),
            lat="geolocation_lat",
            lon="geolocation_lng",
            zoom=3,
            height=500,
            mapbox_style="open-street-map",
        )
        st.plotly_chart(fig)

# Tambahan Analisis
st.subheader("Analisis Tambahan")
if not orders_df.empty:
    st.markdown("### Filter Pesanan")
    orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
    min_date = orders_df["order_purchase_timestamp"].min().date()
    max_date = orders_df["order_purchase_timestamp"].max().date()
    
    selected_date = st.date_input("Rentang Tanggal Pemesanan", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    status_options = orders_df["order_status"].unique().tolist()
    selected_status = st.multiselect("Pilih Status Pesanan", options=status_options, default=status_options)

    filtered_orders = orders_df[
        (orders_df["order_purchase_timestamp"].dt.date >= selected_date[0]) &
        (orders_df["order_purchase_timestamp"].dt.date <= selected_date[1]) &
        (orders_df["order_status"].isin(selected_status))
    ]

    st.markdown("### Distribusi Waktu Pemesanan")
    filtered_orders["order_month"] = filtered_orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
    order_counts = filtered_orders["order_month"].value_counts().sort_index()
    fig = px.line(x=order_counts.index, y=order_counts.values, labels={"x": "Bulan", "y": "Jumlah Pesanan"})
    st.plotly_chart(fig)

    st.markdown("### Status Pesanan")
    status_counts = filtered_orders["order_status"].value_counts()
    fig = px.pie(values=status_counts.values, names=status_counts.index, title="Proporsi Status Pesanan")
    st.plotly_chart(fig)
