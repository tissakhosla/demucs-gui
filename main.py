'''runs hello'''
import os
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import send_from_directory
from flask import flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp/plod'
ALLOWED_EXTENSIONS = { 'wav', 'txt' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "a1s2d3f4g5h6j7k8l9"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def to_upload():
    return redirect('/upload')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    '''main route'''
    if request.method == 'POST':
        if 'file' not in request.files:
            # flash('no file part')
            return redirect(request.url)
        file = request.files['file']
        print(request)
        if file.filename == '':
            # flash('no selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("The file was uploaded successfully")
            return redirect(url_for('newpage'))
            # return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')

@app.route('/newpage')
def newpage():
    '''show fileloc template'''
    print(os.getcwd())
    return render_template('fileloc.html')

@app.route('/uploads/<name>')
def download_file(name):
    '''show the server download after the client upload'''
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
