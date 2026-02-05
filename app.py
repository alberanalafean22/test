import streamlit as st
from googlesearch import search
import pandas as pd
import time
import random

# Konfigurasi Halaman
st.set_page_config(page_title="Solok Business Scraper (Safe Mode)", page_icon="📍", layout="centered")

st.title("📍 Instagram Business Finder - Solok")
st.caption("Mode Aman: Satu Kategori per Pencarian untuk menghindari Error 429.")

# --- DATA KATEGORI ---
# Kita urutkan agar mudah dicari di dropdown
CATEGORIES = sorted([
    "Cafe", "Coffee Shop", "Resto", "Rumah Makan", "Catering", "Toko Kue", 
    "Bakery", "Angkringan", "Warung", "Frozen Food", "Kedai Kopi", "Dessert",
    "Toko Baju", "Boutique", "Distro", "Thrift", "Toko Sepatu", "Toko Tas", 
    "Fashion", "Hijab", "Toko Mas", "Toko Perhiasan", "Toko Kain", "Jahit",
    "Salon", "Barbershop", "Nail Art", "Make Up Artist", "MUA", "Skincare", 
    "Klinik Kecantikan", "Spa", "Gym", "Fitness", "Apotek", "Optik",
    "Wedding Organizer", "Dekorasi", "Fotographer", "Photography", "Videography", 
    "Percetakan", "Undangan", "Laundry", "Rental Mobil", "Travel", "Jasa Kurir",
    "Petshop", "Toko Tanaman", "Florist", "Toko Elektronik", "Gadget", "Service HP",
    "Toko Bangunan", "Interior", "Furniture", "Mebel", "Bengkel", "Variasi Motor",
    "Toko Mainan", "Baby Shop", "Oleh-oleh", "Gift Shop"
])

# --- SIDEBAR ---
with st.sidebar:
    st.header("Pengaturan")
    
    # Dropbox Pilihan Kategori (Hanya Satu)
    selected_category = st.selectbox("Pilih Kategori Bisnis:", CATEGORIES)
    
    st.divider()
    
    # Parameter Search
    num_results = st.slider("Jumlah Hasil Maksimal", 5, 50, 10)
    delay = st.slider("Jeda per hasil (detik)", 2.0, 10.0, 5.0, help="Semakin tinggi semakin aman dari blokir.")

# --- TOMBOL EKSEKUSI ---
if st.button(f"🔍 Cari: {selected_category}"):
    st.info(f"Sedang mencari data untuk kategori: **{selected_category}** di Kota Solok...")
    
    # Query yang lebih sederhana dan spesifik
    query = f'site:instagram.com "Kota Solok" "{selected_category}"'
    
    results = []
    seen_usernames = set()
    
    # Progress Bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Melakukan pencarian
        # sleep_interval sangat penting untuk menghindari 429
        search_iterator = search(query, num_results=num_results, sleep_interval=delay, advanced=True)
        
        for i, res in enumerate(search_iterator):
            url = res.url
            
            # Filter URL non-profil
            if any(x in url for x in ["/p/", "/reels/", "/stories/", "/explore/", "/tags/"]):
                continue

            # Bersihkan URL untuk dapat username
            clean_url = url.rstrip('/')
            username = clean_url.split('/')[-1]
            
            # Cek Duplikasi
            if username not in seen_usernames and username != "instagram.com":
                seen_usernames.add(username)
                
                # Coba ambil nama dari Title Page
                try:
                    page_title = res.title.split("(@")[0].replace("• Instagram photos", "").strip()
                except:
                    page_title = username

                results.append({
                    "Nama Bisnis (Estimasi)": page_title,
                    "Username": f"@{username}",
                    "Kategori": selected_category,
                    "Link Instagram": url,
                    "Sumber": "Google Search"
                })
                
                status_text.text(f"Ditemukan: {username}")
            
            # Update Progress (Estimasi saja karena iterator tidak punya len)
            current_progress = min((i + 1) / num_results, 1.0)
            progress_bar.progress(current_progress)

        # --- HASIL ---
        if results:
            df = pd.DataFrame(results)
            st.success(f"✅ Selesai! Ditemukan {len(df)} akun untuk kategori {selected_category}.")
            
            # Tampilkan Tabel
            st.dataframe(df, use_container_width=True)
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'solok_{selected_category.lower().replace(" ", "_")}.csv',
                mime='text/csv',
            )
        else:
            st.warning("Tidak ditemukan hasil. Coba kategori lain atau Google mungkin sedang membatasi query.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.write("Tips: Jika masih error 429, silakan pause selama 15-30 menit atau ganti koneksi internet (Airplane mode on/off).")
