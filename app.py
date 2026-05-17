import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

# folder untuk menyimpan file upload
app.config['UPLOAD_FOLDER'] = 'uploads'

# buat folder uploads otomatis kalau belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# =====================================================
# PERHITUNGAN BOBOT AHP
# =====================================================
def calculate_ahp_weights():

    # matriks perbandingan antar kriteria
    A = np.array([
        [1,   3,   3,   5,   4],
        [1/3, 1,   2,   4,   3],
        [1/3, 1/2, 1,   3,   2],
        [1/5, 1/4, 1/3, 1,   2],
        [1/4, 1/3, 1/2, 1/2, 1]
    ])

    # normalisasi matriks
    col_sum = A.sum(axis=0)
    norm_A = A / col_sum

    # hitung bobot tiap kriteria
    weights = norm_A.mean(axis=1)

    # =========================
    # CEK KONSISTENSI AHP
    # =========================
    lambda_max = np.sum(col_sum * weights)

    # jumlah kriteria
    n = A.shape[0]

    # consistency index
    CI = (lambda_max - n) / (n - 1)

    # random index untuk n = 5
    RI = 1.12

    # consistency ratio
    CR = CI / RI

    print("Consistency Ratio (CR):", round(CR, 4))

    # validasi matriks
    if CR < 0.1:
        print("Matrix konsisten")
    else:
        print("Matrix tidak konsisten")

    return weights


# =====================================================
# PROSES RANKING KARYAWAN
# =====================================================
def process_ranking(filepath):

    try:

        # =========================
        # LOAD DATA
        # =========================
        df = pd.read_csv(filepath)

        print("Data awal:", df.shape)

        # =========================
        # FEATURE SELECTION
        # =========================
        criteria = [
            'PerformanceScore',
            'EngagementSurvey',
            'EmpSatisfaction',
            'Absences',
            'SpecialProjectsCount'
        ]

        # ambil kolom yang dibutuhkan
        df_spk = df[
            ['EmpID', 'Employee_Name'] + criteria + ['Termd']
        ].copy()

        print("Shape feature selection:", df_spk.shape)

        # =========================
        # FILTER KARYAWAN AKTIF
        # =========================
        print("Distribusi Termd:")
        print(df_spk['Termd'].value_counts())

        # hanya ambil karyawan aktif
        df_spk = df_spk[df_spk['Termd'] == 0]

        print("Shape setelah filter aktif:", df_spk.shape)

        # =========================
        # CEK MISSING VALUE
        # =========================
        print(df_spk.isnull().sum())

        # kolom penting
        cols_needed = criteria + ['Termd']

        # hapus data kosong
        df_spk = df_spk.dropna(subset=cols_needed)

        print("Shape setelah cleaning:", df_spk.shape)

        # =========================
        # HAPUS DUPLIKAT
        # =========================
        print("Jumlah duplikat:", df_spk.duplicated().sum())

        df_spk = df_spk.drop_duplicates()

        print("Shape setelah hapus duplikat:", df_spk.shape)

        # =========================
        # NORMALISASI TEXT
        # =========================
        print("Before cleaning:", df_spk['PerformanceScore'].unique())

        df_spk['PerformanceScore'] = (
            df_spk['PerformanceScore']
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'\s+', ' ', regex=True)
        )

        print("After cleaning:", df_spk['PerformanceScore'].unique())

        # =========================
        # ENCODING PERFORMANCE SCORE
        # =========================
        mapping_perf = {
            'exceeds': 4,
            'fully meets': 3,
            'needs improvement': 2,
            'pip': 1
        }

        df_spk['PerformanceScore'] = (
            df_spk['PerformanceScore']
            .map(mapping_perf)
        )

        print(
            "Null setelah encoding:",
            df_spk['PerformanceScore'].isnull().sum()
        )

        # hapus data yang gagal mapping
        df_spk = df_spk.dropna(subset=['PerformanceScore'])

        print("Shape setelah encoding:", df_spk.shape)

        # cek apakah data kosong
        if df_spk.empty:
            return None

        # =========================
        # HITUNG BOBOT AHP
        # =========================
        weights = calculate_ahp_weights()

        weights_dict = dict(zip(criteria, weights))

        print("Bobot AHP:")
        print(weights_dict)

        # =========================
        # NORMALISASI SAW
        # =========================
        df_norm = df_spk.copy()

        # benefit -> semakin besar semakin baik
        benefit = [
            'PerformanceScore',
            'EngagementSurvey',
            'EmpSatisfaction',
            'SpecialProjectsCount'
        ]

        # cost -> semakin kecil semakin baik
        cost = ['Absences']

        # normalisasi benefit
        for col in benefit:

            max_val = df_spk[col].max()

            df_norm[col] = (
                df_spk[col] / max_val
                if max_val != 0 else 0
            )

        # normalisasi cost
        for col in cost:

            # hindari pembagian nol
            min_val = df_spk[col].replace(0, np.nan).min()

            if not pd.isna(min_val):

                df_norm[col] = (
                    min_val /
                    df_spk[col].replace(0, np.nan)
                )

            else:
                df_norm[col] = 1.0

        # antisipasi jika masih ada nilai kosong
        df_norm.fillna(0, inplace=True)

        # =========================
        # HITUNG SKOR AKHIR
        # =========================
        df_norm['Score'] = 0

        for i, col in enumerate(criteria):

            df_norm['Score'] += (
                df_norm[col] * weights[i]
            )

        # =========================
        # RANKING
        # =========================
        df_rank = df_norm.sort_values(
            by='Score',
            ascending=False
        )

        print(df_rank[
            ['EmpID', 'Employee_Name', 'Score']
        ].head(10))

        # kirim hasil ke html
        return df_rank[
            ['EmpID', 'Employee_Name', 'Score']
        ].head(10).to_dict(orient='records')

    except Exception as e:

        print(f"Error: {e}")
        return None


# =====================================================
# ROUTING
# =====================================================
@app.route('/', methods=['GET', 'POST'])
def index():

    rankings = []

    stats = {
        'total': 0,
        'avg': 0,
        'top_name': "-"
    }

    # proses upload file
    if request.method == 'POST':

        file = request.files.get('file')

        if file and file.filename != '':

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                file.filename
            )

            # simpan file
            file.save(filepath)

            # proses ranking
            data = process_ranking(filepath)

            # kalau data berhasil diproses
            if data and len(data) > 0:

                rankings = data

                stats = {

                    'total': len(data),

                    'avg': sum(
                        r['Score']
                        for r in data
                    ) / len(data),

                    'top_name': data[0]['Employee_Name']
                }

    return render_template(
        'index.html',
        rankings=rankings,
        stats=stats
    )


# =====================================================
# JALANKAN FLASK
# =====================================================
if __name__ == '__main__':

    app.run(
        debug=True,
        port=5000
    )
