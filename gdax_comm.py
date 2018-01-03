import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from decimal import Decimal

api_url = 'https://api.gdax.com/'
gauth = 'x'

###########################################
# Create custom authentication for Exchange
###########################################
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        print(time.time())
        print(request.method)
        print(request.path_url)
        print(request.body)

        message = timestamp + request.method + request.path_url + (request.body or '')

        print ("----" + message)

        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        print(signature_b64)

        print("asdfasdf" + message)

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

###
### OPS no manipulation
###

#####################
# get account info
#####################
def getAccount(auth):
    r = requests.get(api_url + 'accounts', auth=auth)
    global gauth
    gauth = auth
    return r

#####################
# list all orders
#####################
def listOrders(status, product_id):
    r = requests.get(api_url + 'orders?' + 'status=' + status + '&product_id=' + product_id, auth=gauth)
    print(r.json())
    return r

#####################
# get latest quote
#####################
def bidsAsksDiff(product_id):
    r = requests.get(api_url + 'products/' + product_id + '/book?level=2', auth=gauth)
    
    bidsSize = 0
    asksSize = 0

    # [price, size, orders]
    for xxx in r.json()['bids']:        
        bidsSize += Decimal(xxx[0]) * Decimal(xxx[1])

    for xxx in r.json()['asks']:
        asksSize += Decimal(xxx[0]) * Decimal(xxx[1])

    print("bidSize: " + str(bidsSize))
    print("askSize: " + str(asksSize))

##############################
# latest matched trading price
##############################
def getLatestPrice(product_id):
    r = requests.get(api_url + 'products/' + product_id + '/ticker')
    return r

###
### OPS including manipulation ###########################################################################
###

#####################
# EMERGENCY: cancel all orders
#####################
def cancelAllOrders(product_id):
    r = requests.delete(api_url + 'orders?' + 'product_id=' + product_id, auth=gauth)
    print(r.json())
    return r

#####################
# place a limit order
# time_in_force: {GTC, GTT, IOC, FOK}
#####################
def placeLimit(type, size, price, side, time_in_force, post_only, product_id):
    # Place an order
    order = {
        'size': size,
        'price': price,
        'side': side,
        'time_in_force': time_in_force,
        'post_only': post_only,
        'product_id': product_id,
    }
    r = requests.post(api_url + 'orders', json=order, auth=gauth)
    print r.json()
    return r