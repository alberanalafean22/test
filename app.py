import streamlit as st
from duckduckgo_search import DDGS
import pandas as pd
import time
import random

# Konfigurasi Halaman
st.set_page_config(page_title="Solok Business Scraper (DDG Mode)", page_icon="📍", layout="centered")

st.title("📍 Instagram Business Finder - Solok")
st.caption("Menggunakan DuckDuckGo Engine (Lebih Aman dari Blokir)")

# --- DATA KATEGORI ---
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
    selected_category = st.selectbox("Pilih Kategori Bisnis:", CATEGORIES)
    st.divider()
    num_results = st.slider("Target Jumlah Hasil", 5, 50, 20)
    # DuckDuckGo lebih cepat, delay kecil tidak masalah
    delay = st.slider("Jeda per request (detik)", 0.5, 3.0, 1.0)

# --- TOMBOL EKSEKUSI ---
if st.button(f"🔍 Cari: {selected_category}"):
    st.info(f"Mencari data '{selected_category}' di Kota Solok via DuckDuckGo...")
    
    # Query disesuaikan untuk DuckDuckGo
    query = f'site:instagram.com "Kota Solok" "{selected_category}"'
    
    results_data = []
    seen_usernames = set()
    
    # Progress Bar UI
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Menggunakan Context Manager DDGS agar session tertutup rapi
        with DDGS() as ddgs:
            # max_results di DDGS langsung mengambil banyak sekaligus, jadi lebih cepat
            # region='id-id' memprioritaskan hasil Indonesia
            ddg_results = list(ddgs.text(query, region='id-id', max_results=num_results))
            
            total_found = len(ddg_results)
            
            if total_found == 0:
                st.warning("DuckDuckGo tidak menemukan hasil. Coba ganti kategori.")
            
            for i, res in enumerate(ddg_results):
                url = res['href']
                title = res['title']
                
                # Filter URL non-profil (sama seperti sebelumnya)
                if any(x in url for x in ["/p/", "/reels/", "/stories/", "/explore/", "/tags/"]):
                    continue

                # Bersihkan URL
                clean_url = url.split("?")[0].rstrip('/')
                username = clean_url.split('/')[-1]
                
                # Cek Duplikasi
                if username not in seen_usernames and username != "instagram.com":
                    seen_usernames.add(username)
                    
                    # Bersihkan Title
                    clean_title = title.split("(@")[0].replace("• Instagram photos", "").strip()
                    if "..." in clean_title: # Jika title terpotong, pakai username
                        display_name = f"{username} (Cek Link)"
                    else:
                        display_name = clean_title

                    results_data.append({
                        "Nama Bisnis": display_name,
                        "Username": f"@{username}",
                        "Kategori": selected_category,
                        "Link Instagram": clean_url,
                        "Sumber": "DuckDuckGo"
                    })
                    
                    status_text.text(f"Ditemukan: {username}")
                
                # Update progress
                progress = min((i + 1) / total_found, 1.0)
                progress_bar.progress(progress)
                
                # Jeda sopan (meski DDG lebih longgar)
                time.sleep(random.uniform(delay/2, delay))

        # --- TAMPILKAN HASIL ---
        if results_data:
            df = pd.DataFrame(results_data)
            st.success(f"✅ Selesai! Ditemukan {len(df)} akun unik.")
            st.dataframe(df, use_container_width=True)
            
            # Buat nama file aman (hapus spasi)
            filename = f"solok_{selected_category.lower().replace(' ', '_')}.csv"
            
            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=filename,
                mime='text/csv',
            )
        else:
            st.warning("Hasil ditemukan tapi semua terfilter (mungkin bukan link profil).")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.caption("Jika error 'Ratelimit', tunggu 1-2 menit lalu coba lagi.")
