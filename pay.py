'''Payment classes'''
import json
import os
from httplib2 import Http

class Payment:
    '''handle PayPal'''
    def __init__(self):
        # TODO move to env
        assert os.getenv('P_CLIENT')
        assert os.getenv('P_SECRET')

        self.client_id = os.getenv('P_CLIENT')
        self.client_secret = os.getenv('P_SECRET')
        self.base_url = 'https://api-m.sandbox.paypal.com'


    def get_token(self):
        '''get token api call'''
        http = Http()

        url = f'{self.base_url}/v1/oauth2/token'
        method = 'POST'
        body = 'grant_type=client_credentials'
        headers = { 'Accept': 'application/json' }

        resp, pbody = http.request(url, method, body, headers)
        pbody = json.loads(pbody.decode())

        print(resp.status)
        print('------')
        return pbody
