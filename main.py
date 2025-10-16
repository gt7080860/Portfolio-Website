"""from flask import Flask, render_template, url_for, send_from_directory, send_file
import os
import json

app = Flask(__name__)

#UPLOAD_FOLDER = 'static/uploads'
RESUME_PATH = 'static/Gaurav_Tiwari_Resume.pdf'
PROJECTS_JSON = 'projects.json'

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    # Load project data from JSON file
    if os.path.exists(PROJECTS_JSON):
        with open(PROJECTS_JSON, 'r') as f:
            projects = json.load(f)
    else:
        projects = []

    return render_template('index.html', projects=projects)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/resume')
def download_resume():
    return send_file(RESUME_PATH, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
    
    """
from flask import Flask, render_template, url_for, send_from_directory, send_file, request, redirect, session, flash
import os
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'pdf'}
RESUME_PATH = 'static/Gaurav_Tiwari_Resume.pdf'
PROJECTS_JSON = 'projects.json'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    # Load project data from JSON file
    if os.path.exists(PROJECTS_JSON):
        with open(PROJECTS_JSON, 'r') as f:
            projects = json.load(f)
    else:
        projects = []

    return render_template('index.html', projects=projects)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect('/admin/dashboard')
        else:
            flash('Incorrect password. Please try again.', 'error')
            return redirect('/admin/login')
    
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect('/admin/login')
    
    # Check if resume exists
    resume_exists = os.path.exists(RESUME_PATH)
    
    return render_template('admin_dashboard.html', resume_exists=resume_exists)


@app.route('/admin/upload-resume', methods=['POST'])
def upload_resume():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect('/admin/login')
    
    if 'resume' not in request.files:
        flash('No file selected', 'error')
        return redirect('/admin/dashboard')
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect('/admin/dashboard')
    
    if file and allowed_file(file.filename):
        # Save the file with a fixed name
        filename = 'Gaurav_Tiwari_Resume.pdf'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('Resume uploaded successfully!', 'success')
        return redirect('/admin/dashboard')
    else:
        flash('Only PDF files are allowed', 'error')
        return redirect('/admin/dashboard')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect('/')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/resume')
def download_resume():
    if os.path.exists(RESUME_PATH):
        return send_file(RESUME_PATH, as_attachment=True)
    else:
        flash('Resume not found', 'error')
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)