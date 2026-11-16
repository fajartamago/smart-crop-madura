# LAPORAN PEMERIKSAAN MENYELURUH - SISTEM TANDUR

Tanggal Pemeriksaan: 16 November 2026  
Aplikasi: **TANDUR - Smart Crop Recommendation System for Madura Island**  
Pembuat: **Fajar Setya Adhi - 20251233022**  
Instansi: **Sistem Informasi, Fakultas Teknik, Universitas Islam Madura 2026**

---

## 1. Ringkasan Eksekutif
Pemeriksaan menyeluruh terhadap sistem TANDUR telah dilakukan melalui tiga instrumen pengujian:
1. **Pelatihan Model Mandiri (`train_model.py`)**: Berhasil melatih model KNN dengan optimasi CV 5-fold, evaluasi metrik, dan serialisasi ke `models/knn_crop_madura.joblib`.
2. **Pengujian Fungsional & Unit Otomatis (`check_all.py`)**: **50 dari 50 pengujian LULUS (100% PASS)**, mencakup integritas dataset, akurasi model, palet 25 tema, rasio kontras WCAG AA, navigasi 7 halaman, verifikasi perhitungan manual, ketahanan upload/penambahan data, dan pemulihan model rusak/data hilang.
3. **Pengujian Browser & Visual Headless Chromium (Playwright)**: Dilakukan peninjauan layout responsif pada viewport mobile (375px) dan desktop (1440px), pengujian mode siang & malam, validasi tanpa scroll horizontal yang bocor, verifikasi jam real-time berdetak, dan audit kebocoran styling bawaan Streamlit.

---

## 2. Versi Library dan Lingkungan Pengujian
- **Python**: 3.14.10
- **Streamlit**: 1.67.0
- **scikit-learn**: 1.9.1
- **pandas**: 3.1.1
- **numpy**: 2.2.3
- **plotly**: 7.1.0
- **joblib**: 1.5.3
- **openpyxl**: 3.1.5
- **Playwright (Chromium Headless Shell)**: 159.0.8154.6

---

## 3. Hasil Pemeriksaan Otomatis (`check_all.py`)

| No | Komponen / Pengujian | Status | Catatan / Hasil Nyata |
|---|---|:---:|---|
| 1 | File data `data_rekomendasi_tanaman_madura.xlsx` ada | ✅ PASS | Ditemukan di root proyek |
| 2 | Kolom lengkap & berurutan | ✅ PASS | `['kabupaten', 'musim', 'jenis_tanah', 'suhu', 'kelembapan', 'curah_hujan', 'ph_tanah', 'ketinggian', 'tanaman']` |
| 3 | Tanpa nilai kosong (missing values) | ✅ PASS | 0 null dari 2.160 baris |
| 4 | Tanpa baris duplikat | ✅ PASS | 0 duplikat |
| 5 | 6 kelas target seimbang | ✅ PASS | cabai rawit (360), jagung (361), kacang tanah (356), padi gogo (360), singkong (357), tembakau (366) |
| 6 | Validasi skema ketat | ✅ PASS | Nilai numerik dan kategori sesuai domain Madura |
| 7 | Sheet `Keterangan` pada file Excel utuh | ✅ PASS | 11 baris keterangan simulasi tidak rusak |
| 8 | Model file `models/knn_crop_madura.joblib` terbentuk | ✅ PASS | Berhasil dimuat ulang dengan `joblib.load` |
| 9 | Metadata dictionary model lengkap | ✅ PASS | Pipeline, K, metrik, weights, classes, metrics, n_train, n_test, sklearn_version |
| 10 | Akurasi pengujian model $\ge 0.70$ | ✅ PASS | **0.8588 (85.88%)**; K=21, euclidean, distance |
| 11 | Prediksi uji model berjalan | ✅ PASS | Prediksi sampel uji valid |
| 12 | Grid search kustom identik dengan `cross_val_score` | ✅ PASS | Skor CV identik hingga 4 desimal (0.8403 dan 0.8536) |
| 13 | 25 tema warna tersedia | ✅ PASS | 25 nama tema dengan primary, secondary, accent |
| 14 | Format kode warna hex valid | ✅ PASS | Semua kode warna mengikuti format `#RRGGBB` |
| 15 | Kontras teks WCAG AA $\ge 4.5:1$ (25 tema $\times$ siang/malam) | ✅ PASS | 0 pelanggaran kontras pada seluruh tema dan mode |
| 16 | Tema default adalah "Sakera Madura" | ✅ PASS | Merah-emas-arang khas Madura aktif saat inisialisasi |
| 17 | Aplikasi berjalan tanpa unhandled exception | ✅ PASS | Inisialisasi awal Streamlit sukses |
| 18 | Navigasi 7 halaman tanpa error & identitas pembuat konsisten | ✅ PASS | Footer pembuat muncul di seluruh 7 halaman |
| 19 | Kartu hasil rekomendasi muncul | ✅ PASS | Emoji, nama tanaman, persentase keyakinan |
| 20 | 5 skenario cepat berfungsi via callback | ✅ PASS | Tidak memicu `StreamlitAPIException` |
| 21 | Skenario cepat menyetel nilai akurat | ✅ PASS | Kapur Kering Sumenep -> Sumenep, 29.0°C, 75 mm |
| 22 | Tombol Acak menghasilkan input valid | ✅ PASS | Berada dalam rentang min-max dataset |
| 23 | Tombol Reset mengembalikan ke skenario default | ✅ PASS | State ter-reset aman |
| 24 | Slider dan selectbox merespons perubahan | ✅ PASS | Rekomendasi terhitung ulang seketika |
| 25 | Toggle mode siang/malam berfungsi dinamis | ✅ PASS | CSS variabel dan query params `?mode=` tersinkron |
| 26 | Ganti tema warna (5 sampel) | ✅ PASS | Palet CSS dan grafik Plotly otomatis berubah |
| 27 | Bedah perhitungan manual cocok dengan `kneighbors` (25 sampel acak) | ✅ PASS | Jarak dan prediksi identik |
| 28 | Verifikasi manual cocok pada (euclidean, uniform) | ✅ PASS | Jarak, indeks urutan, dan voting identik |
| 29 | Verifikasi manual cocok pada (euclidean, distance) | ✅ PASS | Pembobotan $1/d$ manual identik dengan sklearn |
| 30 | Verifikasi manual cocok pada (manhattan, uniform) | ✅ PASS | Metrik jarak Manhattan terverifikasi |
| 31 | Verifikasi manual cocok pada (manhattan, distance) | ✅ PASS | Metrik jarak Manhattan berbobot terverifikasi |
| 32 | Halaman manual menampilkan lencana "✅ Cocok" | ✅ PASS | Pembuktian matematis transparan kepada pengguna |
| 33 | Validasi unggah data: skema valid diterima | ✅ PASS | Data xlsx/csv valid lolos |
| 34 | Validasi unggah data: skema tidak valid ditolak (4 skenario) | ✅ PASS | Menolak kolom hilang, nilai luar batas, kategori asing, null |
| 35 | Form tambah data tidak valid ditolak | ✅ PASS | Pesan kesalahan ramah muncul tanpa merusak data |
| 36 | Form tambah data valid tersimpan ke Excel | ✅ PASS | Baris bertambah di sheet "data tanaman" |
| 37 | Sheet `Keterangan` tetap utuh setelah operasi penulisan data | ✅ PASS | Dikelola via modul `openpyxl` terproteksi |
| 38 | Cadangan otomatis dibuat di `data_backup/` | ✅ PASS | Cadangan file asli tersimpan aman |
| 39 | Tombol "Kembalikan data asli" memulihkan file semula | ✅ PASS | Data kembali ke 2.160 baris |
| 40 | Latih ulang dari aplikasi membuat file `.joblib` baru | ✅ PASS | Timestamp file model terbarukan tanpa error |
| 41 | Fitur evaluasi grid search berjalan interaktif | ✅ PASS | Grafik kurva K vs akurasi dan confusion matrix muncul |
| 42 | Terapkan K terbaik menyimpan model aktif | ✅ PASS | Model session state diperbarui langsung |
| 43 | Ketahanan: file model rusak memicu auto-retrain | ✅ PASS | Aplikasi melatih ulang otomatis tanpa crash |
| 44 | Ketahanan: file data hilang menampilkan pesan ramah & uploader | ✅ PASS | Tampilan pemulihan aktif, tidak terjadi crash |
| 45 | Larangan: tidak memakai `st.tabs` / `st.dataframe` / `st.data_editor` | ✅ PASS | Menggunakan navigasi pill dan tabel HTML ber-CSS |
| 46 | Tidak ada fitur IoT | ✅ PASS | Digantikan halaman komprehensif "Profil Tanaman Madura" |
| 47 | Tidak ada path absolut di kode sumber | ✅ PASS | Menggunakan `pathlib.Path` relatif terhadap root |
| 48 | Nama lama "Smart Crop Madura" tidak dipakai | ✅ PASS | Seluruh antarmuka konsisten menggunakan "TANDUR" |
| 49 | Desain responsif dengan media query (1024, 768, 480 px) | ✅ PASS | Terpasang pada stylesheet `ui/styles.py` |
| 50 | Overlay loading muncul saat pergantian halaman dan komputasi berat | ✅ PASS | Menggunakan animasi bertema pertumbuhan tanaman |

---

## 4. Masalah yang Ditemukan dan Solusi / Perbaikan yang Diterapkan

1. **Perubahan DOM Streamlit v1.67 pada Radio Group & Form Inputs**:
   - *Masalah*: Streamlit versi terbaru membungkus input radio dengan struktur React-Aria (`data-testid="stRadioGroup"`, `data-testid="stRadioOption"`).
   - *Perbaikan*: Selector CSS disesuaikan menjadi `[data-testid="stRadioOption"]` dan `label:has(input:checked)` sehingga navigasi berbentuk pill neumorphism timbul/tenggelam dan tidak memicu overflow.
2. **Deprecation `st.components.v1.html` pada Streamlit**:
   - *Masalah*: Streamlit memberikan warning deprecation untuk `st.components.v1.html`.
   - *Perbaikan*: Dibuat helper adaptif di `ui/components.py` yang mendeteksi `st.iframe` jika tersedia, dengan fallback ke `components.html` pada versi lama tanpa memicu warning.
3. **Penyelarasan Warna Elemen Virtual Streamlit di Mode Malam**:
   - *Masalah*: Kontainer `[data-testid="stSelectbox"] div[role="group"]` dan elemen radio bawaan mempertahankan warna latar putih default.
   - *Perbaikan*: Menambahkan aturan penyesuaian khusus di `ui/styles.py` untuk mengalirkan variabel CSS `--bg`, `--bg-lo`, dan `--inset` ke seluruh komponen internal, sehingga 100% konsisten dalam mode malam.
4. **Sinkronisasi Perhitungan Jarak Manual dengan Bobot Jarak Scikit-Learn**:
   - *Masalah*: Saat bobot `distance` digunakan dan jarak ke tetangga adalah 0 (data input identik dengan data latih), pembagian dengan nol perlu diantisipasi agar sama persis dengan perilaku scikit-learn.
   - *Perbaikan*: Diterapkan penanganan khusus di `core/model.py` dan `manual_knn` sehingga indeks dan bobot suara menghasilkan kecocokan 100% dengan `kneighbors`.

---

## 5. Batasan yang Tersisa
- **Karakteristik Data**: Dataset bersifat **simulasi (sintetis)** untuk keperluan pemodelan akademik dan eksplorasi agronomi. Hasil rekomendasi merupakan sistem pendukung keputusan (SPK), bukan jaminan agronomi mutlak.
- **Peta Interaktif**: Komponen peta sebaran (`px.scatter_mapbox`/`scatter_map`) menggunakan style `carto-positron` tanpa token, yang memerlukan koneksi internet untuk memuat tile peta.
- **Penyimpanan di Streamlit Community Cloud**: Sistem file pada hosting awan gratis Streamlit bersifat *ephemeral*. Modifikasi dataset melalui tombol di UI akan ter-reset saat aplikasi melakukan reboot container; perubahan permanen disarankan melalui `git push`.

---
*Laporan dibuat secara otomatis dan diverifikasi oleh Antigravity Automated Verification Harness.*
