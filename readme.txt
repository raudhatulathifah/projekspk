Tentu, ini draf **README.md** yang santai tapi tetap profesional dan jelas. Cocok banget buat dikirim ke temen kamu supaya dia nggak bingung cara instalasinya.

Kamu bisa copas teks di bawah ini dan simpan dengan nama `README.md` di folder proyekmu.

---

# 📊 Human Capital Analytics Dashboard

Halo! Ini adalah aplikasi dashboard **Decision Support System (DSS)** untuk melakukan pemeringkatan performa karyawan secara otomatis. Sistem ini menggunakan metodologi komputasi **AHP (Analytic Hierarchy Process)** dan **SAW (Simple Additive Weighting)** dengan tampilan UI yang modern dan profesional.

## 🚀 Cara Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini supaya aplikasinya jalan lancar di laptop kamu:

### 1. Persiapan Awal

Pastikan kamu sudah install **Python** (disarankan versi 3.8 ke atas).

### 2. Install Library yang Dibutuhkan

Buka terminal atau CMD di folder proyek ini, lalu jalankan perintah berikut untuk menginstal semua "bahan baku" yang diperlukan:

```bash
pip install flask pandas numpy (jalankan ini diterminal vscode)

```

### 3. Jalankan Aplikasi

Setelah instalasi selesai, jalankan file utama aplikasinya:

```bash
python app.py

```

### 4. Buka di Browser

Kalau di terminal sudah muncul tulisan `Running on http://127.0.0.1:5000`, buka browser kamu (Chrome/Edge) dan ketik alamat berikut:

```
http://127.0.0.1:5000

```

---

## 📂 Cara Penggunaan

1. Siapkan file data karyawan dalam format **.csv**.
2. Klik tombol **"Pilih File"** pada dashboard.
3. Klik **"Proses"**.
4. Boom! Sistem bakal langsung menghitung dan nampilin:
* **Populasi Sampel**: Jumlah total karyawan yang dianalisis.
* **Pencapaian Tertinggi**: Siapa yang jadi juara (lengkap dengan icon mahkota 👑).
* **Visualisasi Bar Chart**: Perbandingan skor antar karyawan.
* **Urutan Prioritas**: Daftar peringkat dari yang terbaik.



---

## 🛠️ Tech Stack

* **Backend**: Flask (Python)
* **Data Processing**: Pandas & Numpy
* **Frontend**: HTML5, CSS3 (Custom Glassmorphism), Bootstrap 5
* **Charts**: Chart.js
* **Icons**: FontAwesome 6

---

**Note:** Kalau ada error atau bingung, tanya aja ya! Enjoy coding! ☕✨