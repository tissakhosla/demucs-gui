'''Util classes'''

import os
import smtplib
import time
import shutil
import logging
import uuid
import sqlite3
import bcrypt

class User:
    '''handle user info'''
    def __init__(self, useremail, password):
        self.ue = useremail
        self.pwd = password

class Password:
    '''handle password'''
    def __init__(self, password):
        self.pwd = password

    def hashpw(self):
        return bcrypt.hashpw(
            bytes(self.pwd, 'utf-8'),
            bcrypt.gensalt())

class SqlAction:
    '''sql crud'''
    def __init__(self, tbl):
        self.tbl = tbl

    def db_createTable(self):
        '''create the initial table'''
        con = sqlite3.connect(self.tbl, check_same_thread=False)
        cur = con.cursor()
        sqlcmd = '''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT NOT NULL, 
                    password TEXT NOT NULL)'''
        cur.execute(sqlcmd)
        con.commit()
        con.close()

    def db_insert(self, user):
        '''insert a new user'''
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''INSERT INTO users
                    (username, password) VALUES (?, ?)''',
                    (user.ue, user.pwd))
        con.commit()
        con.close()

    def db_read(self, em):
        '''return user that logged in'''
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute(f'SELECT * FROM users WHERE \
                    username = "{em}"')
        user = cur.fetchall()
        con.commit()
        con.close()
        return user

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

    def message(self):
        '''build the email message'''
        subject = f'{self.atts["fn"]} Stems'
        link = f"http://{self.atts['sip']}/{self.zip}.zip"

        body = f'Download the zip file below to access stems: \
                \n{link} \
                \nThanks for using the demucs-gui.'

        return f'Subject: {subject}\n\n{body}'

    def sendmail(self):
        '''send email'''
        # Set up the SMTP server
        server = smtplib.SMTP(os.getenv('G_SMTP'), 587)
        server.starttls()
        # Login to the email account
        me = os.getenv('G_MAIL')
        server.login(me, os.getenv('G_KEY'))
        # Build the email
        server.sendmail(me, [self.atts['ue']], self.message())
        server.quit()
        logging.info(' > EMAIL to: %s', self.atts["ue"])
