import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)

# secret key untuk session
app.secret_key = 'capital_analytics_secret_2024'

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
# AKUN PENGGUNA (tanpa database)
# =====================================================
USERS = {
    'admin':      {'password': 'admin123',   'name': 'Administrator', 'role': 'Admin'},
    'hr_manager': {'password': 'hr2024',     'name': 'HR Manager',    'role': 'HR Manager'},
    'analyst':    {'password': 'analyst123', 'name': 'Data Analyst',  'role': 'Analyst'},
}


# =====================================================
# DECORATOR LOGIN REQUIRED
# =====================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


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

    ahp_meta = {
        'lambda_max': round(float(lambda_max), 4),
        'CI':         round(float(CI), 4),
        'RI':         1.12,
        'CR':         round(float(CR), 4),
        'consistent': bool(CR < 0.1),
        'weights':    {c: round(float(w), 4) for c, w in zip(
            ['PerformanceScore','EngagementSurvey','EmpSatisfaction','Absences','SpecialProjectsCount'],
            weights
        )},
    }

    return weights, ahp_meta


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
        weights, ahp_meta = calculate_ahp_weights()
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

        rankings = df_rank[
            ['EmpID', 'Employee_Name'] + criteria + ['Score']
        ].head(10).to_dict(orient='records')

        # detail: semua karyawan aktif, nilai normalisasi + score
        detail = (
            df_rank[['EmpID', 'Employee_Name'] + criteria + ['Score']]
            .round(4)
            .to_dict(orient='records')
        )

        return rankings, detail, ahp_meta

    except Exception as e:
        print("Error:", e)
        return None, None, None


# =====================================================
# ROUTING - LOGIN
# =====================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['name']     = USERS[username]['name']
            session['role']     = USERS[username]['role']
            return redirect(url_for('index'))
        error = 'Username atau password salah. Silakan coba lagi.'
    return render_template('login.html', error=error)


# =====================================================
# ROUTING - LOGOUT
# =====================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# =====================================================
# ROUTING FLASK
# =====================================================
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    rankings = []
    detail = []
    ahp_meta = None
    stats = {'total': 0, 'avg': 0, 'top_name': "-"}

    if request.method == 'POST':

        file = request.files.get('file')

        if file and file.filename != '':

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            rankings, detail, ahp_meta = process_ranking(filepath)

            if rankings:

                stats = {
                    'total': len(rankings),
                    'avg': sum(r['Score'] for r in rankings) / len(rankings),
                    'top_name': rankings[0]['Employee_Name']
                }

    return render_template(
        'index.html',
        rankings=rankings,
        detail=detail or [],
        ahp_meta=ahp_meta,
        stats=stats,
        user_name=session.get('name'),
        user_role=session.get('role'),
    )


# =====================================================
# RUN APP
# =====================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
