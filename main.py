'''runs hello'''
import os
import smtplib
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import send_from_directory
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

def email(fn):
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
    body = f'the file uploaded is called {fn}.'
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
            flash(f'{filename} was uploaded successfully. \
                \n You will receive an email when files are ready.')

            return redirect(url_for('success', name=filename))
    return render_template('upload.html')

@app.route('/<name>-success')
def success(name):
    '''show success after processing'''
    os.system('ls -al /tmp/plod')
    print('--------------------')
    os.system(f'ls /tmp/plod/{name}')
    os.system(f'demucs /tmp/plod/{name}')
    email(name)
    return render_template('fileloc.html')

@app.route('/static/<path:dirname>')
def serve_static(dirname):
    return send_from_directory('static', dirname)

# TODO: step 1 - serve any specified directory
# TODO: step 2 - serve the directory created by demucs
# TODO: step 3 - send myself the email ( this I already have working )
# TODO: step 4 - put the links to the new directories in there
# TODO: step 5 - have the user put in their email

# TODO: when in the return it just sends us to the file
