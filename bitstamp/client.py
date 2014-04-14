__author__ = 'kmadac'

# set to True to write debug log with each API call to /tmp/xwrap_requests
MONITOR = False

import requests
import datetime
import time
import hmac
import hashlib
import sys

# some code to monitor traffic a bit...
if MONITOR:
    _org_get = requests.get
    def get_proxy(url, *args, **kwargs):
        open('/tmp/xwrap_requests', 'a').write(
            '%s - %s\n' % (
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                url))
        return _org_get(url, *args, **kwargs)
    requests.get = get_proxy

    _org_post = requests.post
    def post_proxy(url, *args, **kwargs):
        open('/tmp/xwrap_requests', 'a').write(
            '%s - %s\n' % (
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                url))
        return _org_post(url, *args, **kwargs)
    requests.post = post_proxy

class JSONError(Exception):
    """Raised when JSON could not be decoded
    """

def get_json_data(request):
    if request.status_code >= 400:
        request.raise_for_status()
    if request.headers.get('content-type', '').startswith('application/json'):
        return request.json()
    raise JSONError(request.content)

class public():
    def __init__(self, proxydict=None):
        self.proxydict = proxydict

    def ticker(self):
        """Return ticker information
        """
        r = requests.get(
            "https://www.bitstamp.net/api/ticker/", proxies=self.proxydict)
        return get_json_data(r)

    def order_book(self, group=True):
        """Returns JSON dictionary with "bids" and "asks".

        Each is a list of open orders and each order is represented as
        a list of price and amount.
        """
        params = {'group': group}

        r = requests.get(
            "https://www.bitstamp.net/api/order_book/",
            params=params, proxies=self.proxydict)
        return get_json_data(r)

    def transactions(self, timedelta_secs=86400):
        """Transactions for the last 'timedelta' seconds
        """
        params = {'timedelta': timedelta_secs}

        r = requests.get(
            "https://www.bitstamp.net/api/transactions/",
            params=params, proxies=self.proxydict)
        return get_json_data(r)

    def bitinstant_reserves(self):
        """Bitinstant USD reserves
        
        Returns simple dictionary {'usd': 'Bitinstant USD reserves'}
        """
        r = requests.get(
            "https://www.bitstamp.net/api/bitinstant/",
            proxies=self.proxydict)
        return get_json_data(r)

    def conversion_rate_usd_eur(self):
        """Conversion rate from USD to EUR
        
        Returns simple dictionary
        
        {'buy': 'buy conversion rate', 'sell': 'sell conversion rate'}
        """
        r = requests.get(
            "https://www.bitstamp.net/api/eur_usd/",
            proxies=self.proxydict)
        return get_json_data(r)


class trading():
    def __init__(self, username, key, secret, proxydict=None):
        self.proxydict = proxydict
        self.username = username
        self.key = key
        self.secret = secret
        self.nonce = int(time.time())
        
    def get_params(self):
        params = {}
        params['key'] = self.key
        msg = str(self.nonce) + self.username + self.key

        if sys.version_info.major == 2:
            signature = hmac.new(
                self.secret, msg=msg, digestmod=hashlib.sha256
            ).hexdigest().upper()
        else:
            signature = hmac.new(
                str.encode(self.secret), msg=str.encode(msg),
                digestmod=hashlib.sha256
            ).hexdigest().upper()
        params['signature'] = signature
        params['nonce'] = self.nonce
        self.nonce += 1
        return params

    def account_balance(self):
        """Returns the balances for this account

        Returns dictionary:
        {u'btc_reserved': u'0',
         u'fee': u'0.5000',
         u'btc_available': u'2.30856098',
         u'usd_reserved': u'0',
         u'btc_balance': u'2.30856098',
         u'usd_balance': u'114.64',
         u'usd_available': u'114.64'}
        """
        params = self.get_params()
        r = requests.post(
            "https://www.bitstamp.net/api/balance/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def user_transactions(self, offset=0, limit=100, descending=True):
        """Returns descending list of transactions
        
        Every transaction (dictionary) contains
        {u'usd': u'-39.25',
         u'datetime': u'2013-03-26 18:49:13',
         u'fee': u'0.20', u'btc': u'0.50000000',
         u'type': 2,
         u'id': 213642}
        """
        params = self.get_params()
        params['offset'] = offset
        params['limit'] = limit
        if descending:
            params['sort'] = "desc"
        else:
            params['sort'] = "asc"

        r = requests.post(
            "https://www.bitstamp.net/api/user_transactions/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def open_orders(self):
        """Returns JSON list of open orders
        
        Each order is represented as dictionary:
        """
        params = self.get_params()
        r = requests.post(
            "https://www.bitstamp.net/api/open_orders/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def cancel_order(self, order_id):
        """Cancel the order specified by order_id

        Returns True if order was successfully canceled,
        otherwise tuple (False, msg) like (False, u'Order not found')
        """
        params = self.get_params()
        params['id'] = order_id
        r = requests.post(
            "https://www.bitstamp.net/api/cancel_order/",
            data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.text == u'true':
                return True
            else:
                data = get_json_data(r)
                if 'error' in data:
                    return False, data['error']
                return False, data
        else:
            r.raise_for_status()

    def buy_limit_order(self, amount, price):
        """
        Order to buy amount of bitcoins for specified price
        """
        params = self.get_params()
        params['amount'] = amount
        params['price'] = price

        r = requests.post(
            "https://www.bitstamp.net/api/buy/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def sell_limit_order(self, amount, price):
        """
        Order to buy amount of bitcoins for specified price
        """
        params = self.get_params()
        params['amount'] = amount
        params['price'] = price

        r = requests.post(
            "https://www.bitstamp.net/api/sell/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data
            
    def check_bitstamp_code(self, code):
        """Returns USD and BTC amount included in given bitstamp code
        """
        params = self.get_params()
        params['code'] = code
        r = requests.post(
            "https://www.bitstamp.net/api/check_code/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def redeem_bitstamp_code(self, code):
        """Returns USD and BTC amount added to user's account
        """
        params = self.get_params()
        params['code'] = code
        r = requests.post(
            "https://www.bitstamp.net/api/redeem_code/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def withdrawal_requests(self):
        """Returns list of withdrawal requests
        
        Each request is represented as dictionary
        """
        params = self.get_params()
        r = requests.post(
            "https://www.bitstamp.net/api/withdrawal_requests/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def bitcoin_withdrawal(self, amount, address):
        """Send bitcoins to another bitcoin wallet specified by address
        """
        params = self.get_params()
        params['amount'] = amount
        params['address'] = address

        r = requests.post(
            "https://www.bitstamp.net/api/bitcoin_withdrawal/",
            data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.text == u'true':
                return True
            else:
                data = get_json_data(r)
                if 'error' in data:
                    return False, data['error']
                return False, data
        else:
            r.raise_for_status()

    def bitcoin_deposit_address(self):
        """Returns bitcoin deposit address as unicode string
        """
        params = self.get_params()
        r = requests.post(
            "https://www.bitstamp.net/api/bitcoin_deposit_address/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def unconfirmed_bitcoin_deposits(self):
        """Returns JSON list of unconfirmed bitcoin transactions
        
        Each transaction is represented as dictionary:
        amount - bitcoin amount
        address - deposit address used
        confirmations - number of confirmations
        """
        params = self.get_params()
        r = requests.post(
            "https://www.bitstamp.net/api/unconfirmed_btc/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data

    def ripple_withdrawal(self, amount, address, currency):
        """Withdraw Ripple

        Returns true if successful
        """
        params = self.get_params()
        params['amount'] = amount
        params['address'] = address
        params['currency'] = currency

        r = requests.post(
            "https://www.bitstamp.net/api/ripple_withdrawal/",
            data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.text == u'true':
                return True
            else:
                data = get_json_data(r)
                if 'error' in data:
                    return False, data['error']
                return data
        else:
            r.raise_for_status()

    def ripple_deposit_address(self):
        """Returns ripple deposit address as unicode string
        """
        params = self.get_params()
        r = requests.post(
            "https://www.bitstamp.net/api/ripple_address/",
            data=params, proxies=self.proxydict)
        data = get_json_data(r)
        if 'error' in data:
            return False, data['error']
        return data
