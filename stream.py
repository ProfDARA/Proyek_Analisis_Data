import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Title
st.title("Dashboard Analisis Data E-Commerce")

# Sidebar
st.sidebar.title("Navigasi")
view = st.sidebar.radio("Pilih dataset:", ("Pelanggan", "Geolokasi"))

# Load data
@st.cache_data
def load_data():
    data_dir = r"E:\\project\\DAta science\\Dicoding 1\\E-commerce-public-dataset"
    customer_path = os.path.join(data_dir, "customers_dataset.csv")
    geo_path = os.path.join(data_dir, "geolocation_dataset.csv")
    order_path = os.path.join(data_dir, "orders_dataset.csv")
    order_items_path = os.path.join(data_dir, "order_items_dataset.csv")

    customer = pd.read_csv(customer_path)
    geolocation = pd.read_csv(geo_path)
    orders = pd.read_csv(order_path)
    order_items = pd.read_csv(order_items_path)
    return customer, geolocation, orders, order_items

customer_df, geo_df, orders_df, order_items_df = load_data()

# Display selected dataset
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

# Visualisasi & Jawaban Pertanyaan Umum
st.subheader(" Insight Visualisasi ")

# Produk paling banyak dibeli
st.markdown("#### 1. Produk apa yang paling banyak dibeli pelanggan?")
most_sold = order_items_df["product_id"].value_counts().head(10)
fig = px.bar(x=most_sold.index, y=most_sold.values, labels={"x": "Product ID", "y": "Jumlah Terjual"})
st.plotly_chart(fig)

# Waktu penjualan tertinggi
st.markdown("#### 2. Kapan waktu penjualan tertinggi terjadi?")
orders_df["order_date"] = orders_df["order_purchase_timestamp"].dt.date
order_daily = orders_df["order_date"].value_counts().sort_index()
fig = px.line(x=order_daily.index, y=order_daily.values, labels={"x": "Tanggal", "y": "Jumlah Pesanan"})
st.plotly_chart(fig)

# Kota dengan volume transaksi tertinggi
st.markdown("#### 3. Kota mana yang memiliki volume transaksi tertinggi?")
order_customer = pd.merge(orders_df, customer_df, on="customer_id", how="inner")
city_volume = order_customer["customer_city"].value_counts().head(10)
fig = px.bar(x=city_volume.index, y=city_volume.values, labels={"x": "Kota", "y": "Jumlah Transaksi"})
st.plotly_chart(fig)

# Rata-rata waktu pengiriman
st.markdown("#### 4. Berapa rata-rata waktu pengiriman dari pembelian ke penerimaan?")
orders_df["order_delivered_customer_date"] = pd.to_datetime(orders_df["order_delivered_customer_date"], errors="coerce")
delivery_time = (orders_df["order_delivered_customer_date"] - orders_df["order_purchase_timestamp"]).dt.days
delivery_time = delivery_time.dropna()
st.write(f"Rata-rata waktu pengiriman: {delivery_time.mean():.2f} hari")
