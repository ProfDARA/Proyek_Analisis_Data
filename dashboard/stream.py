import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Dashboard Analisis Data E-Commerce Brazil")

@st.cache_data

def load_data():
    #url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/merged_df.csv"
    df = pd.read_csv("merged_df.csv")
    df.columns = df.columns.str.strip()
    df["geolocation_lat"] = pd.to_numeric(df["geolocation_lat"], errors="coerce")
    df["geolocation_lng"] = pd.to_numeric(df["geolocation_lng"], errors="coerce")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors='coerce')
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"], errors='coerce')
    return df

merged_df = load_data()

# Sidebar Filters
st.sidebar.header("🔎Filter")
min_date = merged_df["order_purchase_timestamp"].min()
max_date = merged_df["order_purchase_timestamp"].max()
date_range = st.sidebar.date_input("Rentang Tanggal Pembelian", [min_date, max_date])

kategori = st.sidebar.multiselect(
    "Pilih Kategori Produk", 
    options=merged_df["product_category_name"].dropna().unique(),
    default=[]
)

kota = st.sidebar.multiselect(
    "Pilih Kota Pelanggan", 
    options=merged_df["customer_city"].dropna().unique(),
    default=[]
)

# Terapkan filter
filtered_df = merged_df[
    (merged_df["order_purchase_timestamp"].dt.date >= date_range[0]) &
    (merged_df["order_purchase_timestamp"].dt.date <= date_range[1])
]
if kategori:
    filtered_df = filtered_df[filtered_df["product_category_name"].isin(kategori)]
if kota:
    filtered_df = filtered_df[filtered_df["customer_city"].isin(kota)]

# Data preview
st.subheader("Data Gabungan (filtered)")
st.data_editor(filtered_df.head(20), num_rows="dynamic", use_container_width=True)

# Peta Sebaran Geolokasi
st.subheader("Peta Sebaran Lokasi Pelanggan")
valid_geo = filtered_df.dropna(subset=["geolocation_lat", "geolocation_lng"])

if not valid_geo.empty:
    sample_size = min(1000, len(valid_geo))
    fig = px.scatter_mapbox(
        valid_geo.sample(n=sample_size, random_state=42),
        lat="geolocation_lat",
        lon="geolocation_lng",
        color_discrete_sequence=["blue"],
        hover_name="customer_city",
        hover_data=["customer_state", "order_id"],
        zoom=3,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Tidak ada data koordinat yang valid untuk visualisasi.")

# Insight: Produk Terbanyak
with st.expander(" Produk Paling Banyak Dibeli"):
    top_products = filtered_df["product_category_name"].value_counts().head(10)
    fig = px.bar(
        x=top_products.index, 
        y=top_products.values, 
        labels={"x": "Kategori Produk", "y": "Jumlah Pembelian"},
        color=top_products.index
    )
    st.plotly_chart(fig, use_container_width=True)

# Insight: Bulan Terlaris
with st.expander(" Bulan Penjualan Tertinggi"):
    filtered_df["order_purchase_month"] = filtered_df["order_purchase_timestamp"].dt.month
    sales_by_month = filtered_df["order_purchase_month"].value_counts().sort_index()
    fig = px.line(
        x=sales_by_month.index, 
        y=sales_by_month.values, 
        labels={"x": "Bulan", "y": "Jumlah Transaksi"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Insight: Kota Tertinggi
with st.expander(" Kota dengan Transaksi Tertinggi"):
    city_sales = filtered_df.groupby("customer_city")["order_id"].count().sort_values(ascending=False).head(10)
    fig = px.bar(
        x=city_sales.index, 
        y=city_sales.values, 
        labels={"x": "Kota", "y": "Jumlah Transaksi"},
        color=city_sales.index
    )
    st.plotly_chart(fig, use_container_width=True)

# Insight: Rata-rata Waktu Pengiriman
with st.expander("Rata-rata Waktu Pengiriman"):
    filtered_df["delivery_time"] = (filtered_df["order_delivered_customer_date"] - filtered_df["order_purchase_timestamp"]).dt.days
    avg_delivery_time = filtered_df["delivery_time"].mean()
    st.metric("Rata-rata Waktu Pengiriman (hari)", f"{avg_delivery_time:.2f}")

    filtered_df["order_purchase_month"] = filtered_df["order_purchase_timestamp"].dt.to_period("M")
    avg_delivery_time_per_month = filtered_df.groupby("order_purchase_month")["delivery_time"].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    avg_delivery_time_per_month.plot(kind='line', marker='o', ax=ax)
    ax.set_title("Rata-rata Waktu Pengiriman per Bulan")
    ax.set_ylabel("Hari")
    ax.set_xlabel("Bulan")
    st.pyplot(fig)

# Kontak
st.markdown("---")
st.markdown(" Kontak & Proyek Lainnya: [GitHub ProfDARA](https://github.com/ProfDARA)")