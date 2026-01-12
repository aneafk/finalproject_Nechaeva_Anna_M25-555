# valutatrade_hub/core/utils.py
from .currencies import get_currency
from .exceptions import CurrencyNotFoundError


def validate_currency_code(currency_code: str) -> bool:
    '''
    Валидация кода валюты
    '''
    try:
        get_currency(currency_code.upper())
        return True
    except CurrencyNotFoundError:
        return False

def format_currency_amount(amount: float, currency_code: str) -> str:
    '''
    Форматирование суммы валюты
    '''
    if currency_code in ['BTC', 'ETH']:
        return f'{amount:.8f} {currency_code}'
    else:
        return f'{amount:,.2f} {currency_code}'

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    '''
    Расчет процентного изменения
    '''
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100
    
    
