'''Payment classes'''
import os
import base64
import urllib.parse
import json
from hreq import call

class Payment:
    '''handle PayPal'''
    def __init__(self):
        assert os.getenv('P_CLIENT')
        assert os.getenv('P_SECRET')

        self.client_id = os.getenv('P_CLIENT')
        self.client_secret = os.getenv('P_SECRET')
        self.base_url = 'https://api-m.sandbox.paypal.com'

        self.access_token = None
        self.plans = None
        self.products = None
        self.prod_id = None
        self.plan_id = None
        self.sub_detail = None

    # CREATE
    def create_billing(self):
        '''create billing plan'''
        body = {
            'product_id': self.prod_id,
            'name': 'Demucs GUI Subscription',
            'description': 'service for demucs gui',
            'type': 'DIGITAL',
            'status': 'ACTIVE',
            'billing_cycles': [
                {
                    'frequency': {
                        'interval_unit': 'MONTH',
                        'interval_count': 1
                    },
                    'tenure_type': 'REGULAR',
                    'sequence': 1,
                    'total_cycles': 0,
                    'pricing_scheme': {
                        'fixed_price': {
                            'value': '6',
                            'currency_code': 'USD',
                        }
                    }
                }
            ],
            'payment_preferences': {
                'auto_bill_outstanding': True,
                'payment_failure_threshold': 2
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }

        response = call(
            f'{self.base_url}/v1/billing/plans',
            'POST',
            body=json.dumps(body),
            headers=headers)

        self.plan_id = response['id']

    def create_product(self):
        '''create the demucs subscription product'''
        body = {
            'name': 'Demucs GUI Subscription',
            'description': 'service for demucs gui',
            'type': 'DIGITAL',
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }

        response = call(
            f'{self.base_url}/v1/catalogs/products',
            'POST',
            body=json.dumps(body),
            headers=headers)

        self.prod_id = response['id']

    # READ
    def get_token(self):
        '''get token api call'''
        body = {'grant_type': 'client_credentials'}
        auth = f"{self.client_id}:{self.client_secret}".encode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {base64.b64encode(auth).decode()}'
        }

        response = call(
            f'{self.base_url}/v1/oauth2/token',
            'POST',
            body=urllib.parse.urlencode(body),
            headers=headers)

        self.access_token = response['access_token']

    def get_plans(self):
        '''get payment plans'''
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        response = call(
            f'{self.base_url}/v1/billing/plans',
            headers=headers
        )

        self.plans = response

    def get_products(self):
        '''get products'''
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        response = call(
            f'{self.base_url}/v1/catalogs/products',
            headers=headers
        )

        self.products = response

    def get_sub_status(self, sid):
        '''get details regarding a subscription'''

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        response = call(
            f'{self.base_url}/v1/billing/subscriptions/{sid}',
            headers=headers
        )

        return response['status']
