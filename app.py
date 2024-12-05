from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sqlite3
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model 
from tensorflow.keras.preprocessing.image import img_to_array, load_img 

app = Flask(__name__)
# app.secret_key = 'your_secret_key'

model = load_model("training/model.keras")

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Helper: Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database connection
def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['image']
    farmer_name = request.form['farmer_name']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Predict using the model
        try:
            image = load_img(file_path, target_size=(256, 256))  # Adjust based on your model
            image = img_to_array(image) / 255.0
            image = np.expand_dims(image, axis=0)
            prediction = model.predict(image)
            labels = ['Healthy', 'Late Blight', 'Early Blight']
            result = labels[np.argmax(prediction)]

            # Save to database
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO uploads (farmer_name, image_path, result) VALUES (?, ?, ?)", 
                           (farmer_name, file_path, result))
            conn.commit()
            conn.close()

            return render_template('result.html', farmer_name=farmer_name, result=result)
        except Exception as e:
            flash(f"Error during prediction: {e}")
            return redirect(url_for('home'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploads")
    data = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', data=data)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        farmer_name = request.form['farmer_name']
        feedback_message = request.form['feedback_message']
        
        # Save feedback in the database (Optional)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (farmer_name, message) VALUES (?, ?)", 
                       (farmer_name, feedback_message))
        conn.commit()
        conn.close()
        
        flash("Thank you for your feedback!")
        return redirect(url_for('feedback_success'))
    return render_template('feedback.html')

@app.route('/feedback_success')
def feedback_success():
    return render_template('feedback_success.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)
