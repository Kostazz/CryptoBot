File: main.py

from flask import Flask, jsonify from bot_logic import check_trade_signal

app = Flask(name)

@app.route('/') def home(): return "KryptoKamos Scalping Bot v1.0 is running."

@app.route('/run', methods=['GET']) def run_bot(): # Spustí kontrolu signálu a vrátí výsledek result = check_trade_signal() return jsonify(result)

if name == 'main': # Na Replitu běží na portu definovaném proměnnou PORT import os port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port)

File: config.py

import os

Bitget API

API_KEY = os.environ.get('BITGET_API_KEY') API_SECRET = os.environ.get('BITGET_API_SECRET')

Strategické parametry

SYMBOL = os.environ.get('SYMBOL', 'BTCUSDT_UMCBL')  # futures pair LEVERAGE = int(os.environ.get('LEVERAGE', 50)) EMA_SHORT = int(os.environ.get('EMA_SHORT', 9)) EMA_LONG = int(os.environ.get('EMA_LONG', 21)) VOLUME_MULTIPLIER = float(os.environ.get('VOLUME_MULTIPLIER', 1.5)) STOP_LOSS_PCT = float(os.environ.get('STOP_LOSS_PCT', 0.002))  # 0.2% TAKE_PROFIT_PCT = float(os.environ.get('TAKE_PROFIT_PCT', 0.004))  # 0.4% MAX_TRADES_PER_DAY = int(os.environ.get('MAX_TRADES_PER_DAY', 5))

File: trade_engine.py

import requests import time from config import API_KEY, API_SECRET, SYMBOL, LEVERAGE

class BitgetClient: BASE_URL = 'https://api.bitget.com'

def __init__(self, api_key, api_secret):
    self.api_key = api_key
    self.api_secret = api_secret
    # TODO: implement authentication signing

def set_leverage(self, symbol, leverage):
    path = '/mix/v1/account/setLeverage'
    params = {
        'symbol': symbol,
        'leverage': leverage,
        'marginMode': 'cross'
    }
    # send signed request
    return {}

def place_order(self, symbol, side, size, price=None, order_type='market'):
    path = '/mix/v1/order/placeOrder'
    params = {
        'symbol': symbol,
        'side': side,
        'size': size,
        'orderType': order_type
    }
    if price:
        params['price'] = price
    # send signed request
    return {}

def get_klines(self, symbol, interval, limit=50):
    url = f'{self.BASE_URL}/api/mix/v1/market/history-candles'
    params = {'symbol': symbol, 'period': interval, 'size': limit}
    resp = requests.get(url, params=params)
    data = resp.json()
    # transform to list of [timestamp, open, high, low, close, volume]
    return data.get('data', [])

File: bot_logic.py

import pandas as pd from config import SYMBOL, EMA_SHORT, EMA_LONG, VOLUME_MULTIPLIER, STOP_LOSS_PCT, TAKE_PROFIT_PCT from trade_engine import BitgetClient

Initialize client

client = BitgetClient(api_key=None, api_secret=None)  # načteme později z .env def check_trade_signal(): # Získání posledních svíček klines = client.get_klines(SYMBOL, '1m', limit=EMA_LONG+5) df = pd.DataFrame(klines, columns=['ts','open','high','low','close','volume']) df['close'] = df['close'].astype(float) df['volume'] = df['volume'].astype(float) # Vypočítáme EMA df['ema_short'] = df['close'].ewm(span=EMA_SHORT, adjust=False).mean() df['ema_long'] = df['close'].ewm(span=EMA_LONG, adjust=False).mean() # Detekce crossover crossover = df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1] prev_crossover = df['ema_short'].iloc[-2] <= df['ema_long'].iloc[-2] # Objemy avg_vol = df['volume'].rolling(5).mean().iloc[-1] vol_spike = df['volume'].iloc[-1] > VOLUME_MULTIPLIER * avg_vol # Signál BUY nebo SELL if crossover and prev_crossover and vol_spike: return { 'action': 'BUY', 'price': df['close'].iloc[-1] } elif not crossover and df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1] and df['ema_short'].iloc[-2] >= df['ema_long'].iloc[-2] and vol_spike: return { 'action': 'SELL', 'price': df['close'].iloc[-1] } else: return { 'action': 'WAIT' }

File: alerts.py

import os import requests

def send_discord_alert(message): webhook = os.environ.get('DISCORD_WEBHOOK_URL') if not webhook: return False data = { 'content': message } resp = requests.post(webhook, json=data) return resp.status_code == 204 or resp.status_code == 200

File: requirements.txt

flask requests pandas python-dotenv

File: .env.example

BITGET_API_KEY=your_api_key_here BITGET_API_SECRET=your_api_secret_here DISCORD_WEBHOOK_URL=your_webhook_url_here SYMBOL=BTCUSDT_UMCBL LEVERAGE=50 EMA_SHORT=9 EMA_LONG=21 VOLUME_MULTIPLIER=1.5 STOP_LOSS_PCT=0.002 TAKE_PROFIT_PCT=0.004 MAX_TRADES_PER_DAY=5

