from flask import Flask, render_template, url_for, send_from_directory, send_file
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
