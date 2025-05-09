import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Title
st.title("Dashboard Analisis Data E-Commerce")

# Sidebar
st.sidebar.title("Navigasi")

# Load merged data
@st.cache_data
def load_data():
    merged_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/merged_df.csv"
    merged = pd.read_csv(merged_url)
    return merged

merged_df = load_data()

# Tampilkan Data
st.subheader("Data Gabungan (merged_df.csv)")
st.dataframe(merged_df.head())

st.markdown("#### 1. Produk apa yang paling banyak dibeli pelanggan?")
top_products = merged_df["product_category_name"].value_counts().head(10)
fig = px.bar(x=top_products.index, y=top_products.values, labels={"x": "Kategori Produk", "y": "Jumlah Pembelian"})
st.plotly_chart(fig)

st.markdown("#### 2. Kapan waktu penjualan tertinggi terjadi?")
merged_df["order_purchase_timestamp"] = pd.to_datetime(merged_df["order_purchase_timestamp"])
merged_df["order_purchase_month"] = merged_df["order_purchase_timestamp"].dt.month
sales_by_month = merged_df["order_purchase_month"].value_counts().sort_index()
max_month = sales_by_month.idxmax()
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=sales_by_month.index, y=sales_by_month.values, ax=ax)
ax.set_title("Penjualan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Penjualan")
ax.text(max_month, sales_by_month.max(), f"Max: Bulan {max_month}", ha="center", va="bottom", color="red")
st.pyplot(fig)

st.markdown("#### 3. Kota mana yang memiliki volume transaksi tertinggi?")
city_sales = merged_df.groupby("customer_city")["order_id"].count().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 6))
barplot = sns.barplot(x=city_sales.index, y=city_sales.values, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.set_title("Top 10 Kota dengan Volume Transaksi Tertinggi")
ax.set_xlabel("Kota")
ax.set_ylabel("Jumlah Transaksi")
max_value = city_sales.max()
max_index = city_sales.idxmax()
barplot.text(city_sales.index.get_loc(max_index), max_value + 100, f"{max_value}", ha='center', va='bottom', color='black', fontweight='bold')
st.pyplot(fig)

st.markdown("#### 4. Berapa rata-rata waktu pengiriman dari pembelian ke penerimaan?")
merged_df["order_delivered_customer_date"] = pd.to_datetime(merged_df["order_delivered_customer_date"], errors="coerce")
merged_df["delivery_time"] = (merged_df["order_delivered_customer_date"] - merged_df["order_purchase_timestamp"]).dt.days
avg_delivery_time = merged_df["delivery_time"].mean()
st.write(f"Rata-rata waktu pengiriman: {avg_delivery_time:.2f} hari")

merged_df["order_purchase_month"] = merged_df["order_purchase_timestamp"].dt.to_period("M")
avg_delivery_time_per_month = merged_df.groupby("order_purchase_month")["delivery_time"].mean()
fig, ax = plt.subplots(figsize=(12, 6))
avg_delivery_time_per_month.plot(kind='line', marker='o', ax=ax)
ax.set_title("Rata-rata Waktu Pengiriman per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Rata-rata Waktu Pengiriman (hari)")
ax.grid(True)
st.pyplot(fig)