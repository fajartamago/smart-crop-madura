# Panduan Deploy TANDUR (GitHub + Streamlit Community Cloud)

## A. Menghubungkan ke GitHub (akun: fajar.list88@gmail.com)
1. Masuk/daftar di https://github.com dengan email `fajar.list88@gmail.com` (pastikan email terverifikasi di *Settings > Emails*).
2. Pasang Git (https://git-scm.com) lalu atur identitas:
   ```bash
   git config --global user.name "Fajar Setya Adhi"
   git config --global user.email "fajar.list88@gmail.com"
   ```
   Email ini harus sama dengan email di akun GitHub agar commit tercatat sebagai kontribusi Anda.
3. Buat repository baru di GitHub: nama `tandur-madura`, **Public**, JANGAN centang "Add README/.gitignore" (repo kosong).
4. Di folder proyek, jalankan:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: TANDUR - Smart Crop Recommendation System for Madura Island"
   git branch -M main
   git remote add origin https://github.com/<USERNAME_GITHUB>/tandur-madura.git
   git push -u origin main
   ```
   (ganti `<USERNAME_GITHUB>` dengan username GitHub Anda).
5. Autentikasi saat push: gunakan jendela login GitHub yang muncul (Git Credential Manager), atau Personal Access Token
   (GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic) > centang `repo`) sebagai pengganti
   password, atau jalankan `gh auth login` bila memakai GitHub CLI.
6. Alternatif di Antigravity: buka panel *Source Control* > *Initialize Repository* > *Commit* > *Publish Branch/Publish to GitHub* >
   login ke akun GitHub di browser.
7. Pastikan di GitHub terlihat: `app.py`, `requirements.txt`, `data_rekomendasi_tanaman_madura.xlsx`,
   `models/knn_crop_madura.joblib`, folder `.streamlit`.
8. Update berikutnya: `git add .` ; `git commit -m "pesan"` ; `git push`.

## B. Menghubungkan ke Streamlit Community Cloud (streamlit.app)
1. Buka https://share.streamlit.io lalu **Continue with GitHub** dan login dengan akun GitHub yang sama.
2. Authorize Streamlit untuk mengakses repository (boleh pilih hanya repo `tandur-madura`).
3. Klik **Create app** > **Deploy a public app from GitHub**.
4. Isi: Repository = `<USERNAME_GITHUB>/tandur-madura` | Branch = `main` | Main file path = `app.py`.
5. (Opsional) App URL: `tandur-madura` -> https://tandur-madura.streamlit.app (atau `tandur` bila tersedia).
6. **Advanced settings** > Python version 3.11 atau 3.12 > **Deploy**. Tunggu instalasi selesai (beberapa menit).
7. Setiap `git push` ke branch `main` akan otomatis memperbarui app. Gunakan menu "⋮" > *Reboot app* bila perlu.
8. Masalah umum:
   - (a) `ModuleNotFoundError` -> periksa `requirements.txt`.
   - (b) file xlsx tidak ditemukan -> pastikan ikut ter-commit dan nama persis sama (huruf kecil semua).
   - (c) joblib gagal dimuat karena beda versi scikit-learn -> app melatih ulang otomatis.
   - (d) perubahan data lewat app tidak permanen setelah reboot -> ubah file lalu push ke GitHub.

---
© 2026 Fajar Setya Adhi - 20251233022 | Sistem Informasi, Fakultas Teknik, Universitas Islam Madura
