import alpaca_trade_api as tradeApi
from Errors import *
from SMA_System import *
from Strategy import *
from TestTrade import *
from Trade import Trade, OrderType
from config import *

class Trader:
    def __init__(self, API_KEY, SECRET_KEY, baseUrl, exchange='CBSE'):
        self.api = tradeApi.REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url=baseUrl)
        self.account = self.api.get_account()
        self.exchange = exchange
        self.trades = []
    
    
    def addTrade(self, symbol, value=10, stopLoss=0.05):
        trade = Trade(
            symbol=symbol,
            qty=self.getQuantity(symbol, value),
            stopLossPercentage=stopLoss
        )
        self.fullfilOrder(trade.buyOrder)
        trade.setStopLossOrder()
        self.fullfilOrder(trade.stopLossOrder)
        trade.isActive = True
        self.trades.append(trade)

    def exitTrade(self, trade):
        self.api.cancel_order(trade.stopLossOrder.message.id)
        self.fullfilOrder(trade.sellOrder)
        trade.isActive = False
    
    def getQuantity(self, symbol, value):
        return round(value / self.getPrice(symbol), 4)
    
    def getPrice(self, symbol):
        return self.api.get_crypto_snapshot(symbol=symbol, exchange=self.exchange).latest_quote.ap

    def fullfilOrder(self, order):
        if order.type == OrderType.MarketOrder:
            msg = self.fullfilMarketOrder(order)
            order.setMessage(msg)
            price = self.findOrderPrice(order)
            order.setPrice(price)

        elif order.type == OrderType.StopLimitOrder:
            msg = self.fullfilStopLimitOrder(order)
            order.setMessage(msg)

        elif order.type == OrderType.StopOrder:
            msg = self.fullfilStoptOrder(order)

        elif order.type == OrderType.LimitOrder:
            msg = self.fullfilLimitOrder(order)
        


    def findOrderPrice(self, order):
        for activity in self.api.get_activities():
            if activity.order_id == order.message.id:
                return float(activity.price)
    
    
    def fullfilMarketOrder(self, order):
        order_msg = self.api.submit_order(
            symbol=order.symbol,
            qty=order.quantity,
            side=order.side,
            type='market',
            time_in_force='gtc'
        )
        return order_msg

    def fullfilStopLimitOrder(self, order):
        order_msg = self.api.submit_order(
            symbol=order.symbol,
            qty=order.quantity,
            side=order.side,
            type='stop_limit',
            time_in_force='gtc',
            limit_price=order.limitPrice,
            stop_price=order.stopPrice
        )
        return order_msg

    def fullfilStopOrder(self, order):
        order_msg = self.api.submit_order(
            symbol=order.symbol,
            qty=order.quantity,
            side=order.side,
            type='stop',
            time_in_force='gtc',
            stop_price=order.stopPrice
        )
        return order_msg


    def fullfilLimitOrder(self, order):
        order_msg = self.api.submit_order(
            symbol=order.symbol,
            qty=order.quantity,
            side=order.side,
            type='limit',
            time_in_force='gtc',
            limit_price=order.stopPrice
        )
        return order_msg
        
