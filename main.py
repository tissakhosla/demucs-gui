'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''

import os
import smtplib
import uuid
import logging

from datetime import datetime
from threading import Thread
from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory
)

from werkzeug.utils import secure_filename

# setup logging
logging.basicConfig(level=logging.INFO)

# initialize Flask App

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = { 'wav', 'mp3' }
MODELS = [
    'htdemucs', 'htdemucs_ft', 'htdemucs_6s', 'htdemucs_mmi',
    'mdx', 'mdx_extra', 'mdx_q', 'mdx_extra_q']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12)

# confirm env vars

assert os.getenv('G_SMTP')
assert os.getenv('G_MAIL')
assert os.getenv('G_KEY')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def utime():
    '''create timestamp when called'''
    dt = datetime.now()
    return datetime.timestamp(dt)

def email(uid, fn, em, ip, dm, op):
    '''send email'''
    # Set up the SMTP server
    server = smtplib.SMTP(os.getenv('G_SMTP'), 587)
    server.starttls()

    # Login to the email account
    me = os.getenv('G_MAIL')
    server.login(me, os.getenv('G_KEY'))

    # Build the email
    to = [em]
    subject = f'{fn} Split Tracks'

    body = f'Here are the links your files: \
        \n\n http://{ip}/separated/{dm}/{uid}/bass.{op} \
        \n http://{ip}/separated/{dm}/{uid}/drums.{op} \
        \n http://{ip}/separated/{dm}/{uid}/other.{op} \
        \n http://{ip}/separated/{dm}/{uid}/vocals.{op}'

    if dm == 'htdemucs_6s':
        body += f'\n http://{ip}/separated/{dm}/{uid}/guitar.{op} \
        \n http://{ip}/separated/{dm}/{uid}/piano.{op}'

    msg = f'Subject: {subject}\n\n{body}'
    server.sendmail(me, to, msg)

    server.quit()

def demucs(p, m, o):
    if o == 'mp3':
        flags = f'--mp3 -n {m} {p}'
    else:
        flags = f'-n {m} {p}'

    os.system(f'echo demucs {flags} > fpipe')

def process(path, code, trackname, uemail, hostip, model, output):
    demucs(path, model, output)
    email(code, trackname, uemail, hostip, model, output)
    # TODO: Why does this fire before demucs is complete?
    logging.info(' > EMAIL to: %s', uemail)

@app.route("/")
def to_upload():
    return redirect('/upload')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    '''main route'''
    server_ip = request.host
    user_ip = request.environ['REMOTE_ADDR']

    logging.info(' START: a wild user has appeared')
    logging.info(' SERVER: %s', server_ip)
    logging.info(' CLIENT: %s', user_ip)

    if request.method == 'POST':

        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        useremail = request.form['email']
        demucsmodel = request.form['model']
        outputformat = request.form['output']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            logging.info(' < FILE: %s', filename)
            logging.info(' < TYPE: %s', file.content_type)
            logging.info(' < SIZE: %s bytes', len(file.read()))
            file.seek(0)

            # write file to FS
            codename = str(uuid.uuid4())
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], codename)
            file.save(filepath)

            return redirect(url_for(
                'success',
                fp=filepath,
                cn=codename,
                fn=filename,
                ue=useremail,
                sip=server_ip,
                dm=demucsmodel,
                of=outputformat))

    return render_template('upload.html', models=enumerate(MODELS))

@app.route('/success')
def success():
    '''show success after saving file'''
    fp = request.args.get('fp')
    cn = request.args.get('cn')
    fn = request.args.get('fn')
    ue = request.args.get('ue')
    sip = request.args.get('sip')
    dm = request.args.get('dm')
    of = request.args.get('of')
    
    _process = Thread(
        target=process,
        args=(fp, cn, fn, ue, sip, dm, of))
    _process.start()

    return render_template('success.html', ue=ue, fn=fn)

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)

@app.route('/help')
def help():
    return render_template('help.html')
