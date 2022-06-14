import pandas as pd

class TestTrade:
    def __init__(self, data, b_date, s_date):
        self.buy_date = b_date
        self.sell_date = s_date
        self.set_buy_price(data)
        self.set_sell_price(data)
        self.set_profit()
        
    def get_buy_date(self):
        return self.buy_date
    
    def get_sell_price(self):
        self.sell_date
        
    def get_buy_price(self):
        return self.buy_price

    def get_sell_price(self):
        return self.sell_price
        
    def get_profit(self):
        return self.profit
        
    def set_buy_price(self, data):
        self.buy_price = data['Close'].loc[self.buy_date]

    def set_sell_price(self, data):
        self.sell_price = data['Close'].loc[self.sell_date]
        
    def set_profit(self):
        self.profit = 100 * (self.sell_price - self.buy_price) / self.buy_price
    
    def __str__(self):
        return f'buy: {self.buy_date} | {self.buy_price}\nsell: {self.sell_date} | {self.sell_price}\nprofit = {self.get_profit()}'
    
    def get_next_sell(signals, index):
        for i in range(index, len(signals)):
            if pd.isna(signals['Sell Signal'].iloc[i]) == False:
                return i      
        return -1
    
