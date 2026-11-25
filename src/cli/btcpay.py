'''
BTCPay (Greenfield API) client of the Meile app.

The app creates the invoices it shows itself, with a fine-grained API key of
the store that may only create invoices (btcpay.store.cancreateinvoice): such a
key cannot read an invoice of the store (a GET of
/api/v1/stores/<id>/invoices answers 403), so a key recovered from the
obfuscated app cannot look up who paid what, and it cannot modify, refund or
pay anything either.

That is why the state of an invoice is never read here.  The app asks the plan
API instead (meile-plan-rest), which holds the view-only key of the store and
answers for one invoice id whether it was paid - see
HTTParams.API_INVOICE_STATUS and /v1/invoice/status there.  The flow this
replaces used a pickled BitPay client handed out by the fiat gateway on
aimokoivunen.mathnodes.com, whose merchant token could read and create invoices
and was therefore worth recovering from the app.
'''

from adapters import HTTPRequests
from fiat.stripe_pay.dist import scrtsxx
from typedef.konstants import HTTParams


class BTCPayGreenfield():
    '''
    Create invoices on the BTCPay store of the app with the create-only key.

    The store, its id and the key are read from scrtsxx.py (BTCPAYSERVER,
    BTCPAY_STORE_ID, BTCPAY_API_KEY) when they are not passed in, so a build
    only has to fill them in there.
    '''

    def __init__(self, base=None, store=None, key=None, timeout=None):
        self.base    = str(base or getattr(scrtsxx, 'BTCPAYSERVER', '') or '').rstrip('/')
        self.store   = str(store or getattr(scrtsxx, 'BTCPAY_STORE_ID', '') or '')
        self.key     = str(key or getattr(scrtsxx, 'BTCPAY_API_KEY', '') or '')
        self.timeout = timeout or HTTParams.BTCPAY_TIMEOUT

    def configured(self):
        '''True when the store, its id and the create-only key are set.'''
        return bool(self.base and self.store and self.key)

    def create_invoice(self, amount, currency='USD', metadata=None,
                       checkout=None):
        '''
        Create an invoice for AMOUNT of CURRENCY and return it.

        The invoice is quoted in ``currency`` and answers with its ``id``, its
        ``status`` (``New`` until it is paid), the ``checkoutLink`` the app
        opens in a browser and the ``checkout`` options it was created with.
        It carries no payment method: BTCPay adds the address of every method
        of the store a moment later, so the address of the coin the user picked
        is asked for at the plan API, which is also where the state of the
        invoice is read from (see the module docstring).

        ``metadata`` is what the plan API reads the buyer back from
        (``buyerName``: the wallet of a plan subscription, the app UUID of an
        SMS top-up), ``checkout`` carries the speed policy (``HighSpeed``
        credits a 0 confirmation payment) and the method the checkout page
        opens on.  Raises on a store that cannot be reached or answers with an
        error, so the caller can tell the user instead of waiting forever.
        '''
        if not self.configured():
            raise RuntimeError('BTCPay is not configured: BTCPAYSERVER, '
                               'BTCPAY_STORE_ID and BTCPAY_API_KEY must be '
                               'set in scrtsxx.py')

        payload = {'amount'  : str(amount),
                   'currency': str(currency)}
        if metadata:
            payload['metadata'] = metadata
        if checkout:
            payload['checkout'] = checkout

        Request = HTTPRequests.MakeRequest(TIMEOUT=self.timeout)
        http = Request.hadapter()
        response = http.post(
            '%s/api/v1/stores/%s/invoices' % (self.base, self.store),
            json=payload,
            headers={'Authorization': 'token ' + self.key,
                     'Content-Type': 'application/json'})

        if response.status_code != 200:
            raise RuntimeError('BTCPay answered with status %s'
                               % response.status_code)

        invoice = response.json()
        if not isinstance(invoice, dict) or not invoice.get('id'):
            raise RuntimeError('BTCPay answered without an invoice')

        return invoice
