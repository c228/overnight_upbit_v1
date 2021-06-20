import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
import datetime
import time

# current balance
access_key = ""
secret_key = ""
server_url = "https://api.upbit.com"

def current_balance():
    payload = {
        "access_key": access_key,
        "nonce": str(uuid.uuid4())
    }
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = "Bearer {}".format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    response = requests.get(server_url + "/v1/accounts", headers=headers)
    
    print(response.json())
    return response.json()

#---------------------------------------------------

# order (order information)
def crypto_info(market):
    query = {
        "market": market
    }
    query_string = urlencode(query).encode()
    
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    
    payload = {
        "access_key": access_key,
        "nonce": str(uuid.uuid4()),
        "query_hash": query_hash,
        "query_hash_alg": "SHA512"
    }
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = "Bearer {}".format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    response = requests.get(server_url + "/v1/orders/chance", params=query, headers=headers)
    
    print(response.json())
    
def order(market, side, volume, price, ord_type):
    query = {
        "market": "KRW-" + market,
        "side": side,
        "volume": volume,
        "price": price,
        "ord_type": ord_type        
    }
    query_string = urlencode(query).encode()
    
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        "access_key": access_key,
        "nonce": str(uuid.uuid4()),
        "query_hash": query_hash,
        "query_hash_alg": "SHA512"
    }
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = "Bearer {}".format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    response = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    print(response.json())
    
# current prices
def get_ticker(market):
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets":"KRW-" + market}
    response = requests.get(url, params=querystring)
    print(response.json())
    
# amount in KRW
def market_buy_order(market, amount):
    order(market, "bid", "", amount, "price")
    
def market_buy_order_full(market):
    amount = current_balance()[0]
    amount = int(float(amount['balance']) * 0.99)
    order(market, "bid", "", amount, "price")
    
def market_sell_order(market, amount):
    order(market, "ask", amount, "", "market")
    
def market_sell_order_full(market):
    amount = current_balance()[1]
    amount = amount['balance']
    order(market, "ask", amount, "", "market")

#quotation apis
def call_codes():
    querystring = {"isDetails": "true"}
    url = "https://api.upbit.com/v1/market/all"
    response = requests.get(url, params=querystring)
    print(response.text)

#hour candles
def hour_candles(market, to):
     url = "https://api.upbit.com/v1/candles/minutes/60"
     querystring = {"market": "KRW-" + market, "count":"200", "to": to}
     response = requests.get(url, params=querystring)
     return response.json()
     print(response.json()[0])
 
# day candles
def day_candles(market):
    url = "https://api.upbit.com/v1/candles/days"
    querystring = {
        "market": "KRW-" + market,
      #  "to": "2020-12-25",
        "count":"30"
        }
    response = requests.get(url, params=querystring)
    print(response.json()[0])
    
#------------------------------------------------------------
    
def get_midnight_prices(to):
    price_data = []
    for x in hour_candles("BTC", to):
        if x["candle_date_time_kst"].split("T")[1] == "00:00:00":
            price_data.append([x["candle_date_time_kst"], x["opening_price"]])
    return price_data

def eight_day_delta(today):
    d = datetime.timedelta(days = 8)
    a = today - d
    return a

def get_midnight_prices_32():
    today = datetime.datetime.today()
    price_data = get_midnight_prices("")
    for x in range(3):
        today = eight_day_delta(today)
        price_data += get_midnight_prices(str(today).split()[0] + " 05:00:00")
    return price_data

def get_midnight_prices_360():
    today = datetime.datetime.today()
    price_data = get_midnight_prices("")
    for x in range(44):
        today = eight_day_delta(today)
        price_data += get_midnight_prices(str(today).split()[0] + " 05:00:00")
        time.sleep(0.05)
    return price_data
            
def get_noon_prices(to):
    price_data = []
    for x in hour_candles("BTC", to):
        if x["candle_date_time_kst"].split("T")[1] == "12:00:00":
            price_data.append([x["candle_date_time_kst"], x["opening_price"]])
    return price_data

def get_noon_prices_32():
    today = datetime.datetime.today()
    price_data = get_noon_prices("")
    for x in range(3):
        today = eight_day_delta(today)
        price_data += get_noon_prices(str(today).split()[0] + " 05:00:00")
    return price_data

def get_noon_prices_360():
    today = datetime.datetime.today()
    price_data = get_noon_prices("")
    for x in range(44):
        today = eight_day_delta(today)
        price_data += get_noon_prices(str(today).split()[0] + " 05:00:00")
        time.sleep(0.05)
    return price_data
        
def mndelta(to):
    midnight_price_data = get_midnight_prices(to)
    noon_price_data = get_noon_prices(to)
    for x in range(len(midnight_price_data)):
        print(noon_price_data[x][1] - midnight_price_data[x][1])
        
def mndelta32():
    data = []
    midnight_price_data = get_midnight_prices_32()
    noon_price_data = get_noon_prices_32()
    for x in range(len(midnight_price_data)):
        data.append(noon_price_data[x][1] - midnight_price_data[x][1])
    return data
    
def mndelta360():
    data = []
    midnight_price_data = get_midnight_prices_360()
    noon_price_data = get_noon_prices_360()
    for x in range(len(midnight_price_data)):
        data.append(noon_price_data[x][1] - midnight_price_data[x][1])
    return data

#you may have to shift by 1 here the dates.
#def reverse_mndelta360():
    data = []
    midnight_price_data = get_midnight_prices_360()
    noon_price_data = get_noon_prices_360()
    for x in range(len(midnight_price_data)):
        data.append(midnight_price_data[x][1] - noon_price_data[x][1])
    return data

def find_profit_ratio(array):
    wins = []
    losses = []
    for x in array:
        if x > 0:
            wins.append(x)
        else:
            losses.append(x)
    w_total = 0
    l_total = 0
    for x in wins:
        w_total += x
    w_avg = w_total / len(wins)
    for x in losses:
        l_total += x
    l_avg = l_total / len(losses)
    return abs(w_avg / l_avg)
        
def win_ratio(array):
    pos = 0
    total = 0
    for x in array:
        if x > 0:
            pos+=1
            total+=1
        else:
            total+=1
    return pos/total

def recent_win_streak(array):
    streak = 0
    for x in array:
        if x > 0:
            streak += 1
        else:
            return streak
   
#print(win_ratio(mndelta360()))
#print(find_profit_ratio(mndelta360()))

#---------------------------------------------------------
#trading logic

now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1, hours=3, minutes=10)
nine = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1, hours=9)

while True:
    try:
        now = datetime.datetime.now()
        if nine < now < nine + datetime.delta(seconds=10):
            market_sell_order_full("BTC")
        
        if mid < now < mid + datetime.delta(seconds=10):
            if mndelta32()[0] > 0:
                market_buy_order_full("BTC")
    
    except:
        print("Error!")
    time.sleep(1)
    
    




