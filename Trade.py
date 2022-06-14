

from enum import Enum



class OrderType(Enum):
    MarketOrder = 'Market'
    StopOrder = 'Stop'
    LimitOrder = 'Limit'
    StopLimitOrder = 'Stop Limit'

class Order:
    def __init__(self, side, symbol, qty, type):
        self.side = side
        self.symbol = symbol
        self.quantity = qty
        self.type = type

    def setMessage(self, msg):
        self.message = msg




class MarketOrder(Order):
    def __init__(self, side, symbol, qty):
        Order.__init__(self, side, symbol, qty, OrderType.MarketOrder)

    def setPrice(self, price):
        self.price = price

class StopOrder(Order):
    def __init__(self, side, symbol, qty, stopPrice):
        Order.__init__(self, side, symbol, qty, OrderType.StopOrder)
        self.stopPrice = stopPrice



class LimitOrder(Order):
    def __init__(self, side, symbol, qty, limitPrice):
        Order.__init__(self, side, symbol, qty, OrderType.LimitOrder)
        self.limitPrice = limitPrice



class StopLimitOrder(Order):
    def __init__(self, side, symbol, qty, limitPrice, stopPrice):
        Order.__init__(self, side, symbol, qty, OrderType.StopLimitOrder)
        self.stopPrice = stopPrice
        self.limitPrice = limitPrice


class Trade():
    def __init__(self, symbol, qty, stopLossPercentage):
        self.symbol = symbol
        self.quantity = qty
        self.lossPercentage = stopLossPercentage
        self.setBuyOrder()
        self.setSellOrder()
        self.isActive = False

    def setBuyOrder(self):
        self.buyOrder = MarketOrder('buy', self.symbol, self.quantity)
        

    def setStopLossOrder(self):
        price = self.buyOrder.price
        stopPrice = round(price * (1 - self.lossPercentage))
        limitPrice = round(price * (1 - 2 * self.lossPercentage))
        print(f'stop price = {stopPrice}')
        print(f'limit price = {limitPrice}')
        self.stopLossOrder = StopLimitOrder('sell', self.symbol, self.quantity, limitPrice, stopPrice)

    def setSellOrder(self):
        self.sellOrder = MarketOrder('sell', self.symbol, self.quantity)
