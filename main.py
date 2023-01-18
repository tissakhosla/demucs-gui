'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''
import os
import smtplib
import uuid
import logging
import sqlite3

from datetime import datetime
from threading import Thread

import pprint
pp = pprint.PrettyPrinter(indent=4)


from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory
)

from werkzeug.utils import secure_filename

# setup logging
logging.basicConfig(level=logging.INFO)

# initialize Flask App

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = { 'wav' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12)

# confirm env vars

assert os.getenv('G_SMTP')
assert os.getenv('G_MAIL')
assert os.getenv('G_KEY')

# TODO: App functions - Make into util class

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def utime():
    '''create timestamp when called'''
    dt = datetime.now()
    return datetime.timestamp(dt)

def email(uid, fn, em, ip):
    '''send email'''
    # Set up the SMTP server
    server = smtplib.SMTP(os.getenv('G_SMTP'), 587)
    server.starttls()

    # Login to the email account
    me = os.getenv('G_MAIL')
    server.login(me, os.getenv('G_KEY'))

    logging.info(' > to: %s', em)
    # Build the email
    to = [em]
    subject = f'{fn} Split Tracks'

    body = f'Here are the links your files: \
        \n\n http://{ip}/separated/mdx_extra_q/{uid}/bass.wav \
        \n http://{ip}/separated/mdx_extra_q/{uid}/drums.wav \
        \n http://{ip}/separated/mdx_extra_q/{uid}/other.wav \
        \n http://{ip}/separated/mdx_extra_q/{uid}/vocals.wav'

    msg = f'Subject: {subject}\n\n{body}'
    server.sendmail(me, to, msg)

    # Disconnect from the server
    server.quit()

def demucs(path):
    os.system(f'echo {path} > ~/demucs/demucs-gui/fpipe')

def process(path, code, trackname, uemail, hostip):
    demucs(path)
    email(code, trackname, uemail, hostip)

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

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            logging.info(' < FILE: %s', filename)
            logging.info(' < TYPE: %s', file.content_type)
            logging.info(' < SIZE: %s bytes', len(file.read()))
            file.seek(0)
            codename = str(uuid.uuid4())

            # write file to FS
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], codename)
            file.save(filepath)
            print(filename)

            return redirect(url_for(
                'success',
                fp=filepath,
                cn=codename,
                fn=filename,
                ue=useremail, 
                sip=server_ip))
    return render_template('upload.html')

@app.route('/success')
def success():
    '''show success after saving file'''
    fp = request.args.get('fp')
    cn = request.args.get('cn')
    fn = request.args.get('fn')
    ue = request.args.get('ue')
    sip = request.args.get('sip')

    _process = Thread(target=process, args=(fp, cn, fn, ue, sip))
    _process.start()

    return render_template('success.html', ue=ue, fn=fn)

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)


# TODO: add license
# TODO: add start time and end time to job
# TODO: get a smaller reserved instance
# TODO: enlarge the disk and extend the fs
# TODO: if I update demucs in PRD, it'll use the new one
# TODO: in PRD the path is 'separated/mdx_extra_q/...'
# TODO: create new email address to handle all this
# TODO: Use Official LTS Ubuntu Linux for ec2
# TODO: <♩♩♩♩/> and make it an HTML email
# TODO: https://flask.palletsprojects.com/en/2.2.x/logging/#email-errors-to-admins
# TODO: Get DNS
# TODO: Make the frontend pretty (CSS)
# TODO: cron removal of separated tracks once a week
# TODO: confirm when /tmp/ is emptied
# TODO: don't use flask built in server in PRD