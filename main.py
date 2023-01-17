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

# initialize db
TBL = 'track'

con = sqlite3.connect("tracks.db", check_same_thread=False)
cur = con.cursor()

trackTable = f'CREATE TABLE IF NOT EXISTS  \
            {TBL}(title, timestamp, user, code, status)'

cur.execute(trackTable)

# initialize Flask App

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = { 'wav' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12)

# confirm env vars

assert os.getenv('G_SMTP')
assert os.getenv('G_MAIL')
assert os.getenv('G_KEY')

# TODO: DB functions - Make into util class
# create
def db_insert(fn, ts, ue, cn, status):
    '''insert track data into db'''
    sqlcmd = f"INSERT into {TBL} VALUES \
    ('{fn}', {ts}, '{ue}', '{cn}', '{status}')"
    logging.info(' < SQLCMD: %s', sqlcmd)
    cur.execute(sqlcmd)
    con.commit()

# read
def db_all():
    sqlcmd = "SELECT * FROM track"
    res = cur.execute(sqlcmd)
    return res.fetchall()

def db_toptrack():
    sqlcmd = "SELECT * FROM track ORDER BY timestamp"
    res = cur.execute(sqlcmd)
    return res.fetchone()

# update
def db_update(uid):
    '''update demucsing track status to D'''
    sqlcmd = f"UPDATE track SET status = 'D' WHERE code = '{uid}'"
    res = cur.execute(sqlcmd)
    logging.info(' UPDATE: %s', res)
    con.commit()

# delete
def db_delete(uid):
    '''delete track'''
    sqlcmd = f"DELETE from track WHERE code = '{uid}'"
    res = cur.execute(sqlcmd)
    logging.info(' DELETE: %s', res)
    con.commit()

# TODO: App functions - Make into util class

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def check_status(s):
    for t in db_all():
        if t[4] == s:
            return True

def utime():
    '''create timestamp when called'''
    dt = datetime.now()
    return datetime.timestamp(dt)

def demucs(wav):
    '''run demucs and send email'''
    os.system(f'demucs /tmp/{wav}')
    db_delete(wav)
    pp.pprint(db_all())

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
        \n\n http://{ip}/separated/htdemucs/{uid}/bass.wav \
        \n http://{ip}/separated/htdemucs/{uid}/drums.wav \
        \n http://{ip}/separated/htdemucs/{uid}/other.wav \
        \n http://{ip}/separated/htdemucs/{uid}/vocals.wav'

    msg = f'Subject: {subject}\n\n{body}'
    server.sendmail(me, to, msg)

    # Disconnect from the server
    server.quit()

def process(host):
    '''process the oldest track in the db'''
    t = db_toptrack()
    db_update(t[3])
    demucs(t[3])
    email(t[3], t[0], t[2], host)

def process_tracks(req_host):
    '''process all tracks in DB'''
    process(req_host)
    if check_status('W'):
        process(req_host)
    if check_status('N'):
        process(req_host)
    else:
        print("no tracks left")

@app.route("/")
def to_upload():
    return redirect('/upload')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    '''main route'''
    logging.info(' START: a wild user has appeared')
    logging.info(' SERVER: %s', request.host)
    logging.info(' CLIENT: %s', request.environ['REMOTE_ADDR'])

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
            fp = os.path.join(app.config['UPLOAD_FOLDER'], codename)
            file.save(fp)
            # TODO: assert os.path.exists(fp)

            return redirect(url_for('success', cn=codename, fn=filename, ue=useremail))
    return render_template('upload.html')

@app.route('/success-<cn>')
def success(cn):
    '''show success after saving file'''
    os.system(f'ls /tmp/{cn}')
    ue = request.args.get('ue')
    fn = request.args.get('fn')

    if check_status('D'):
        # oops D is done and the file no longer there?!
        db_insert(fn, utime(), ue, cn, 'W')
    else:
        db_insert(fn, utime(), ue, cn, 'N')

    _process_tracks = Thread(target=process_tracks, args=(request.host,))
    _process_tracks.start()

    return render_template('success.html', ue=ue, fn=fn)

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)



# TODO: State Machine - N, W, D, E(liminated)
# TODO: clean up all the code - make 2 helper classes
# TODO: cn in the db should be defined as a unique key
# TODO: use unique increment field instead UNIX time
# TODO: atomic database push and pop
# TODO: 2 db ops insert, delete
# TODO: infinite loop module to demucs topfile

# TODO: sqlite transaction call
# TODO: add start time and end time to job

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
