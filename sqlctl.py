'''handle sql actions'''
import sqlite3

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
                        sub_id TEXT,
                        sub_status TEXT,
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

    def db_update_sub_stat(self, em, status):
        '''update user subscription status'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''UPDATE users
                        SET sub_status = ? 
                        WHERE username = ?''',
                        (status, em))
            con.commit()
        finally:
            con.close()

    def db_subscription(self, em, subid):
        '''set new subscription id for user'''
        con = sqlite3.connect('users.db')
        try:
            cur = con.cursor()
            cur.execute('''UPDATE users
                        SET sub_id = ? 
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
