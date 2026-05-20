# Human Capital Analytics Dashboard
Aplikasi ini merupakan sistem pendukung keputusan (Decision Support System/DSS) untuk melakukan pemeringkatan performa karyawan menggunakan metode AHP (Analytic Hierarchy Process) dan SAW (Simple Additive Weighting).

Sistem akan memproses data karyawan dari file CSV, menghitung bobot kriteria menggunakan AHP, kemudian melakukan perangkingan menggunakan metode SAW. Hasil akhir ditampilkan dalam bentuk dashboard dan visualisasi grafik.

## Fitur Utama
* Upload dataset karyawan format `.csv`
* Perhitungan bobot kriteria menggunakan metode AHP
* Proses normalisasi dan perangkingan menggunakan metode SAW
* Menampilkan ranking karyawan terbaik
* Visualisasi data dalam bentuk chart
* Tampilan dashboard berbasis web

## Teknologi yang Digunakan
* Python
* Flask
* Pandas
* NumPy
* HTML, CSS, Bootstrap
* Chart.js

## Cara Menjalankan Program

### 1. Install Python
Pastikan Python versi 3.8 atau lebih baru sudah terpasang di perangkat.

### 2. Install Dependency
Buka terminal atau CMD pada folder project, lalu jalankan:
pip install flask pandas numpy

### 3. Jalankan Program
Jalankan file utama aplikasi dengan perintah:
python app.py

### 4. Buka Aplikasi
Jika program berhasil dijalankan, akan muncul alamat berikut pada terminal:
http://127.0.0.1:5000
Buka alamat tersebut melalui browser.

## Cara Penggunaan
1. Siapkan file dataset karyawan dengan format `.csv`
2. Klik tombol “Pilih File”
3. Upload dataset
4. Klik tombol “Proses”
5. Sistem akan menampilkan hasil ranking karyawan berdasarkan perhitungan AHP dan SAW

## Struktur Perhitungan Sistem

### AHP (Analytic Hierarchy Process)
Metode AHP digunakan untuk menentukan bobot setiap kriteria berdasarkan matriks perbandingan berpasangan. Sistem juga melakukan pengecekan konsistensi menggunakan Consistency Ratio (CR).

### SAW (Simple Additive Weighting)
Metode SAW digunakan untuk menghitung nilai preferensi akhir setiap karyawan melalui proses:
* Pembentukan matriks keputusan
* Normalisasi data
* Perkalian nilai normalisasi dengan bobot AHP
* Penjumlahan seluruh nilai preferensi
* Proses perangkingan

Rumus SAW:
Vi = Σ (wj × rij)

Keterangan:
* Vi = nilai preferensi alternatif
* wj = bobot kriteria
* rij = nilai normalisasi alternatif

## Dataset
Dataset yang digunakan berupa data karyawan yang memiliki beberapa kriteria penilaian, seperti:
* PerformanceScore
* EngagementSurvey
* EmpSatisfaction
* Absences
* SpecialProjectsCount

## Catatan
Pastikan file dataset sesuai format dan tidak terdapat data kosong pada kolom utama yang digunakan dalam proses perhitungan.
