#!/usr/bin/env python3
'''
Standalone test for the BTCPay Greenfield client of the app (cli/btcpay.py).

The client only needs scrtsxx.py, adapters.HTTPRequests and HTTParams, so the
Kivy stack of the app is not imported here: those modules are replaced with
small stand-ins and the client is loaded from its file.  Run with:

    python3 tests/btcpay_greenfield_test.py
'''

import importlib.util
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLIENT = os.path.join(ROOT, 'src', 'cli', 'btcpay.py')

BASE = 'https://btcpay.example'
STORE = 'StoreId123'
KEY = 'test-key'


class FakeResponse():
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession():
    '''The HTTP session of the client, recording what it was asked for.'''

    def __init__(self):
        self.calls = []
        self.answer = FakeResponse({'id': 'invoice-1'})

    def post(self, url, json=None, headers=None):
        self.calls.append({'url': url, 'json': json, 'headers': headers})
        return self.answer


class FakeHTTPRequests():
    def __init__(self, session):
        self.session = session

    def MakeRequest(self, TIMEOUT=None, headers=None):
        return self

    def hadapter(self):
        return self.session


def load_client(session, **config):
    '''Load cli/btcpay.py against stand-ins for its three imports.'''
    scrtsxx = types.ModuleType('scrtsxx')
    for name, value in config.items():
        setattr(scrtsxx, name, value)

    dist = types.ModuleType('fiat.stripe_pay.dist')
    dist.scrtsxx = scrtsxx
    stripe_pay = types.ModuleType('fiat.stripe_pay')
    stripe_pay.dist = dist
    fiat = types.ModuleType('fiat')
    fiat.stripe_pay = stripe_pay

    adapters = types.ModuleType('adapters')
    adapters.HTTPRequests = FakeHTTPRequests(session)

    konstants = types.ModuleType('typedef.konstants')
    konstants.HTTParams = type('HTTParams', (), {'BTCPAY_TIMEOUT': 30})
    typedef = types.ModuleType('typedef')
    typedef.konstants = konstants

    modules = {
        'fiat'                : fiat,
        'fiat.stripe_pay'     : stripe_pay,
        'fiat.stripe_pay.dist': dist,
        'adapters'            : adapters,
        'typedef'             : typedef,
        'typedef.konstants'   : konstants,
    }
    saved = {name: sys.modules.get(name) for name in modules}
    sys.modules.update(modules)

    try:
        spec = importlib.util.spec_from_file_location('btcpay_client', CLIENT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value

    return module


def main():
    failures = []

    def check(name, condition):
        print(('PASS' if condition else 'FAIL') + ': ' + name)
        if not condition:
            failures.append(name)

    session = FakeSession()
    module = load_client(session, BTCPAYSERVER=BASE, BTCPAY_STORE_ID=STORE,
                         BTCPAY_API_KEY=KEY)

    client = module.BTCPayGreenfield()
    check('the store, its id and the key come from scrtsxx.py',
          client.configured() is True)

    invoice = client.create_invoice(
        12.5,
        metadata={'buyerName': 'sent1wallet', 'itemDesc': 'plan'},
        checkout={'speedPolicy': 'HighSpeed',
                  'defaultPaymentMethod': 'XMR-CHAIN'})

    check('the invoice is created on the store of the key',
          session.calls[-1]['url'] == '%s/api/v1/stores/%s/invoices'
          % (BASE, STORE))
    check('the create-only key is sent as a token',
          session.calls[-1]['headers']['Authorization'] == 'token ' + KEY)
    payload = session.calls[-1]['json']
    check('the amount is quoted in USD',
          payload['amount'] == '12.5' and payload['currency'] == 'USD')
    check('the buyer is put into the metadata',
          payload['metadata']['buyerName'] == 'sent1wallet')
    check('the checkout options are passed on',
          payload['checkout']['speedPolicy'] == 'HighSpeed'
          and payload['checkout']['defaultPaymentMethod'] == 'XMR-CHAIN')
    check('the invoice is returned', invoice['id'] == 'invoice-1')

    # A store that answers with an error must not look like a created invoice.
    session.answer = FakeResponse({'message': 'forbidden'}, 403)
    try:
        client.create_invoice(1)
        check('an error of the store raises', False)
    except Exception as e:
        check('an error of the store raises', '403' in str(e))

    session.answer = FakeResponse({'message': 'no invoice'})
    try:
        client.create_invoice(1)
        check('an answer without an invoice raises', False)
    except Exception:
        check('an answer without an invoice raises', True)

    # An unconfigured client must not ask the store at all.
    empty = load_client(session, BTCPAYSERVER='', BTCPAY_STORE_ID='',
                        BTCPAY_API_KEY='')
    calls = len(session.calls)
    check('an unconfigured client is not configured',
          empty.BTCPayGreenfield().configured() is False)
    try:
        empty.BTCPayGreenfield().create_invoice(1)
        check('an unconfigured client raises', False)
    except Exception:
        check('an unconfigured client raises', True)
    check('... without asking the store', len(session.calls) == calls)

    print()
    if failures:
        print('%s checks FAILED' % len(failures))
        return 1
    print('All BTCPay Greenfield client tests passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
