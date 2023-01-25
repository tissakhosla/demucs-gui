'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''

import os
import smtplib
import uuid
import logging
import time

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
    'htdemucs', 'htdemucs_ft', 'htdemucs_6s', 'hdemucs_mmi',
    'mdx', 'mdx_extra', 'mdx_q', 'mdx_extra_q']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12)

# confirm env vars
assert os.getenv('G_SMTP')
assert os.getenv('G_MAIL')
assert os.getenv('G_KEY')

class Track:
    '''process track and send email'''
    def __init__(self, attributes):

        self.atts = attributes
        self.flags = None

    def demucs(self):
        '''send command to pipe'''
        os.system(f'echo demucs {self.flags} > fpipe')

    def setflags(self):
        '''create flags for cmd'''
        if self.atts['of'] == 'mp3':
            self.flags = f'--mp3 -n {self.atts["dm"]} {self.atts["fp"]}'
        else:
            self.flags = f'-n {self.atts["dm"]} {self.atts["fp"]}'

    def giveprogress(self, logmsg):
        '''log mesg every 5 seconds w status'''
        time.sleep(5)
        logging.info(' < %s: %s for %s', logmsg, self.atts['fn'], self.atts['ue'])

    def filenum(self, filedir, filecount):
        '''wait for filecount to = 4 or 6 based on model'''
        while len(os.listdir(filedir)) != filecount:
            self.giveprogress('STILL SEPARATING')

    def isdir(self):
        '''check if the directory exists'''
        filedir = f'./separated/{self.atts["dm"]}/{self.atts["cn"]}'

        while os.path.exists(filedir):
            if self.atts['dm'] == 'htdemucs_6s':
                self.filenum(filedir, 6)
            else:
                self.filenum(filedir, 4)
            return

        self.giveprogress('BUILDING DIR')
        self.isdir()

    def message(self):
        '''build the email message'''

        ip = self.atts['sip']
        dm = self.atts['dm']
        cn = self.atts['cn']
        of = self.atts['of']

        stems = ['bass', 'drums', 'other', 'vocals', 'guitar', 'piano']

        subject = f'{self.atts["fn"]} Stems'
        link = 'http://{}/separated/{}/{}/{}.{} \n'
        body = 'Here are links to your files: \n'

        if dm == 'htdemucs_6s':
            for stem in stems:
                body += link.format(ip, dm, cn, stem, of)
        else:
            for stem in stems[:4]:
                body += link.format(ip, dm, cn, stem, of)

        body += 'Thanks for using the demucs-gui.'
        return f'Subject: {subject}\n\n{body}'

    def email(self):
        '''send email'''
        # Set up the SMTP server
        server = smtplib.SMTP(os.getenv('G_SMTP'), 587)
        server.starttls()

        # Login to the email account
        me = os.getenv('G_MAIL')
        server.login(me, os.getenv('G_KEY'))

        # Build the email
        to = [self.atts['ue']]
        msg = self.message()
        server.sendmail(me, to, msg)

        server.quit()
        logging.info(' > EMAIL to: %s', self.atts["ue"])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def process(a):
    '''initialize Track class and run methods'''
    t = Track(a)
    t.setflags()
    t.demucs()
    t.isdir()
    t.email()

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
    atts = {'fp': request.args.get('fp'),
            'cn': request.args.get('cn'),
            'fn': request.args.get('fn'),
            'ue': request.args.get('ue'),
            'sip': request.args.get('sip'),
            'dm': request.args.get('dm'),
            'of': request.args.get('of')}

    _process = Thread(target=process, args=(atts,))
    _process.start()

    return render_template('success.html', ue=atts['ue'], fn=atts['fn'])

@app.route('/separated/<path:filename>')
def serve_static(filename):
    return send_from_directory('separated', filename)

@app.route('/help')
def _help():
    return render_template('help.html')

@app.route('/license')
def _license():
    return render_template('license.html')
