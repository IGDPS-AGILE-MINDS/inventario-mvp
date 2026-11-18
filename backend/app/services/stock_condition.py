from enum import Enum


class StockCondition(str, Enum):
    agotado = "agotado"
    stock_bajo = "stock_bajo"
    normal = "normal"


def get_stock_condition(quantity: int, min_stock: int) -> StockCondition:
    if quantity == 0:
        return StockCondition.agotado
    if quantity <= min_stock:
        return StockCondition.stock_bajo
    return StockCondition.normal
