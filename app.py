import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def calculate_ahp_weights():
    A = np.array([
        [1,   3,   3,   5,   4],
        [1/3, 1,   2,   4,   3],
        [1/3, 1/2, 1,   3,   2],
        [1/5, 1/4, 1/3, 1,   2],
        [1/4, 1/3, 1/2, 1/2, 1]
    ])
    col_sum = A.sum(axis=0)
    norm_A = A / col_sum
    return norm_A.mean(axis=1)

def process_ranking(filepath):
    try:
        df = pd.read_csv(filepath)
        criteria = ['PerformanceScore', 'EngagementSurvey', 'EmpSatisfaction', 'Absences', 'SpecialProjectsCount']
        
        # Filter & Clean
        df_spk = df[['Employee_Name'] + criteria + ['Termd']].copy()
        df_spk = df_spk[df_spk['Termd'] == 0]
        
        df_spk['PerformanceScore'] = df_spk['PerformanceScore'].astype(str).str.strip().str.lower()
        mapping_perf = {'exceeds': 4, 'fully meets': 3, 'needs improvement': 2, 'pip': 1}
        df_spk['PerformanceScore'] = df_spk['PerformanceScore'].map(mapping_perf)
        
        df_spk = df_spk.dropna(subset=criteria)

        if df_spk.empty:
            return None

        # Normalisasi SAW
        df_norm = df_spk.copy()
        benefit = ['PerformanceScore', 'EngagementSurvey', 'EmpSatisfaction', 'SpecialProjectsCount']
        cost = ['Absences']
        
        for col in benefit:
            max_val = df_spk[col].max()
            df_norm[col] = df_spk[col] / max_val if max_val != 0 else 0
            
        for col in cost:
            min_val = df_spk[col].replace(0, np.nan).min()
            if not pd.isna(min_val):
                df_norm[col] = min_val / df_spk[col].replace(0, np.nan)
            else:
                df_norm[col] = 1.0

        # Hitung Skor
        weights = calculate_ahp_weights()
        df_norm['Score'] = 0
        for i, col in enumerate(criteria):
            df_norm['Score'] += df_norm[col] * weights[i]
        
        return df_norm[['Employee_Name', 'Score']].sort_values(by='Score', ascending=False).head(10).to_dict(orient='records')
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    # Inisialisasi variabel agar tidak "Undefined" di HTML
    rankings = []
    stats = {'total': 0, 'avg': 0, 'top_name': "-"}
    
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            data = process_ranking(filepath)
            
            if data and len(data) > 0:
                rankings = data
                stats = {
                    'total': len(data),
                    'avg': sum(r['Score'] for r in data) / len(data),
                    'top_name': data[0]['Employee_Name']
                }
    
    # Kirim rankings dan stats meskipun kosong (biar index.html ga bingung)
    return render_template('index.html', rankings=rankings, stats=stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)