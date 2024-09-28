import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    # Resample DataFrame untuk mendapatkan order harian dan revenuenya
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        'order_id': 'nunique',    
        'payment_value': 'sum'      
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_payment_type_df(df):
    # Menghitung jumlah order berdasarkan payment_type
    payment_type_df = df.groupby("payment_type").order_id.count().reset_index()
    payment_type_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return payment_type_df

def create_sum_order_categories_df(df):
    # Menghitung total penjualan berdasarkan kategori produk
    sum_order_categories_df = main_df.groupby("product_category_name_english").size().reset_index(name='total_sales')
    sum_order_categories_df.rename(columns={"order_item_id": "total_ordered_items"}, inplace=True)
    return sum_order_categories_df
    
def create_bystate_df(df):
    # Mengelompokkan data berdasarkan 'customer_state' dan menghitung jumlah unik customer berdasarkan 'customer_unique_id'
    bystate_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    # Mengganti nama kolom agar lebih deskriptif
    bystate_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)

    return bystate_df
def create_bycity_df(df):
    # Mengelompokkan data berdasarkan 'customer_city' dan menghitung jumlah unik customer berdasarkan 'customer_unique_id'
    bycity_df = df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
    # Mengganti nama kolom agar lebih deskriptif
    bycity_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)

    return bycity_df
def create_rfm_df(df):
    # Mengelompokkan data berdasarkan 'customer_unique_id'
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_approved_at": "max",  # Mengambil tanggal order terakhir
        "order_id": "nunique",        # Menghitung jumlah order unik
        "payment_value": "sum"        # Menghitung total nilai pembayaran
    })

    # Mengganti nama kolom untuk RFM
    rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
    # Mengonversi timestamp menjadi tanggal
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    # Menghitung tanggal terbaru dalam data
    recent_date = df["order_approved_at"].dt.date.max()
    # Menghitung Recency
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    # Menghapus kolom max_order_timestamp jika tidak diperlukan
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df
all_df = pd.read_csv("dashboard\main_data.csv")
datetime_columns = ["order_approved_at", "order_delivered_customer_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Mengambil tanggal minimum dan maksimum dari kolom order
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.markdown('<h2 style="text-align: left;">Welcome to Dashboard</h2>', unsafe_allow_html=True)
    st.image("dashboard\Logo.png", width=230)
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Masukkan Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    st.write("**Created by:** Navy Nurlyn Ajrina")
    st.write("**Location:** UPN Veteran Jawa Timur")

# Memfilter DataFrame berdasarkan rentang tanggal yang dipilih
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]
daily_orders_df = create_daily_orders_df(main_df)
payment_type_df = create_payment_type_df(main_df)
sum_order_categories_df = create_sum_order_categories_df(main_df)
bystate_df = create_bystate_df(main_df)
bycity_df = create_bycity_df(main_df)
payment_type_df_sorted = payment_type_df.sort_values(by='order_count', ascending=False)
rfm_df = create_rfm_df(main_df)

st.header("Brazil's E-Commerce Dashboard :sparkles:")
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='en_US')
    st.metric("Total Revenue (USD)", value=total_revenue)

# Visualisasi jumlah order harian
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9" 
)
ax.tick_params(axis='y', labelsize=20, colors='white') 
ax.tick_params(axis='x', labelsize=15, colors='white')  
# Mengatur judul dan label sumbu
ax.set_title('Daily Order Quantity', fontsize=28, color='white')  
ax.set_xlabel('Tanggal', fontsize=20, color='white')  
ax.set_ylabel('Jumlah Order', fontsize=20, color='white') 
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_visible(True)
ax.set_facecolor('black')  
fig.patch.set_facecolor('black') 

st.pyplot(fig)

# Visualisasi kategori produk dengan penjualan terbaik dan terburuk
st.subheader("Best & Worst Performing Product Categories")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 25))
# Warna untuk kategori terbaik dan terburuk
top_colors_best = ['#00CCDD'] * 5  
top_colors_worst = ['#FF4191'] * 5 
other_color= '#D3D3D3' 
colors_best = top_colors_best + [other_color] * (len(sum_order_categories_df) - 5)
colors_worst = top_colors_worst + [other_color] * (len(sum_order_categories_df) - 5)

# Kategori dengan penjualan terbaik
best_categories = sum_order_categories_df.sort_values(by="total_sales", ascending=False).head(10)
sns.barplot(x="total_sales", y="product_category_name_english", data=best_categories, palette=colors_best, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=40, color='white')
ax[0].set_title("Best Performing Product Categories", loc="center", fontsize=50, color='white')
ax[0].tick_params(axis='y', labelsize=35, colors='white')
ax[0].tick_params(axis='x', labelsize=30, colors='white')
ax[0].spines['top'].set_visible(False)
ax[0].spines['right'].set_visible(False)
ax[0].spines['left'].set_visible(False)
ax[0].spines['bottom'].set_visible(False)

# Kategori dengan penjualan terburuk
worst_categories = sum_order_categories_df.sort_values(by="total_sales").head(10)
sns.barplot(x="total_sales", y="product_category_name_english", data=worst_categories, palette=colors_worst, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30, color='white')
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Categories", loc="center", fontsize=50, color='white')
ax[1].tick_params(axis='y', labelsize=35, colors='white')
ax[1].tick_params(axis='x', labelsize=30, colors='white')
ax[1].spines['top'].set_visible(False)
ax[1].spines['right'].set_visible(False)
ax[1].spines['left'].set_visible(False)
ax[1].spines['bottom'].set_visible(False)
ax[0].set_facecolor('black') 
ax[1].set_facecolor('black') 
fig.patch.set_facecolor('black')  

st.pyplot(fig)

# Customer Demographic Section
st.subheader("Customer Demographics")
 # Top 10 State by Number of Customers
fig_state, ax_state = plt.subplots(figsize=(12, 6))
sns.barplot(x="customer_count", y="customer_state", data=bystate_df.sort_values(by="customer_count", ascending=False).head(10), palette='viridis', ax=ax_state, width=0.8)  # Adjust the width parameter here
ax_state.set_title('Number of Customers by State', fontsize=24)
ax_state.set_xlabel('Number of Customers', fontsize=20)
ax_state.set_ylabel('State', fontsize=20)
ax_state.tick_params(axis='y', labelsize=15)
ax_state.tick_params(axis='x', labelsize=15)
st.pyplot(fig_state)

# Top 10 Cities by Number of Customers
top_10_cities = bycity_df.sort_values(by="customer_count", ascending=False).head(10)
fig_top10, ax_top10 = plt.subplots(figsize=(12, 6))
sns.barplot(x="customer_count", y="customer_city", data=top_10_cities, palette="magma", ax=ax_top10)
ax_top10.set_title("Top 10 Cities by Number of Customers", fontsize=24)
ax_top10.set_xlabel("Number of Customers", fontsize=20)
plt.yticks(rotation=45, ha='right') 
ax_top10.set_ylabel("City", fontsize=20)
ax_top10.tick_params(axis='y', labelsize=15)
ax_top10.tick_params(axis='x', labelsize=15)
st.pyplot(fig_top10)

# Payment Type Visualization
st.subheader("Number of Orders by Payment Type")
top_payment_type = payment_type_df_sorted.iloc[0]['payment_type'] 
colors = ['#00CCDD' if payment_type == top_payment_type else '#00CCDD' for payment_type in payment_type_df_sorted['payment_type']]
fig_payment, ax_payment = plt.subplots(figsize=(12, 6))
sns.barplot(
    x="payment_type", 
    y="order_count", 
    data=payment_type_df_sorted, 
    palette=colors, 
    ax=ax_payment
)
ax_payment.set_title('Number of Orders by Payment Type', fontsize=24, color='white')
ax_payment.set_xlabel('Payment Type', fontsize=20, color='white')
ax_payment.set_ylabel('Number of Orders', fontsize=20, color='white')
ax_payment.tick_params(axis='y', labelsize=15, colors='white')
ax_payment.tick_params(axis='x', labelsize=15, colors='white')
ax_payment.spines['top'].set_visible(False)
ax_payment.spines['right'].set_visible(False)
ax_payment.spines['left'].set_visible(True)
ax_payment.spines['bottom'].set_visible(True)
ax_payment.set_facecolor('black') 
fig_payment.patch.set_facecolor('black')  
# Menampilkan plot di Streamlit
st.pyplot(fig_payment)

st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    # Hitung dan tampilkan nilai rata-rata Recency dalam hari
    avg_recency = round(rfm_df['recency'].mean(), 1)  # Rata-rata berapa hari sejak pembelian terakhir
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    # Hitung dan tampilkan nilai rata-rata Frequency (berapa kali pembelian)
    avg_frequency = round(rfm_df['frequency'].mean(), 2)  # Rata-rata jumlah pembelian per pelanggan
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    # Hitung dan tampilkan nilai rata-rata Monetary dalam IDR
    avg_monetary = format_currency(rfm_df['monetary'].mean(), "USD", locale='en_US')  # Rata-rata nilai total transaksi per pelanggan
    st.metric("Average Monetary (USD)", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#7CF5FF", "#7CF5FF", "#7CF5FF", "#7CF5FF", "#7CF5FF"]
rfm_non_zero_recency = rfm_df[rfm_df['recency'] > 0]

# Top 5 customer by Recency
sns.barplot(y="recency", x="customer_unique_id", 
            data=rfm_non_zero_recency.sort_values(by="recency", ascending=True).head(5), 
            palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=30, color='white')
ax[0].set_title("Top 5 Customers by Recency", fontsize=35, color='white')
ax[0].tick_params(axis='y', labelsize=30, colors='white')
ax[0].tick_params(axis='x', rotation=55, labelsize=25, colors='white')
ax[0].spines['top'].set_visible(False)
ax[0].spines['right'].set_visible(False)
ax[0].spines['left'].set_visible(True) 
ax[0].spines['bottom'].set_visible(True) 

# Top 5 customer by Frequency (most frequent)
sns.barplot(y="frequency", x="customer_unique_id", 
            data=rfm_df.sort_values(by="frequency", ascending=False).head(5), 
            palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=30, color='white')
ax[1].set_title("Top 5 Customers by Frequency", loc="center", fontsize=35, color='white')
ax[1].tick_params(axis='y', labelsize=30, colors='white')
ax[1].tick_params(axis='x', rotation=55, labelsize=25, colors='white')
ax[1].spines['top'].set_visible(False)
ax[1].spines['right'].set_visible(False)
ax[1].spines['left'].set_visible(True)   
ax[1].spines['bottom'].set_visible(True) 

# Top 5 customer by Monetary (highest spending)
sns.barplot(y="monetary", x="customer_unique_id", 
            data=rfm_df.sort_values(by="monetary", ascending=False).head(5), 
            palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer ID", fontsize=30, color='white')
ax[2].set_title("Top 5 Customers by Monetary", loc="center", fontsize=35, color='white')
ax[2].tick_params(axis='y', labelsize=30, colors='white')
ax[2].tick_params(axis='x', rotation=55, labelsize=25, colors='white')
ax[2].spines['top'].set_visible(False)
ax[2].spines['right'].set_visible(False)
ax[2].spines['left'].set_visible(True) 
ax[2].spines['bottom'].set_visible(True) 

ax[0].set_facecolor('black')
ax[1].set_facecolor('black')
ax[2].set_facecolor('black')
fig.patch.set_facecolor('black')

st.pyplot(fig)

st.caption('Copyright (c) Navy Nurlyn Ajrina 2024')