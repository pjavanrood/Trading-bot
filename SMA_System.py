import pandas as pd
import numpy as np
import mplfinance as mpf
from TestTrade import *

class SMA_System:
    def __init__(self, data_, fast_window_, slow_window_):
        self.data = data_
        self.fast_window = fast_window_
        self.slow_window = slow_window_
        self.set_ma_data()
        self.set_signals()
        self.set_trades()
        self.set_avg_profit()
        self.set_total_profit()
        
    def get_data(self):
        return self.data
    
    def get_fast_window(self):
        return self.fast_window
    
    def get_slow_window(self):
        return self.slow_window
    
    def get_ma_data(self):
        return self.ma_data
    
    def get_signals(self):
        return self.signals
    
    def get_trades(self):
        return self.trades
    
    def get_avg_profit(self):
        return self.avg_profit
    
    def get_total_profit(self):
        return self.total_profit
        
    def set_ma_data(self):
        data = self.data
        fast_window = self.fast_window
        slow_window = self.slow_window
        ma_test = pd.DataFrame({
            fast_window: SMA_System.mav_pd(data['Close'], fast_window),
            slow_window: SMA_System.mav_pd(data['Close'], slow_window),
        })

        buy_signal = []
        sell_signal = []
        
        for index, date in enumerate(ma_test.index):
            if ma_test[fast_window].iloc[index] > ma_test[slow_window].iloc[index] and ma_test[fast_window].iloc[index - 1] <= ma_test[slow_window].iloc[index - 1]:
                buy_signal.append(ma_test[fast_window].iloc[index])
                sell_signal.append(np.nan)

            elif ma_test[slow_window].iloc[index] > ma_test[fast_window].iloc[index] and ma_test[slow_window].iloc[index - 1] <= ma_test[fast_window].iloc[index - 1]:
                buy_signal.append(np.nan)
                sell_signal.append(ma_test[fast_window].iloc[index])

            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)

        ma_test['Buy Signal'] = buy_signal
        ma_test['Sell Signal'] = sell_signal

        self.ma_data = ma_test
        
    def set_signals(self):
        self.signals = self.ma_data.loc[(pd.isna(self.ma_data['Buy Signal']) == False) | (pd.isna(self.ma_data['Sell Signal']) == False)]
 
    def set_trades(self):
        trades = []
        signals = self.signals
        data = self.data
        for index, b_date in enumerate(signals.index):
            if pd.isna(signals['Buy Signal'].iloc[index]) == False:
                sell_index = TestTrade.get_next_sell(signals, index)
                s_date = signals.index[sell_index]
                trades.append( TestTrade(data, b_date, s_date) )
        self.trades = trades
        
    def set_avg_profit(self):
        if len(self.trades) == 0:
            return 0
        self.avg_profit = sum(trade.get_profit() for trade in self.trades) / len(self.trades)
        
    def set_total_profit(self):
        self.total_profit = sum(trade.get_profit() for trade in self.trades) * 0.01

    def plot(self, year=None, period=(None, None)):
        ma_test = self.ma_data
        fast_window = self.fast_window
        slow_window = self.slow_window
        data = self.data
        start_date, end_date = period
        
        if year != None:
            add_ma = [mpf.make_addplot(ma_test[[fast_window, slow_window]].loc[f'{year}']), 
                      mpf.make_addplot(ma_test['Buy Signal'].loc[f'{year}'], type='scatter', marker='o', color='g'), 
                      mpf.make_addplot(ma_test['Sell Signal'].loc[f'{year}'], type='scatter', marker='o', color='r')]
            mpf.plot(data.loc[f'{year}'], type='candle', style='yahoo', addplot=add_ma)
            
        
        
        elif (start_date != None and end_date != None):
            add_ma = [mpf.make_addplot(ma_test[[fast_window, slow_window]].loc[start_date:end_date]), 
                      mpf.make_addplot(ma_test['Buy Signal'].loc[start_date:end_date], type='scatter', marker='o', color='g'), 
                      mpf.make_addplot(ma_test['Sell Signal'].loc[start_date:end_date], type='scatter', marker='o', color='r')]
            mpf.plot(data.loc[start_date:end_date], type='candle', style='yahoo', addplot=add_ma)
    
    
        else:
            add_ma = [mpf.make_addplot(ma_test[[fast_window, slow_window]].loc[start_date:end_date]), 
                      mpf.make_addplot(ma_test['Buy Signal'], type='scatter', marker='o', color='g'), 
                      mpf.make_addplot(ma_test['Sell Signal'], type='scatter', marker='o', color='r')]
            mpf.plot(data, type='candle', style='yahoo', addplot=add_ma)
    
    @staticmethod
    def calculate_mav(df, index, time):
        i = list(df.index).index(index)  
        close_col = list(df.columns).index('Close')

        first_index = i - time + 1
        if first_index < 0:
            mav_val = np.nan
            
        else:
            price_sum = sum(df.iloc[first_index:i+1, close_col])
            mav_val = price_sum / time
                    
        return mav_val
        
    @staticmethod
    def add_ma_data(data, fast_window, slow_window):
        data[fast_window] = SMA_System.mav_pd(data['Close'], fast_window)
        data[slow_window] = SMA_System.mav_pd(data['Close'], slow_window)
        
        buy_signal = []
        sell_signal = []
        

        for index, date in enumerate(data.index):
            if data[fast_window].iloc[index] > data[slow_window].iloc[index] and data[fast_window].iloc[index - 1] <= data[slow_window].iloc[index - 1]:
                buy_signal.append(data[fast_window].iloc[index])
                sell_signal.append(np.nan)

            elif data[slow_window].iloc[index] > data[fast_window].iloc[index] and data[slow_window].iloc[index - 1] <= data[fast_window].iloc[index - 1]:
                buy_signal.append(np.nan)
                sell_signal.append(data[fast_window].iloc[index])

            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)

        data['Buy Signal'] = buy_signal
        data['Sell Signal'] = sell_signal

        return  
    
    @staticmethod
    def add_signals(data, index_, fast_window, slow_window):
        index = list(data.index).index(index_)
        
        if data[fast_window].iloc[index] > data[slow_window].iloc[index] and data[fast_window].iloc[index - 1] <= data[slow_window].iloc[index - 1]:
            data.at[index_, 'Buy Signal'] = data[fast_window].iloc[index]
            data.at[index_, 'Sell Signal'] = np.nan

        elif data[slow_window].iloc[index] > data[fast_window].iloc[index] and data[slow_window].iloc[index - 1] <= data[fast_window].iloc[index - 1]:
            data.at[index_, 'Buy Signal'] = np.nan
            data.at[index_, 'Sell Signal'] = data[fast_window].iloc[index]

        else:
            data.at[index_, 'Buy Signal'] = np.nan
            data.at[index_, 'Sell Signal'] = np.nan
            
    @staticmethod
    def mav_pd(data, window):
        return data.rolling(window).mean()
    
    @staticmethod
    def get_best_pair(data, min_window=5, max_window=100, accuracy=5):
        systems = {}
        for fast in range(min_window, max_window+1, accuracy):
            for slow in range(fast + accuracy, max_window+1, accuracy):
                system = SMA_System(data, fast, slow)
                systems[(fast, slow)] = system.get_total_profit()
        systems = dict(sorted(systems.items(), key=lambda item: item[1], reverse=True))
        top_fast, top_slow = list(systems.keys())[0]
        top_profit = systems[ list(systems.keys())[0] ]
        return (top_fast, top_slow, top_profit)