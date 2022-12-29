'''runs hello'''
import os
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
# from flask import send_from_directory
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

def topfile():
    print("monkeys uncle")

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
            flash(f'{filename} was uploaded successfully')

            return redirect(url_for('success', name=filename))
    return render_template('upload.html')

@app.route('/uploads/<name>')
def success(name):
    '''show the server download after the client upload'''
    os.system('ls -al /tmp/plod')
    print('--------------------')
    os.system(f'ls /tmp/plod/{name}')
    os.system(f'demucs /tmp/plod/{name}')
    return render_template('fileloc.html')

# TODO: what is this doing: send_from_directory(app.config["UPLOAD_FOLDER"], name)
# TODO: send_from_directory(app.config["UPLOAD_FOLDER"], name)
# TODO: when in the return it just sends us to the file
