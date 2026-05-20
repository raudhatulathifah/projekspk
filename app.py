import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

# folder upload
app.config['UPLOAD_FOLDER'] = 'uploads'

# buat folder uploads otomatis
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# =====================================================
# URUTAN KRITERIA
# =====================================================
criteria = [
    'PerformanceScore',
    'EngagementSurvey',
    'EmpSatisfaction',
    'Absences',
    'SpecialProjectsCount'
]


# =====================================================
# PERHITUNGAN BOBOT AHP
# =====================================================
def calculate_ahp_weights():

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

    # bobot (eigen vector aproksimasi)
    weights = norm_A.mean(axis=1)

    # =========================
    # CEK KONSISTENSI
    # =========================
    Aw = np.dot(A, weights)
    lambda_max = np.mean(Aw / weights)

    n = A.shape[0]
    CI = (lambda_max - n) / (n - 1)

    RI = 1.12  # n = 5
    CR = CI / RI

    print("Consistency Ratio (CR):", round(CR, 4))

    if CR < 0.1:
        print("Matrix konsisten")
    else:
        print("Matrix tidak konsisten")

    return weights


# =====================================================
# PROSES RANKING
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
        df_spk = df[['EmpID', 'Employee_Name'] + criteria + ['Termd']].copy()
        print("Shape feature selection:", df_spk.shape)

        # =========================
        # FILTER AKTIF KARYAWAN
        # =========================
        df_spk = df_spk[df_spk['Termd'] == 0]
        print("Shape setelah filter aktif:", df_spk.shape)

        # =========================
        # CLEANING DATA
        # =========================
        df_spk = df_spk.dropna(subset=criteria + ['Termd'])
        df_spk = df_spk.drop_duplicates()

        # =========================
        # NORMALISASI TEXT
        # =========================
        df_spk['PerformanceScore'] = (
            df_spk['PerformanceScore']
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'\s+', ' ', regex=True)
        )

        # =========================
        # ENCODING PERFORMANCE
        # =========================
        mapping_perf = {
            'exceeds': 4,
            'fully meets': 3,
            'needs improvement': 2,
            'pip': 1
        }

        df_spk['PerformanceScore'] = df_spk['PerformanceScore'].map(mapping_perf)
        df_spk = df_spk.dropna(subset=['PerformanceScore'])

        if df_spk.empty:
            return None

        # =========================
        # AHP WEIGHTS
        # =========================
        weights = calculate_ahp_weights()
        weights_dict = dict(zip(criteria, weights))

        print("Bobot AHP:", weights_dict)

        # =========================
        # NORMALISASI SAW
        # =========================
        df_norm = df_spk.copy()

        benefit = [
            'PerformanceScore',
            'EngagementSurvey',
            'EmpSatisfaction',
            'SpecialProjectsCount'
        ]

        cost = ['Absences']

        # benefit normalization
        for col in benefit:
            max_val = df_spk[col].max()
            df_norm[col] = df_spk[col] / max_val if max_val != 0 else 0

        # cost normalization
        for col in cost:
            max_val = df_spk[col].max()
            if max_val != 0:
                df_norm[col] = 1 - (df_spk[col] / max_val)
            else:
                df_norm[col] = 0

        df_norm.fillna(0, inplace=True)

        # =========================
        # FINAL SCORE SAW
        # =========================
        df_norm['Score'] = 0

        for i, col in enumerate(criteria):
            df_norm['Score'] += df_norm[col] * weights[i]

        # =========================
        # RANKING
        # =========================
        df_rank = df_norm.sort_values(by='Score', ascending=False)

        print(df_rank[['EmpID', 'Employee_Name'] + criteria + ['Score']].head(10))

        return df_rank[
            ['EmpID', 'Employee_Name'] + criteria + ['Score']
        ].head(10).to_dict(orient='records')

    except Exception as e:
        print("Error:", e)
        return None


# =====================================================
# ROUTING FLASK
# =====================================================
@app.route('/', methods=['GET', 'POST'])
def index():

    rankings = []
    stats = {'total': 0, 'avg': 0, 'top_name': "-"}

    if request.method == 'POST':

        file = request.files.get('file')

        if file and file.filename != '':

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            data = process_ranking(filepath)

            if data:

                rankings = data

                stats = {
                    'total': len(data),
                    'avg': sum(r['Score'] for r in data) / len(data),
                    'top_name': data[0]['Employee_Name']
                }

    return render_template('index.html', rankings=rankings, stats=stats)


# =====================================================
# RUN APP
# =====================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
