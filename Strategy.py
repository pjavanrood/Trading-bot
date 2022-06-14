import pandas as pd
import datetime as dt

import time
import json
import threading
from functools import partial

import websocket
import alpaca_trade_api as tradeApi

from Errors import *
from SMA_System import *
from TestTrade import *
from Trade import *
from Trader import *
from config import *

class DataReceiver():
    def __init__(self, socketUrl, baseUrl, storage, exchange='CBSE'):
        self.setKEYS(API_KEY, SECRET_KEY, socketUrl, baseUrl)
        self.exchange = exchange
        self.subscriptions = []
        self.storage = storage
        self.log = {}
        
        
    @staticmethod
    def on_open(ws, dReceiver):
        print('connected')
        #Authenticate
        msg = {"action": "auth", "key": dReceiver.API_KEY, "secret": dReceiver.SECRET_KEY}
        ws.send(json.dumps(msg))
        #Subscribe
        msg = {'action': 'subscribe', 'bars': dReceiver.subscriptions}
        ws.send(json.dumps(msg))
        
    
    @staticmethod
    def on_message(ws, msg, dReceiver):
        print('message received!')
        #print(msg)
        msg_dict = json.loads(msg)[0]
        if DataReceiver.checkData(msg_dict) == True:
            dReceiver.saveData(msg_dict)
            
        else:
            dReceiver.saveLog(msg_dict)
            
    @staticmethod
    def on_close(ws):
        print('connection closed!')
        
    @staticmethod
    def checkData(msg):
        if msg['T'] == 'b':
            return True
        
        return False
    
    
    
    def setKEYS(self, API_KEY, SECRET_KEY, socketUrl, baseUrl):
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.socketUrl = socketUrl
        self.baseUrl = baseUrl
    
    def addSubscription(self, pairs: list):
        self.subscriptions.extend(pairs)
    
    def runWS(self):
        self.ws = websocket.WebSocketApp(self.socketUrl,
                                         on_open=partial(DataReceiver.on_open, dReceiver=self),
                                         on_message=partial(DataReceiver.on_message, dReceiver=self),
                                         on_close=DataReceiver.on_close)
        self.ws.run_forever()
        
    
    def saveData(self, msg):
        print('saved!!!!!')
        strTime = msg['t']
        strOpen = msg['o']
        strHigh = msg['h']
        strClose = msg['c']
        strLow = msg['l']
        strVol = msg['v']
        strCount = msg['n']
        strVwap = msg['vw']
        #symbol = msg['S']
        exchange = msg['x']
        if self.exchange == exchange:
            newData = {
                'Time': [pd.to_datetime(strTime.replace('T', ' ').replace('Z', ''), utc=True)],
                #'Exchange': exchange,
                #'Symbol': [symbol], 
                'Open': [float(strOpen)],
                'High': [float(strHigh)],
                'Close': [float(strClose)],
                'Low': [float(strLow)],
                'Volume': [float(strVol)],
                'Trade Count': [float(strCount)],
                'Vwap': [float(strVwap)]
                        }
            newData = pd.DataFrame(newData)
            newData.set_index('Time', inplace=True)
            self.storage['data'] = newData
            self.storage['notification'] = True
        return
    
    
    def getRecentData(self):
        return self.recentData

         
    def saveLog(self, msg):
        t = pd.to_datetime(time.time(), unit='ms', origin='unix')
        self.log[t] = msg
        return
    
    def getHistoricData(self, symbol, lookback):
        api = tradeApi.REST(
        key_id=API_KEY,
        secret_key=SECRET_KEY,
        base_url=self.baseUrl)
        start_time = ( dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=lookback) ).strftime('%Y-%m-%dT%H:%M:%SZ')
        data = api.get_crypto_bars(symbol, timeframe='1Min', start=start_time).df
        data.reset_index(inplace=True)
        data.columns = ['Time', 'Exchange', 'Open', 'High', 'Close', 'Low', 'Volume', 'Trade Count', 'Vwap']
        data['Time'] = pd.to_datetime(data['Time'])
        data = data.loc[data['Exchange'] == self.exchange]
        del data['Exchange']
        return data

   

class BackTester():
    def __init__(self, symbol, dataReceiver, exchange):
        self.symbol = symbol
        self.exchange = exchange
        self.dataReceiver = dataReceiver
        
    def backTest(self, t_lookback=24):
        histData = self.dataReceiver.getHistoricData(symbol=self.symbol, lookback=t_lookback)
        histData.set_index('Time', inplace=True)
        f_window, s_window, profit = SMA_System.get_best_pair(histData, accuracy=5)
        return (f_window, s_window)


class TradingBot():
    def __init__(self, symbol, exchange='CBSE', lookback=12):
        self.setupGeneral(symbol, lookback, exchange)
        self.setupDataReceiver()
        self.setData()
        self.setupBackTest()
        self.trader = Trader(API_KEY, SECRET_KEY, base_url)
        
    
    def setupGeneral(self, symbol, lookback, exchange):
        self.symbol = symbol
        self.lookback = lookback
        self.exchange = exchange
        self.start = False
    
    def setupDataReceiver(self):
        self.receiverStorage = {'data': pd.DataFrame(), 'notification': False}
        self.dataReceiver = DataReceiver(socket_url, base_url, self.receiverStorage, exchange=self.exchange)
        self.dataReceiver.addSubscription([self.symbol])
        
        
    def setupBackTest(self):
        self.backTester = BackTester(self.symbol, self.dataReceiver, self.exchange)
        self.windows = self.backTester.backTest(self.lookback)
        SMA_System.add_ma_data(self.data, self.windows[0], self.windows[1])
    
    
    def setData(self):
        df = self.dataReceiver.getHistoricData(self.symbol, self.lookback)
        df['Analyzed'] = True
        df.set_index('Time', inplace=True)
        self.data = df
        

        
    def saveNewData(self):
        newData = self.receiverStorage['data'].copy()
        newData['Analyzed'] = False
        df = pd.concat([self.data, newData], axis=0)
        self.data = df
        self.receiverStorage['notification'] = False
        
        
    def analyze(self):
        df = self.data
        newData = df.loc[df['Analyzed'] == False]
        addedDates = list(newData.index)
        for i in addedDates:
            self.data.at[i, self.windows[0]] = SMA_System.calculate_mav(df, i, self.windows[0])
            self.data.at[i, self.windows[1]] = SMA_System.calculate_mav(df, i, self.windows[1])
            self.data.at[i, 'Analyzed'] = True
            SMA_System.add_signals(self.data, i, self.windows[0], self.windows[1])

    
    def checkTrade(self):
        lastBuySignal = self.data.iloc[-1]['Buy Signal']
        lastSellSignal = self.data.iloc[-1]['Sell Signal']
        if pd.isna(lastBuySignal) == False:
            self.trader.addTrade(self.symbol)

        if pd.isna(lastSellSignal) == False:
            for trade in self.trader.trades:
                if trade.isActive == True:
                    self.trader.exitTrade(trade)


    def mainThreadFunction(self):
        while self.start == True:            
            if self.receiverStorage['notification'] == True:
                self.saveNewData()
                self.analyze()    
                self.checkTrade()     
            
        

    


    def run(self):
        self.start = True
        thread = threading.Thread(target=self.dataReceiver.runWS)
        thread.start()

        mainThread = threading.Thread(target=self.mainThreadFunction)
        mainThread.start()


    def stop(self):
        self.stop = True
        self.dataReceiver.ws.close()