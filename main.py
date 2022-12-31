'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''
import os
import smtplib
import uuid
import threading

from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import send_from_directory
from flask import flash
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = '/tmp/plod'
ALLOWED_EXTENSIONS = { 'wav' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "a1s2d3f4g5h6j7k8l9"

def demucs(wav):
    os.system(f'demucs /tmp/plod/{wav}')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def email(c):
    '''send email'''
    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to the email account
    # TODO: move to env
    me = 'tissa.music@gmail.com'
    server.login(me, 'zfjqkwrmmnghxzgv')
    # Send the email

    to = ['tissa@finityllc.com']
    subject = 'testing python email'
    body = f'Here are the links: \
        \n http://127.0.0.1:5000/separated/htdemucs/{c}/bass.wav \
        \n http://127.0.0.1:5000/separated/htdemucs/{c}/drums.wav \
        \n http://127.0.0.1:5000/separated/htdemucs/{c}/other.wav \
        \n http://127.0.0.1:5000/separated/htdemucs/{c}/vocals.wav'
    msg = f'Subject: {subject}\n\n{body}'
    server.sendmail(me, to, msg)

    # Disconnect from the server
    server.quit()

@app.route("/")
def to_upload():
    return redirect('/upload')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    '''main route'''
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('no selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            codename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], codename))
            flash(f'{filename} split successfully')
            flash('Check your email')
            return redirect(url_for('success', cn=codename))
    return render_template('upload.html')

@app.route('/success-<cn>')
def success(cn):
    '''show success after processing'''
    os.system(f'ls /tmp/plod/{cn}')
    demucs(cn)
    email(cn)
    return render_template('success.html')

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)

# maintain state in flask

# start the demucs in a separate thread
# thread places a marker when complete
# listener sends an email when the marker is present
# listener deletes the marker
# clear flashes?
