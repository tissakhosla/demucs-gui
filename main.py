'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''
import os
import smtplib
import uuid
import logging
from threading import Thread

from flask import (
    Flask, render_template, request,redirect,
    url_for, send_from_directory, flash
)

from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = '/tmp/plod'
ALLOWED_EXTENSIONS = { 'wav' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12)

def demucs(wav, em):
    os.system(f'demucs /tmp/plod/{wav}')
    email(wav, em)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def email(c, e):
    '''send email'''
    # Set up the SMTP server
    # TODO: move smtp server to env
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to the email account
    # TODO: move these to env
    me = 'tissa.music@gmail.com'
    server.login(me, 'zfjqkwrmmnghxzgv')
    # Send the email
    logging.info(' > to: %s', e)
    to = [e]
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
    logging.info('START: a wild user has appeared')
    if request.method == 'POST':
        useremail = request.form['email']

        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('no selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            logging.info(' < file: %s', filename)
            logging.info(' < type: %s', file.content_type)
            logging.info(' < size: %s bytes', len(file.read()))
            file.seek(0)
            codename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], codename))

            flash(f'{filename} uploaded successfully.')
            flash('You will receive an email when processing is complete')
            return redirect(url_for('success', cn=codename, ue=useremail))
    return render_template('upload.html')

@app.route('/success-<cn>')
def success(cn):
    '''show success after processing'''
    os.system(f'ls /tmp/plod/{cn}')
    ue = request.args.get('ue')
    _demucs = Thread(target=demucs, args=(cn, ue))
    _demucs.start()
    return render_template('success.html')

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)

# TODO: get user email from frontend
# TODO: put gmail key and my personal email in ENV
# TODO: use demucs module within python
# TODO: create a helper class for all the functions
# TODO: routes can live here
# TODO: send all requests to admins
# TODO: https://flask.palletsprojects.com/en/2.2.x/logging/#email-errors-to-admins
# TODO: don't use flash, pass the variables into render_template
# TODO: create new email to handle all this
