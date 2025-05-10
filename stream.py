import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Title
st.title("Dashboard Analisis Data E-Commerce")

# Load merged data
@st.cache_data
def load_data():
    merged_url = "https://raw.githubusercontent.com/ProfDARA/Proyek_Analisis_Data/refs/heads/master/merged_df.csv"
    merged = pd.read_csv(merged_url)
    return merged

merged_df = load_data()

# Insight Umum
st.markdown("""
**Insight data E-Commerce Brazil:**
- Kategori rumah tangga mendominasi pasar produk seperti cama, mesa, banho (perlengkapan tidur, meja, dan kamar mandi), moveis_decoracao (furnitur & dekorasi), serta utilidades_domesticas menunjukkan bahwa kebutuhan rumah tangga menjadi prioritas bagi banyak pelanggan. Ini bisa menunjukkan tren bahwa konsumen lebih fokus pada peningkatan kenyamanan rumah.
- Kesehatan & kecantikan memiliki permintaan tinggi, beleza_saude (kecantikan & kesehatan) masuk dalam posisi ketiga, menunjukkan tingginya minat pelanggan terhadap produk perawatan diri dan kesehatan. Ini bisa menjadi peluang besar untuk promosi dan bundling produk dengan kategori lain seperti olahraga dan aksesoris teknologi.
- Berdasar grafik, Bulan penjualan tertinggi ada pada bulan 5 atau Mei
- São Paulo sangat dominan dalam jumlah pelanggan dan lokasi dengan nilai 26114, sangat ideal untuk pusat distribusi.
- Distribusi pelanggan menyebar tapi tidak merata → pendekatan logistik & pemasaran harus mempertimbangkan hal ini.
- Dapat disimpulkan kalau rata-rata pengiriman adalah 11 Hari
""")

# Tampilkan Data
st.subheader("Data Gabungan (merged_df.csv)")
st.dataframe(merged_df.head())


# Peta Sebaran Geolokasi
st.markdown("### Peta Sebaran Geospasial")
if "geolocation_lat" in merged_df.columns and "geolocation_lng" in merged_df.columns:
    fig = px.scatter_mapbox(merged_df.dropna(subset=["geolocation_lat", "geolocation_lng"]).sample(1000),
                            lat="geolocation_lat", lon="geolocation_lng", zoom=2, height=500)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

# Jawaban Pertanyaan
st.markdown("#### 1. Produk apa yang paling banyak dibeli pelanggan?")
top_products = merged_df["product_category_name"].value_counts().head(10)
fig = px.bar(x=top_products.index, y=top_products.values, labels={"x": "Kategori Produk", "y": "Jumlah Pembelian"})
st.plotly_chart(fig)
st.info("Kategori rumah tangga seperti cama, mesa, banho (perlengkapan tidur, meja, dan kamar mandi), moveis_decoracao (furnitur & dekorasi), dan utilidades_domesticas mendominasi pasar. Ini menunjukkan bahwa pelanggan cenderung berbelanja untuk kebutuhan rumah dan peningkatan kenyamanan tempat tinggal.")

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
st.info("Bulan Mei memiliki jumlah penjualan tertinggi, menunjukkan adanya pola musiman atau faktor tertentu yang meningkatkan transaksi pada periode ini. Bisa jadi ini terkait dengan promosi khusus, perubahan cuaca, atau adanya momen penting yang meningkatkan minat belanja.")

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
st.info("São Paulo adalah kota dengan volume transaksi terbesar, dengan 26,114 pesanan. Ini menjadikannya sebagai lokasi strategis untuk pusat distribusi dan pemasaran, karena konsentrasi pelanggan yang tinggi bisa meningkatkan efisiensi operasional.")

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
st.info("Rata-rata waktu pengiriman adalah sekitar 12 Hari. Ini menandakan bahwa kecepatan pengiriman masih bisa dioptimalkan untuk meningkatkan kepuasan pelanggan, terutama jika dibandingkan dengan standar pengiriman yang lebih cepat di industri e-commerce.")
