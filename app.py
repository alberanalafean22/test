import streamlit as st
from googlesearch import search
import pandas as pd
import time
import random

# Konfigurasi Halaman
st.set_page_config(page_title="Solok Business Scraper", page_icon="📍", layout="wide")

st.title("📍 Instagram Business Finder - Kota Solok")
st.markdown("Mencari profil bisnis Instagram di **Kota Solok** berdasarkan kategori bisnis yang luas menggunakan Google Dorking.")

# --- DATA KATEGORI ---
# Daftar kategori yang diperluas
DEFAULT_CATEGORIES = [
    # F&B
    "Cafe", "Coffee Shop", "Resto", "Rumah Makan", "Catering", "Toko Kue", 
    "Bakery", "Angkringan", "Warung", "Frozen Food", "Kedai Kopi", "Dessert",
    
    # Fashion & Retail
    "Toko Baju", "Boutique", "Distro", "Thrift", "Toko Sepatu", "Toko Tas", 
    "Fashion", "Hijab", "Toko Mas", "Toko Perhiasan", "Toko Kain", "Jahit",
    
    # Beauty & Health
    "Salon", "Barbershop", "Nail Art", "Make Up Artist", "MUA", "Skincare", 
    "Klinik Kecantikan", "Spa", "Gym", "Fitness", "Apotek", "Optik",
    
    # Services & Events
    "Wedding Organizer", "Dekorasi", "Fotographer", "Photography", "Videography", 
    "Percetakan", "Undangan", "Laundry", "Rental Mobil", "Travel", "Jasa Kurir",
    
    # Hobbies & Others
    "Petshop", "Toko Tanaman", "Florist", "Toko Elektronik", "Gadget", "Service HP",
    "Toko Bangunan", "Interior", "Furniture", "Mebel", "Bengkel", "Variasi Motor",
    "Toko Mainan", "Baby Shop", "Oleh-oleh", "Gift Shop"
]

# --- SIDEBAR ---
with st.sidebar:
    st.header("Pengaturan Pencarian")
    
    # Pilihan Kategori
    st.write("**Filter Kategori**")
    use_all = st.checkbox("Gunakan Semua Kategori", value=True)
    
    if use_all:
        selected_categories = DEFAULT_CATEGORIES
    else:
        selected_categories = st.multiselect("Pilih Kategori Spesifik", DEFAULT_CATEGORIES, default=DEFAULT_CATEGORIES[:5])

    st.divider()
    
    # Parameter Search
    num_results_per_batch = st.slider("Jumlah Hasil per Batch", 5, 30, 10, help="Semakin banyak, semakin lama dan berisiko terkena limit.")
    delay = st.slider("Delay antar request (detik)", 3, 15, 6, help="Disarankan minimal 5 detik untuk menghindari blokir Google.")

# --- FUNGSI UTAMA ---
def chunks(lst, n):
    """Membagi list menjadi potongan-potongan kecil (chunks)"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if st.button("🔍 Mulai Pencarian Bisnis"):
    if not selected_categories:
        st.error("Harap pilih setidaknya satu kategori.")
    else:
        all_results = []
        seen_usernames = set()
        
        # Area Tampilan Progress
        status_text = st.empty()
        progress_bar = st.progress(0)
        results_container = st.container()

        # Strategi: Mengelompokkan kategori menjadi batch isi 5 agar query tidak terlalu panjang
        # Contoh query: site:instagram.com "Kota Solok" ("Cafe" OR "Resto" OR "Toko Kue")
        category_batches = list(chunks(selected_categories, 5))
        total_batches = len(category_batches)

        try:
            for batch_idx, batch in enumerate(category_batches):
                # Membangun Query Dorking dengan Operator OR
                or_string = " OR ".join([f'"{cat}"' for cat in batch])
                query = f'site:instagram.com "Kota Solok" ({or_string})'
                
                status_text.markdown(f"⏳ **Batch {batch_idx + 1}/{total_batches}**: Mencari `{or_string}`...")
                
                # Melakukan Pencarian
                search_results = search(query, num_results=num_results_per_batch, sleep_interval=delay, advanced=True)
                
                for res in search_results:
                    url = res.url
                    # Filter URL yang bukan profil utama
                    if "instagram.com/p/" in url or "instagram.com/reels/" in url or "instagram.com/stories/" in url:
                        continue
                        
                    # Ekstrak Username
                    # Membersihkan trailing slash
                    clean_url = url.rstrip('/')
                    username = clean_url.split('/')[-1]
                    
                    # Cek duplikasi
                    if username not in seen_usernames and username not in ["instagram.com", "explore"]:
                        seen_usernames.add(username)
                        
                        # Tebak kategori berdasarkan query batch saat ini (Simple heuristic)
                        guessed_category = ", ".join(batch)
                        
                        all_results.append({
                            "Username": f"@{username}",
                            "Nama Akun (Estimasi)": res.title.split("(@")[0].replace("• Instagram photos", "").strip(),
                            "Kategori Terkait": guessed_category,
                            "URL Profil": url,
                            "Lokasi": "Kota Solok"
                        })
                
                # Update Progress Bar
                progress_bar.progress((batch_idx + 1) / total_batches)
                
                # Jeda random antar batch untuk keamanan
                time.sleep(random.uniform(2, 5))

            # --- HASIL AKHIR ---
            if all_results:
                df = pd.DataFrame(all_results)
                
                st.success(f"✅ Selesai! Ditemukan {len(df)} bisnis unik.")
                
                # Tampilkan Tabel
                st.dataframe(df, use_container_width=True)
                
                # Tombol Download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data CSV",
                    data=csv,
                    file_name='data_bisnis_solok_lengkap.csv',
                    mime='text/csv',
                )
            else:
                st.warning("Tidak ditemukan hasil. Mungkin delay perlu diperlama atau Google membatasi sementara.")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.warning("Jika error '429 Too Many Requests', Google memblokir IP Anda sementara. Coba lagi nanti atau gunakan VPN.")
