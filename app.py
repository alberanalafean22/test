import streamlit as st
from googlesearch import search
import pandas as pd
import time
import random

st.set_page_config(page_title="Solok Business Scraper", page_icon="📍")

st.title("📍 Instagram Business Finder (Google Dorking)")
st.write("Mencari profil bisnis Instagram di Kota Solok tanpa login.")

# Input Form
with st.sidebar:
    keyword = st.text_input("Kata Kunci Tambahan", value="Cafe")
    location = "Kota Solok"
    num_results = st.slider("Jumlah Hasil", 5, 50, 10)
    delay = st.slider("Delay antar request (detik)", 2, 10, 5)

if st.button("Mulai Pencarian"):
    # Gabungkan query dorking
    query = f'site:instagram.com "{location}" "{keyword}"'
    
    st.info(f"Mencari: {query}")
    
    results = []
    
    try:
        # Proses Pencarian di Google
        # Menggunakan pause untuk menghindari bot detection dari Google
        search_results = search(query, num_results=num_results, sleep_interval=delay)
        
        progress_bar = st.progress(0)
        
        for i, url in enumerate(search_results):
            if "instagram.com/p/" in url or "instagram.com/reels/" in url:
                continue # Lewati jika link postingan, kita hanya butuh profil
            
            # Ekstrak Username dari URL
            username = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            
            results.append({
                "Nama Usaha": username.replace('.', ' ').replace('_', ' ').title(),
                "Username": f"@{username}",
                "URL Profil": url,
                "Lokasi": location
            })
            
            # Update Progress
            progress = (i + 1) / num_results
            progress_bar.progress(progress)
            time.sleep(random.uniform(1, 3)) # Random delay tambahan

        if results:
            df = pd.DataFrame(results)
            st.success(f"Ditemukan {len(df)} potensi bisnis!")
            
            # Tampilkan Data
            st.dataframe(df, use_container_width=True)
            
            # Tombol Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data sebagai CSV",
                data=csv,
                file_name=f'bisnis_solok_{keyword}.csv',
                mime='text/csv',
            )
        else:
            st.warning("Tidak ditemukan hasil. Coba ganti kata kunci.")

    except Exception as e:
        st.error(f"Terjadi kesalahan atau limit Google: {e}")
        st.info("Tips: Jika error 'Too Many Requests', tunggu beberapa menit atau coba deploy ke cloud.")
