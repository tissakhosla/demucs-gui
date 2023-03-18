"""wrapper for Http.request"""
import logging
import json
from httplib2 import Http


def call(url, method='GET', body=None, headers=None):
    """ref: https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html"""
    logging.info('Q %8s %s', method, url)

    qbody = body if body else None

    http = Http()

    resp, pbody = http.request(url, method, body=qbody, headers=headers)

    if pbody:
        pbody = json.loads(pbody.decode())

    if resp.status not in (200,201):
        logging.fatal('!! %d: %s', resp.status, pbody)

    assert resp.status in (200,201)

    return pbody
