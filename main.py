from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
import os
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'gt_secret_key'

UPLOAD_FOLDER = 'static/uploads'
PROJECTS_FILE = 'projects.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PASSWORD = os.environ.get('ADMIN_PASSWORD', 'fallbackpass')

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    projects = []
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            projects = json.load(f)
    return render_template('index.html', projects=projects, is_admin=session.get('admin'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        entered = request.form.get('admin_password')
        if entered == PASSWORD:
            session['admin'] = True
            flash("Admin login successful")
            return redirect(url_for('admin'))
        else:
            flash("Incorrect password")
            return redirect(url_for('admin'))

    if session.get('admin'):
        # Admin panel view
        return render_template('admin_panel.html')
    else:
        # Show login form
        return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    flash("Logged out successfully")
    return redirect(url_for('admin'))

@app.route('/upload-project', methods=['POST'])
def upload_project():
    if not session.get('admin'):
        flash("Unauthorized access.")
        return redirect(url_for('admin'))

    name = request.form['project_name']
    desc = request.form['project_description']
    start_date = request.form['project_start_date']
    end_date = request.form['project_end_date']
    file = request.files['project_file']


    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        projects = []
        if os.path.exists(PROJECTS_FILE):
            with open(PROJECTS_FILE, 'r') as f:
                projects = json.load(f)
        start_date = request.form['project_start_date']
        end_date = request.form['project_end_date']

        projects.append({
        'name': name,
        'description': desc,
        'start_date': start_date,
        'end_date': end_date,
        'file': filename
        })
         

        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)

        flash('Project uploaded successfully!')

    return redirect(url_for('admin'))
@app.route('/delete-project/<filename>', methods=['POST'])
def delete_project(filename):
    if not session.get('admin'):
        flash("Unauthorized access.")
        return redirect(url_for('index'))

    # Load existing projects
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            projects = json.load(f)

        # Filter out the project to delete
        projects = [p for p in projects if p['file'] != filename]

        # Save updated list
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)

    # Delete actual file if it exists
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    flash('Project deleted successfully.')
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
