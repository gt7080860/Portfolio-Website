from flask import Flask, render_template, send_file, request, redirect, session, flash
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'pdf'}

# Fixed, permanent resume path
RESUME_FILENAME = 'Gaurav-Tiwari-Resume.pdf'
RESUME_PATH = os.path.join(UPLOAD_FOLDER, RESUME_FILENAME)

PROJECTS_JSON = 'static/projects.json'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return redirect('/landing')


@app.route('/landing')
def landing():
    return render_template('landing.html')


@app.route('/portfolio')
def portfolio():
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
            flash('Incorrect password.', 'error')
            return redirect('/admin/login')

    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect('/admin/login')

    resume_exists = os.path.exists(RESUME_PATH)

    if os.path.exists(PROJECTS_JSON):
        with open(PROJECTS_JSON, 'r') as f:
            projects = json.load(f)
    else:
        projects = []

    return render_template(
        'admin_dashboard.html',
        resume_exists=resume_exists,
        projects=projects
    )


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
        # Always overwrite the same resume file
        file.save(RESUME_PATH)
        flash('Resume uploaded successfully!', 'success')
        return redirect('/admin/dashboard')
    else:
        flash('Only PDF files are allowed', 'error')
        return redirect('/admin/dashboard')


@app.route('/admin/add-project', methods=['POST'])
def add_project():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect('/admin/login')

    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    github_link = request.form.get('github_link')

    if not all([name, description, start_date, end_date, github_link]):
        flash('All fields are required!', 'error')
        return redirect('/admin/dashboard')

    if os.path.exists(PROJECTS_JSON):
        with open(PROJECTS_JSON, 'r') as f:
            projects = json.load(f)
    else:
        projects = []

    projects.append({
        'name': name,
        'description': description,
        'start_date': start_date,
        'end_date': end_date,
        'github_link': github_link
    })

    with open(PROJECTS_JSON, 'w') as f:
        json.dump(projects, f, indent=2)

    flash('Project added successfully!', 'success')
    return redirect('/admin/dashboard')


@app.route('/admin/delete-project/<int:index>', methods=['POST'])
def delete_project(index):
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect('/admin/login')

    if not os.path.exists(PROJECTS_JSON):
        flash('No projects found!', 'error')
        return redirect('/admin/dashboard')

    with open(PROJECTS_JSON, 'r') as f:
        projects = json.load(f)

    if 0 <= index < len(projects):
        deleted = projects.pop(index)
        with open(PROJECTS_JSON, 'w') as f:
            json.dump(projects, f, indent=2)
        flash(f'Project "{deleted["name"]}" deleted!', 'success')
    else:
        flash('Invalid project index!', 'error')

    return redirect('/admin/dashboard')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect('/')


@app.route('/resume')
def download_resume():
    if os.path.exists(RESUME_PATH):
        return send_file(
            RESUME_PATH,
            as_attachment=True,
            download_name='Gaurav_Tiwari_Resume.pdf'
        )
    else:
        flash('Resume not found', 'error')
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
