'''Payment classes'''
import json
import os
import base64
import urllib.parse
from httplib2 import Http

class Payment:
    '''handle PayPal'''
    def __init__(self):
        assert os.getenv('P_CLIENT')
        assert os.getenv('P_SECRET')

        self.client_id = os.getenv('P_CLIENT')
        self.client_secret = os.getenv('P_SECRET')
        self.base_url = 'https://api-m.sandbox.paypal.com'


    def get_token(self):
        '''get token api call'''
        http = Http()
        auth = f"{self.client_id}:{self.client_secret}".encode()
        url = f'{self.base_url}/v1/oauth2/token'
        method = 'POST'
        body = {'grant_type': 'client_credentials'}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {base64.b64encode(auth).decode()}'
        }

        resp, pbody = http.request(url, method, body=urllib.parse.urlencode(body), headers=headers)
        pbody = json.loads(pbody.decode())

        print(resp.status)
        print('------')

        return pbody
