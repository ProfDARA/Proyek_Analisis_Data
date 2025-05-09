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

# Load cleaned data from URL
@st.cache_data
def load_data():
    customer_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/cleaned_customer.csv"
    geo_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/cleaned_geolocation.csv"
    orders_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/cleaned_orders.csv"
    order_items_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/E-commerce-public-dataset/order_items_dataset.csv"
    products_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/E-commerce-public-dataset/products_dataset.csv"
    payments_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/E-commerce-public-dataset/order_payments_dataset.csv"

    customer = pd.read_csv(customer_url)
    geolocation = pd.read_csv(geo_url)
    orders = pd.read_csv(orders_url)
    order_items = pd.read_csv(order_items_url)
    products = pd.read_csv(products_url)
    payments = pd.read_csv(payments_url)
    return customer, geolocation, orders, order_items, products, payments

customer_df, geo_df, orders_df, order_items_df, products_df, payments_df = load_data()

# Display selected dataset
if view == "Pelanggan":
    st.subheader("Data Pelanggan")
    st.dataframe(customer_df.head())
    st.markdown(f"Jumlah baris: {customer_df.shape[0]}, Kolom: {customer_df.shape[1]}")

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

# Analisis Tambahan
st.subheader("Analisis Tambahan")
if not orders_df.empty:
    st.markdown("### Filter Pesanan")
    orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
    min_date = orders_df["order_purchase_timestamp"].min().date()
    max_date = orders_df["order_purchase_timestamp"].max().date()

    selected_date = st.date_input("Rentang Tanggal Pemesanan", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    if "order_status" in orders_df.columns:
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

# Insight Visualisasi
st.subheader(" Insight Visualisasi ")

# Produk paling banyak dibeli berdasarkan product_category_name
st.markdown("#### 1. Produk apa yang paling banyak dibeli pelanggan?")
merged_df = pd.merge(orders_df, order_items_df, on='order_id', how='left')
merged_df = pd.merge(merged_df, products_df, on='product_id', how='left')
merged_df = pd.merge(merged_df, payments_df, on='order_id', how='left')
merged_df = pd.merge(merged_df, customer_df, on='customer_id', how='left')

if "product_category_name" in merged_df.columns:
    top_products = merged_df["product_category_name"].value_counts().head(10)
    fig = px.bar(x=top_products.index, y=top_products.values, labels={"x": "Kategori Produk", "y": "Jumlah Pembelian"})
    st.plotly_chart(fig)

# Waktu penjualan tertinggi
if "order_purchase_timestamp" in orders_df.columns:
    st.markdown("#### 2. Kapan waktu penjualan tertinggi terjadi?")
    orders_df["order_date"] = orders_df["order_purchase_timestamp"].dt.date
    order_daily = orders_df["order_date"].value_counts().sort_index()
    fig = px.line(x=order_daily.index, y=order_daily.values, labels={"x": "Tanggal", "y": "Jumlah Pesanan"})
    st.plotly_chart(fig)

# Kota dengan volume transaksi tertinggi
if "customer_id" in orders_df.columns and "customer_id" in customer_df.columns:
    st.markdown("#### 3. Kota mana yang memiliki volume transaksi tertinggi?")
    order_customer = pd.merge(orders_df, customer_df, on="customer_id", how="inner")
    city_volume = order_customer["customer_city"].value_counts().head(10)
    fig = px.bar(x=city_volume.index, y=city_volume.values, labels={"x": "Kota", "y": "Jumlah Transaksi"})
    st.plotly_chart(fig)

# Rata-rata waktu pengiriman
if "order_delivered_customer_date" in orders_df.columns:
    st.markdown("#### 4. Berapa rata-rata waktu pengiriman dari pembelian ke penerimaan?")
    orders_df["order_delivered_customer_date"] = pd.to_datetime(orders_df["order_delivered_customer_date"], errors="coerce")
    delivery_time = (orders_df["order_delivered_customer_date"] - orders_df["order_purchase_timestamp"]).dt.days
    delivery_time = delivery_time.dropna()
    st.write(f"Rata-rata waktu pengiriman: {delivery_time.mean():.2f} hari")