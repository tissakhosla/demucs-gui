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

from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory
)

from werkzeug.utils import secure_filename

# setup logging
logging.basicConfig(level=logging.INFO)

# initialize db
TBL = 'track'
con = sqlite3.connect("tracks.db", check_same_thread=False)
cur = con.cursor()
trackTable = f'CREATE TABLE IF NOT EXISTS  \
            {TBL}(title, timestamp, user, code)'
cur.execute(trackTable)

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = { 'wav' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12)

assert os.getenv('G_SMTP')
assert os.getenv('G_MAIL')
assert os.getenv('G_KEY')

def insert(fn, ts, ue, cn):
    '''insert track data into db'''
    sqlcmd = f"INSERT into {TBL} VALUES \
    ('{fn}', {ts}, '{ue}', '{cn}')"
    logging.info(' < SQLCMD: %s', sqlcmd)
    cur.execute(sqlcmd)
    con.commit()

def utime():
    '''create timestamp when called'''
    dt = datetime.now()
    print(dt)
    return datetime.timestamp(dt)

def demucs(wav, f, em, url):
    os.system(f'demucs /tmp/{wav}')
    email(wav, f, em, url)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def email(c, f, e, u):
    '''send email'''
    # Set up the SMTP server
    server = smtplib.SMTP(os.getenv('G_SMTP'), 587)
    server.starttls()

    # Login to the email account
    me = os.getenv('G_MAIL')
    server.login(me, os.getenv('G_KEY'))

    logging.info(' > to: %s', e)
    # Build the email
    to = [e]
    subject = f'{f} Split Tracks'

    body = f'Here are the links your files: \
        \n\n http://{u}/separated/htdemucs/{c}/bass.wav \
        \n http://{u}/separated/htdemucs/{c}/drums.wav \
        \n http://{u}/separated/htdemucs/{c}/other.wav \
        \n http://{u}/separated/htdemucs/{c}/vocals.wav'

    msg = f'Subject: {subject}\n\n{body}'
    server.sendmail(me, to, msg)

    # Disconnect from the server
    server.quit()

@app.route("/")
def to_upload():
    print(utime())
    return redirect('/upload')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    '''main route'''
    logging.info(' START: a wild user has appeared')
    logging.info(' SERVER: %s', request.host)
    if request.method == 'POST':

        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        useremail = request.form['email']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            logging.info(' < file: %s', filename)
            logging.info(' < type: %s', file.content_type)
            logging.info(' < size: %s bytes', len(file.read()))
            file.seek(0)
            codename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], codename))

            insert(filename, utime(), useremail, codename)

            return redirect(url_for('success', cn=codename, fn=filename, ue=useremail))
    return render_template('upload.html')

@app.route('/success-<cn>')
def success(cn):
    '''show success after processing'''
    os.system(f'ls /tmp/{cn}')
    ue = request.args.get('ue')
    fn = request.args.get('fn')
    _demucs = Thread(target=demucs, args=(cn, fn, ue, request.host))
    # _demucs.start()
    return render_template('success.html', ue=ue, fn=fn)

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)


# TODO: use sqlite3
# TODO: get better variable names throughout
# TODO: add start time and end time to job
# TODO: use flask-session to keep state
# TODO: get a smaller reserved instance
# TODO: enlarge the disk and extend the fs
# TODO: if I update demucs in PRD, it'll use the new one
# TODO: in PRD the path is 'separated/mdx_extra_q/...'
# TODO: we will need options on the GUI once we use the new update
# TODO: create new email address to handle all this
# TODO: Use Official LTS Ubuntu Linux for ec2
# TODO: <♩♩♩♩/> and make it an HTML email
# TODO: https://flask.palletsprojects.com/en/2.2.x/logging/#email-errors-to-admins
# TODO: Get DNS
# TODO: Make the frontend pretty (CSS)
