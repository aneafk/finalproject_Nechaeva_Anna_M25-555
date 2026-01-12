# valutatrade_hub/parser_service/api_clients.py
import time
from typing import Dict, Optional

import requests


class ApiRequestError(Exception):
    pass


# Основной класс для API клиентов
class BaseApiClient:
    '''
    config - текущий конфиг.
    Базовый класс для API клиентов
    '''
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CurrencyParser/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_rates(self) -> Dict[str, float]:
        '''
        Получение курсов валют - должен быть реализован в подклассах
        '''
        raise NotImplementedError
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        '''
        Выполнение HTTP запроса с повторными попытками
        '''
        last_error = None
        
        for attempt in range(self.config.REQUEST_RETRIES):
            try:
                self.config.validate()
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.config.REQUEST_TIMEOUT
                )
                
                if response.status_code != 200:
                    raise ApiRequestError(f'HTTP {response.status_code}: {response.text}')
                
                data = response.json()
                return data
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt == self.config.REQUEST_RETRIES - 1:
                    raise ApiRequestError(f'Не удалось выполнить запрос после {self.config.REQUEST_RETRIES} попыток: {last_error}')
                
                time.sleep(self.config.RETRY_DELAY * (attempt + 1))
        
        raise ApiRequestError(f'Ошибка: Все попытки завершились ошибкой: {last_error}')


# Класс для работы с CoinGecko API 
class CoinGeckoClient(BaseApiClient):
    '''
    Клиент для работы с CoinGecko API (без ключа)
    '''
    
    def fetch_rates(self) -> Dict[str, float]:
        '''
        Получение курсов криптовалют
        '''
        try:
            params = self.config.get_coingecko_params()
            data = self._make_request(self.config.COINGECKO_URL, params)
            
            rates = {}
            for crypto_code, gecko_id in self.config.CRYPTO_ID_MAP.items():
                if gecko_id in data and self.config.BASE_CURRENCY.lower() in data[gecko_id]:
                    pair_key = f"{crypto_code}_{self.config.BASE_CURRENCY}"
                    rates[pair_key] = data[gecko_id][self.config.BASE_CURRENCY.lower()]
            
            print(f'CoinGecko: получено {len(rates)} крипто-курсов')
            return rates
            
        except Exception as e:
            print(f'CoinGecko error: {e}')
            raise ApiRequestError(f'Ошибка: Ошибка получения данных от CoinGecko: {e}')


# Класс для работы с xchangeRate API 
class ExchangeRateApiClient(BaseApiClient):
    '''
    Клиент для работы с ExchangeRate-API (требует ключ)
    '''
    
    def fetch_rates(self) -> Dict[str, float]:
        '''
        Получение курсов фиатных валют
        '''
        try:
            url = self.config.get_exchangerate_url()
            data = self._make_request(url)
            
            if data.get('result') != 'success':
                error_type = data.get('error-type', 'unknown_error')
                raise ApiRequestError(f'Ошибка: ExchangeRate-API error: {error_type}')
            
            rates = {}
            conversion_rates = data.get('conversion_rates', {})
            
            for currency in self.config.FIAT_CURRENCIES:
                if currency in conversion_rates:
                    pair_key = f'{currency}_{self.config.BASE_CURRENCY}'
                    rates[pair_key] = conversion_rates[currency]
            
            print(f'ExchangeRate-API: получено {len(rates)} фиатных курсов')
            return rates
            
        except ApiRequestError:
            raise 
        except Exception as e:
            print(f'Ошибка: ExchangeRate-API error: {e}')
            return {}
            
            
