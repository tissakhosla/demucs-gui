'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''
import os
import smtplib
import uuid
from threading import Thread

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
app.config['SECRET_KEY'] = os.urandom(12)

def demucs(wav):
    os.system(f'demucs /tmp/plod/{wav}')
    email(wav)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def email(c):
    '''send email when ready'''

    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to the email account
    # TODO: move to env
    me = 'tissa.music@gmail.com'
    server.login(me, 'zfjqkwrmmnghxzgv')
    # Send the email

    # TODO: receive users email from frontend
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
            flash(f'{filename} uploaded successfully.')
            flash('You will receive an email when processing is complete')
            return redirect(url_for('success', cn=codename))
    return render_template('upload.html')

@app.route('/success-<cn>')
def success(cn):
    '''show success after processing'''
    os.system(f'ls /tmp/plod/{cn}')
    dmuxThread = Thread(target=demucs, args=(cn,))
    dmuxThread.start()
    return render_template('success.html')

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)

# TODO: get user email from frontend
# TODO: put gmail key and my personal email in ENV
# TODO: use demucs module within python
# TODO: create a helper class for all the functions
# TODO: routes can live here
