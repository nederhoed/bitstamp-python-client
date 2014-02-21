bitstamp-python-client
======================

Python package to communicate with bitstamp.net API.

Compatible with Python v2, v3.3 and higher.

RRN: be sure to check if the author updates the repo before October 30th due to changes in the API https://bitcointalk.org/index.php?topic=38711.msg3218202#msg3218202

## Overview ##

There are two classes. One for public part of API and second for trading part.
Public class doesn't need user credentials, because API commands which this class implements are not bound to bitstamp user account.

Description of API:
https://www.bitstamp.net/api/

### Package requirements ###

* requests (pip install requests)

### Install from Git ###

    sudo pip install git+git://github.com/kmadac/bitstamp-python-client.git

### Activate new API ###

1. Login your bitstamp Account.
2. Click on Security -> Api Access.
3. Select permissions which you want to have for you access key (If you don't check any box, you will get error message 'No permission found' after each API call)
4. Click 'Generate key' button and don't forget to write down your Secret!
5. Click Activate
6. Goto your Inbox and click on link sent by Bitstamp service
7. Your account is activated Now and you can use API

### Usage example ###

```python
import bitstamp.client
bs_client_public = bitstamp.client.public()
ticker = bs_client_public.ticker()

bs_client_trading = bitstamp.client.trading(username='999999', key='xxx', secret='xxx')
account_balance = bs_client_trading.account_balance()

# Dictionary result
{ u'btc_reserved': u'0',
  u'fee': u'0.5000',
  u'btc_available': u'2.30856098',
  u'usd_reserved': u'0',
  u'btc_balance': u'2.30856098',
  u'usd_balance': u'114.64',
  u'usd_available': u'114.64'
}
```

### If this code is usable for you, here is my wallet id where you can contribute to my work with few micro BCs: ###

## 159bihAxJTKNsJSvCxYgAHKd8UX7kJugUQ ##

### NOTE: THIS IS A FORK ###

This fork is maintained by Bitmymoney to avoid unpleasant surprise updates,
if you want to use this code we advise to use the original product instead!


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/kmadac/bitstamp-python-client/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

