'''Util classes'''

import os
import smtplib
import time
import shutil
import logging
import uuid
import sqlite3
import secrets
import bcrypt

class User:
    '''handle user info'''
    def __init__(self, useremail, password, subscription):
        self.ue = useremail
        self.pwd = password
        self.sub = subscription

class Password:
    '''handle password'''
    def __init__(self, password):
        self.pwd = password

    def hashpw(self):
        return bcrypt.hashpw(
            bytes(self.pwd, 'utf-8'),
            bcrypt.gensalt())

    def generate_toke(self):
        return secrets.token_urlsafe()

class Email:
    '''handle emails'''
    def __init__(self, to, message):
        # Set up the SMTP server
        self.server = smtplib.SMTP(os.getenv('G_SMTP'), 587)
        self.me = os.getenv('G_MAIL')
        self.to = to
        self.message = message
        self.server.starttls()
        self.server.login(self.me, os.getenv('G_KEY'))

    def send(self):
        self.server.sendmail(self.me, self.to, self.message)
        self.server.quit()
        logging.info(' > EMAIL to: %s', self.to)

class SqlAction:
    '''sql crud'''
    def __init__(self, tbl):
        self.tbl = tbl

    def db_createTable(self):
        '''create the initial table'''
        con = sqlite3.connect(self.tbl)
        try:
            cur = con.cursor()
            sqlcmd = '''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT NOT NULL, 
                        password TEXT NOT NULL,
                        subscription TEXT,
                        resettoken TEXT)'''
            cur.execute(sqlcmd)
            con.commit()
        finally:
            con.close()

    def db_insert(self, user):
        '''insert a new user'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''INSERT INTO users
                        (username, password) VALUES (?, ?)''',
                        (user.ue, user.pwd))
            con.commit()
        finally:
            con.close()

    def db_read(self, em):
        '''return user that logged in'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''SELECT * FROM users WHERE
                        username = ?''', (em, ))
            user = cur.fetchall()
            con.commit()
        finally:
            con.close()
        return user

    def db_update_pwd(self, em, password):
        '''update password after reset'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''UPDATE users
                        SET password = ? 
                        WHERE username = ?''',
                        (password, em))
            con.commit()
        finally:
            con.close()

    def db_subscription(self, em, subid):
        '''set new subscription id for user'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''UPDATE users
                        SET subscription = ? 
                        WHERE username = ?''',
                        (subid, em))
            con.commit()
        finally:
            con.close()

    def db_passtoke(self, em, token):
        '''set new token for user to reset pwd'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''UPDATE users
                        SET resettoken = ? 
                        WHERE username = ?''',
                        (token, em))
            con.commit()
        finally:
            con.close()

    def db_delete_token(self, em):
        '''set new token for user to reset pwd'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''UPDATE users
                        SET resettoken = NULL 
                        WHERE username = ?''',
                        (em, ))
            con.commit()
        finally:
            con.close()

class Track:
    '''process track and send email'''
    def __init__(self, attributes):

        self.atts = attributes
        self.flags = None
        self.filedir = f'./separated/{self.atts["dm"]}/{self.atts["cn"]}'
        self.zip = None

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

    def filenum(self, filecount):
        '''wait for filecount to = 4 or 6 based on model'''
        while len(os.listdir(self.filedir)) != filecount:
            self.giveprogress('STILL SEPARATING')

    def isdir(self):
        '''check if the directory exists'''

        while os.path.exists(self.filedir):
            if self.atts['dm'] == 'htdemucs_6s':
                self.filenum(6)
            else:
                self.filenum(4)
            return

        self.giveprogress('BUILDING DIR')
        self.isdir()

    def zippit(self):
        '''zip the directory'''
        logging.info(' < ZIP START: %s', self.atts["fn"])
        zipdir = f"{str(uuid.uuid4())}/{self.atts['fn'][:-4]}"
        self.zip = f"zips/{zipdir}"

        shutil.make_archive( self.zip, 'zip', self.filedir )

        logging.info(' > ZIPPED: %s', f'{zipdir}')

    def track_email(self):
        '''send track email'''
        subject = f'{self.atts["fn"]} Stems'
        link = f"https://{self.atts['sip']}/{self.zip}.zip"
        body = f'Download the zip file below to access stems: \
                \n{link} \
                \nThanks for using the demucs-gui.'

        message = f'Subject: {subject}\n\n{body}'
        mail = Email([self.atts['ue']], message)
        mail.send()
