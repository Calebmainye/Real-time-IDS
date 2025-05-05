from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import os
import pandas as pd
import numpy as np
import joblib
import pickle
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Load model and related files
model_dir = os.path.join(os.path.dirname(__file__), 'models')
model = joblib.load(os.path.join(model_dir, 'final_model.joblib'))
scaler = pickle.load(open(os.path.join(model_dir, 'scaler.pkl'), 'rb'))
with open(os.path.join(model_dir, 'optimal_threshold.txt'), 'r') as f:
    threshold = float(f.read().strip())
selected_features = pd.read_csv(os.path.join(model_dir, 'selected_features.csv'), header=None)[0].tolist()

# Mock user database (replace with real database in production)
users = {
    'admin@example.com': {
        'password': 'admin123',
        'name': 'Admin'
    }
}

# Mock alerts database (replace with real database in production)
alerts = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and users[email]['password'] == password:
            session['user'] = email
            session['name'] = users[email]['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if email in users:
            flash('Email already exists', 'error')
        else:
            users[email] = {
                'password': password,
                'name': name
            }
            flash('Account created successfully', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('name', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', alerts=alerts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/file-upload')
def file_upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('file_upload.html')

@app.route('/manual-input')
def manual_input():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('manual_input.html', features=selected_features)

@app.route('/predict-file', methods=['POST'])
def predict_file():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save the file temporarily
        file_path = os.path.join('temp', f"{uuid.uuid4()}.csv")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        
        # Read and process the file
        data = pd.read_csv(file_path)
        # Ensure all required features are present
        for feature in selected_features:
            if feature not in data.columns:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
        
        # Extract selected features
        X = data[selected_features]
        
        # Scale the features
        X_scaled = scaler.transform(X)
        
        # Make predictions
        predictions = model.predict_proba(X_scaled)[:, 1]
        
        # Apply threshold
        results = (predictions >= threshold).astype(int)
        
        # Store alerts for intrusions
        if 1 in results:
            for i, result in enumerate(results):
                if result == 1:
                    alert = {
                        'id': str(uuid.uuid4()),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'File Upload',
                        'confidence': float(predictions[i]),
                        'details': data.iloc[i].to_dict()
                    }
                    alerts.append(alert)
        
        # Clean up
        os.remove(file_path)
        
        # Return results
        return jsonify({
            'total': len(results),
            'intrusions': int(sum(results)),
            'safe': int(len(results) - sum(results)),
            'results': [{'index': i, 'is_intrusion': bool(result), 'confidence': float(predictions[i])} 
                        for i, result in enumerate(results)]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict-manual', methods=['POST'])
def predict_manual():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get input data
        data = {}
        for feature in selected_features:
            value = request.form.get(feature)
            if value is None:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
            data[feature] = float(value)
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Scale the features
        X_scaled = scaler.transform(df)
        
        # Make prediction
        prediction = model.predict_proba(X_scaled)[0, 1]
        
        # Apply threshold
        result = int(prediction >= threshold)
        
        # Store alert if intrusion
        if result == 1:
            alert = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Manual Input',
                'confidence': float(prediction),
                'details': data
            }
            alerts.append(alert)
        
        # Return result
        return jsonify({
            'is_intrusion': bool(result),
            'confidence': float(prediction),
            'threshold': float(threshold)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(alerts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)