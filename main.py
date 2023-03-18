'''
A user can upload a file
Demucs will split it
On success, we will send the user an email
'''
import os
import logging
import uuid
from threading import Thread

from flask import (
    Flask, render_template, request, flash,
    redirect, url_for, send_from_directory,
    make_response
)

import bcrypt
from werkzeug.utils import secure_filename
from util import (Track, SqlAction,
    User, Password, Email
)

from pay import Payment

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

# confirm env
assert os.path.exists(UPLOAD_FOLDER)
assert os.getenv('G_SMTP')
assert os.getenv('G_MAIL')
assert os.getenv('G_KEY')
assert os.getenv('P_CLIENT')
# TODO: assert ./listener is running

# initialize DB
sqla = SqlAction("users.db")
sqla.db_createTable()

def allowed_file(filename):
    '''check filename safety'''
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def process(a):
    '''initialize Track class and run methods'''
    t = Track(a)
    t.setflags()
    t.demucs()
    t.isdir()
    t.zippit()
    t.track_email()



@app.route("/")
def index():
    '''check if user is logged in'''
    if request.cookies.get('demucs user'):
        return redirect('/upload')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''create a useremail and password'''
    if request.method == 'POST':

        if request.form['password'] != request.form['first-pass']:
            flash('Passwords do not match')
            return render_template('register.html')

        pwd = Password(request.form['password'])
        new_user = User(request.form['email'], pwd.hashpw(), None)

        if sqla.db_read(new_user.ue):
            flash(f'{new_user.ue} is already registered')
            return render_template('register.html')

        sqla.db_insert(new_user)

        subject = 'Demucs-gui registration Successful'
        body = f'Please see the {request.host}/help section for instructions. \
                    \nGood shedding, \
                    \nTissa'
        em = Email([new_user.ue], f'Subject: {subject}\n\n{body}')
        em.send()

        res = make_response(redirect(url_for('_subscribe')))
        res.set_cookie("demucs user", new_user.ue, max_age=900, secure=True)

        return res

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''user login'''
    if request.cookies.get('demucs user'):
        return redirect('/upload')

    if request.method == 'POST':
        net_pwd = bytes(request.form['password'], 'utf-8')
        db_user = sqla.db_read(request.form['email'])

        if db_user:
            db_pwd = db_user[0][2]

            if bcrypt.checkpw(net_pwd, db_pwd):
                res = make_response(redirect(url_for('upload_file')))
                res.set_cookie("demucs user", db_user[0][1], max_age=900)
                return res

        flash('Incorrect username or password')
    return render_template('login.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    '''main route'''

    if not request.cookies.get('demucs user'):
        flash('Please login before file upload')
        return redirect(url_for('login'))

    if not sqla.db_read(request.cookies.get('demucs user'))[0][3]:
        flash('Please subscribe before file upload')
        return redirect(url_for('_subscribe'))

    p = Payment()
    p.get_token()
    status = p.is_sub_active(
        sqla.db_read(request.cookies.get('demucs user'))[0][3])

    if status['status'] != 'ACTIVE':
        flash('Please reactivate subscription')
        return redirect(url_for('_subscribe'))

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

    return render_template('upload.html',
                        models=MODELS,
                        login=request.cookies.get('demucs user'))

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

    return render_template(
        'success.html',
        ue=atts['ue'],
        fn=atts['fn'],
        login=request.cookies.get('demucs user'))

@app.route('/zips/<path:filename>')
def serve_zip(filename):
    return send_from_directory('zips', filename)

@app.route('/help')
def _help():
    return render_template('help.html',
            login=request.cookies.get('demucs user'))

@app.route('/license')
def _license():
    return render_template('license.html',
            login=request.cookies.get('demucs user'))

@app.route('/subscribe')
def _subscribe():
    if not request.cookies.get('demucs user'):
        flash('Please login before subscribing')
        return redirect(url_for('login'))

    p = Payment()
    p.get_token()
    p.get_plans()
    plan_id = p.plans['plans'][0]['id']
    client = os.getenv('P_CLIENT')
    src = f'https://www.paypal.com/sdk/js?client-id={client}&vault=true&intent=subscription'

    return render_template('subscribe.html', pid=plan_id, src=src)

@app.route('/sub-id', methods=['POST'])
def _save_sub_id():
    if request.method == 'POST':
        sqla.db_subscription(
            request.cookies.get('demucs user'),
            request.form['subscription_id']
        )

        return redirect(url_for('upload_file'))
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
