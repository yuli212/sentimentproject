import feedparser
import urllib.parse

def fetch_news(keyword, max_results=5):
    """
    Fungsi untuk mengambil berita dari RSS Feed berdasarkan kata kunci.
    Menggunakan endpoint Google News (English) agar relevan dengan Amazon Comprehend.
    """
    print(f"[INFO] Memulai pencarian berita untuk kata kunci: '{keyword}'...")
    
    # 1. Format kata kunci agar aman untuk URL (misal: "us dollar" menjadi "us%20dollar")
    safe_keyword = urllib.parse.quote(keyword)
    
    # 2. API Endpoint RSS Feed (Menggunakan Google News berbahasa Inggris)
    rss_url = f"https://news.google.com/rss/search?q={safe_keyword}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        # 3. Eksekusi parsing XML ke dalam bentuk objek Python
        feed = feedparser.parse(rss_url)
        news_list = []
        
        # 4. Validasi jika berita tidak ditemukan
        if not feed.entries:
            print("[WARN] Tidak ada berita yang ditemukan.")
            return news_list

        # 5. Looping untuk mengekstrak elemen penting dari masing-masing berita
        for entry in feed.entries[:max_results]:
            news_item = {
                'title': entry.title,
                'link': entry.link,
                # Mengambil ringkasan, jika tidak ada, beri string kosong
                'summary': entry.get('description', '') 
            }
            news_list.append(news_item)
            
        print(f"[SUCCESS] Berhasil mengambil {len(news_list)} berita terbaru.")
        return news_list

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat mengambil RSS: {e}")
        return []

# ==========================================
# BLOK PENGUJIAN LOKAL (TESTING)
# ==========================================
# Kode di bawah ini HANYA akan berjalan jika kamu menjalankan file ini langsung di terminal
# dan tidak akan tereksekusi saat di-import oleh Lambda nanti.

if __name__ == "__main__":
    # Mari kita uji coba dengan kata kunci "dollar"
    test_keyword = "dollar"
    hasil_berita = fetch_news(test_keyword, max_results=3)
    
    print("\n--- HASIL PENCARIAN ---")
    for i, berita in enumerate(hasil_berita, 1):
        print(f"{i}. Judul : {berita['title']}")
        print(f"   Link  : {berita['link']}")
        print(f"   Isi   : {berita['summary'][:100]}...\n") # Potong summary agar terminal tidak penuh