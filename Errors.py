from enum import Enum

class Error(Enum):
    SymbolNotFound = ValueError('Symbol not found in positions')
    NotEnoughPosition = ValueError('Sell quantity exceeds the available quantity')