# 🌱 TANDUR

**Teknologi Analisis dan Rekomendasi untuk Dunia Usaha Pertanian Madura**

**SMART CROP RECOMMENDATION SYSTEM FOR MADURA ISLAND**
Sistem Pendukung Keputusan Rekomendasi Tanaman Berbasis K-Nearest Neighbors (KNN)

**Pembuat:** Fajar Setya Adhi - 20251233022
**Instansi:** Sistem Informasi, Fakultas Teknik, Universitas Islam Madura 2026

> "Tandur" dalam bahasa Madura/Jawa berarti *menanam*.

TANDUR adalah aplikasi web Streamlit yang merekomendasikan tanaman (jagung, tembakau, kacang tanah,
cabai rawit, singkong, padi gogo) berdasarkan kabupaten, musim, jenis tanah, suhu, kelembapan, curah
hujan, pH tanah, dan ketinggian di Pulau Madura. Metode: **K-Nearest Neighbors**
(`scikit-learn.KNeighborsClassifier`).

> ⚠️ **Catatan kejujuran:** data bersifat **simulasi (sintetis)**, bukan hasil pengukuran lapangan.
> Hasil adalah saran pendukung keputusan, bukan keputusan akhir.

## Fitur
7 halaman: Dashboard & Rekomendasi · Visualisasi 3D & 2D · Bedah Perhitungan Manual · Evaluasi & Optimasi K ·
Manajemen Dataset · Profil Tanaman Madura · Tentang & Panduan. Tampilan neumorphism lembut, 25 tema warna,
mode siang/malam, maskot "Si Odheng", jam real-time WIB, responsif (desktop/tablet/mobile).

## Menjalankan secara lokal
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python train_model.py              # opsional: melatih & menyimpan models/knn_crop_madura.joblib
streamlit run app.py
```
Jika `.joblib` belum ada / rusak / beda versi scikit-learn, aplikasi melatih ulang otomatis.

Pemeriksaan otomatis: `python check_all.py` (hasil lengkap di [LAPORAN_PEMERIKSAAN.md](LAPORAN_PEMERIKSAAN.md)).

## Struktur proyek
```
app.py                  aplikasi utama (state, sidebar, navigasi, routing)
core/                   data.py (xlsx & validasi), model.py (KNN, grid search, hitung manual),
                        themes.py (25 tema + kontras), info.py (konten tanaman)
ui/                     styles.py (CSS), components.py (maskot, loading, tabel HTML, plotly), pages.py (7 halaman)
train_model.py          melatih KNN & menyimpan .joblib
check_all.py            pemeriksaan otomatis (PASS/FAIL)
data_rekomendasi_tanaman_madura.xlsx   dataset (sheet "data tanaman" + "Keterangan")
models/knn_crop_madura.joblib          model terlatih
.streamlit/config.toml  konfigurasi
PANDUAN_DEPLOY.md       panduan GitHub + Streamlit Community Cloud
```

## Keputusan desain (diambil otomatis & dicatat)
- Banner berupa container ber-key; jam real-time (JavaScript, zona Asia/Jakarta) diletakkan di dalam kartu banner.
- Riwayat rekomendasi otomatis bertambah saat input di Dashboard berubah (maks 50, `session_state`).
- Model menyimpan salinan data latih (`train_df`) di `.joblib` agar halaman "Bedah Perhitungan Manual" konsisten dengan model.
- Penambahan/penggantian data membuat cadangan otomatis di `data_backup/` (dipakai tombol "Kembalikan data asli").
- Tema & mode tersimpan di `st.query_params` (`?theme=...&mode=...`).
- Variabel lingkungan opsional untuk pengujian: `TANDUR_DATA_FILE`, `TANDUR_MODEL_FILE`, `TANDUR_LOAD_SECONDS`.
- Streamlit baru memakai `st.iframe` untuk jam (fallback ke `components.html` di versi lama).
- Peta dasar (`carto-positron`) membutuhkan koneksi internet.

---
© 2026 Fajar Setya Adhi - 20251233022 | Sistem Informasi, Fakultas Teknik, Universitas Islam Madura
