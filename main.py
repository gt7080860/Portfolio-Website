from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, send_file
import os
import psycopg2
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, find_dotenv

print("Loaded env from:", find_dotenv())  # Temporary debug print

load_dotenv()

app = Flask(__name__)
app.secret_key = 'gt_secret_key'

UPLOAD_FOLDER = 'static/uploads'
RESUME_PATH = 'static/resume.pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PASSWORD = os.environ.get('ADMIN_PASSWORD', 'fallbackpass')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database Connection ---
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# --- Create Table if not exists ---
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    file TEXT
                );
            """)
        conn.commit()

init_db()


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, description, start_date, end_date, file FROM projects;")
    projects = [dict(zip(['name', 'description', 'start_date', 'end_date', 'file'], row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
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
        return render_template('admin_panel.html')
    else:
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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO projects (name, description, start_date, end_date, file)
            VALUES (%s, %s, %s, %s, %s);
        """, (name, desc, start_date, end_date, filename))
        conn.commit()
        cur.close()
        conn.close()

        flash('Project uploaded successfully!')

    return redirect(url_for('admin'))


@app.route('/delete-project/<filename>', methods=['POST'])
def delete_project(filename):
    if not session.get('admin'):
        flash("Unauthorized access.")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE file = %s;", (filename,))
    conn.commit()
    cur.close()
    conn.close()

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    flash('Project deleted successfully.')
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/upload-resume', methods=['GET', 'POST'])
def upload_resume():
    if not session.get('admin'):
        flash("Unauthorized access.")
        return redirect(url_for('admin'))

    if request.method == 'POST':
        resume = request.files.get('resume')
        if resume and resume.filename.endswith('.pdf'):
            resume.save(RESUME_PATH)
            flash("Resume uploaded successfully.")
            return redirect(url_for('admin'))
        else:
            flash("Please upload a PDF file.")
            return redirect(url_for('upload_resume'))

    return render_template('upload_resume.html')


@app.route('/resume')
def download_resume():
    return send_file(RESUME_PATH, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
