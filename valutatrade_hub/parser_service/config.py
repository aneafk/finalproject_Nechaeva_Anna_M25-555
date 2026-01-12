# valutatrade_hub/parser_service/config.py
import os
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class ParserConfig:
    '''
    Конфигурация для сервиса парсинга
    '''
    
    EXCHANGERATE_API_KEY: str = os.getenv('EXCHANGERATE_API_KEY') 
 
 
    COINGECKO_URL: str = 'https://api.coingecko.com/api/v3/simple/price'  # Без ключа
    EXCHANGERATE_API_URL: str = 'https://v6.exchangerate-api.com/v6'  # Требует ключ
    
    
    BASE_CURRENCY: str = 'USD'
    
    
    FIAT_CURRENCIES: Tuple[str, ...] = ('EUR', 'GBP', 'RUB', 'JPY', 'CNY')
    CRYPTO_CURRENCIES: Tuple[str, ...] = ('BTC', 'ETH', 'SOL', 'ADA', 'DOT')
    
    
    CRYPTO_ID_MAP: Dict[str, str] = None
    
    
    REQUEST_TIMEOUT: int = 30
    REQUEST_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    
    
    RATES_FILE_PATH: str = 'data/rates.json'
    HISTORY_FILE_PATH: str = 'data/exchange_rates.json'
    
    
    UPDATE_INTERVAL_MINUTES: int = 5
    RATES_TTL_SECONDS: int = 300
    
    def __post_init__(self):
        '''
        Инициализация после создания объекта
        '''
        if self.CRYPTO_ID_MAP is None:
            self.CRYPTO_ID_MAP = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum', 
                'SOL': 'solana',
                'ADA': 'cardano',
                'DOT': 'polkadot'
            }
        
        
        os.makedirs(os.path.dirname(self.RATES_FILE_PATH), exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'ParserConfig':
        '''
        Создание конфигурации из переменных окружения
        '''
        return cls(
            EXCHANGERATE_API_KEY=os.getenv('EXCHANGERATE_API_KEY'), ##9e67590197666010904d1334
            REQUEST_TIMEOUT=int(os.getenv('PARSER_REQUEST_TIMEOUT', '30')),
            UPDATE_INTERVAL_MINUTES=int(os.getenv('PARSER_UPDATE_INTERVAL', '5')),
            RATES_TTL_SECONDS=int(os.getenv('RATES_TTL_SECONDS', '300'))
        )
    
    def validate(self) -> bool:
        '''
        Валидация конфигурации
        '''
        if not self.EXCHANGERATE_API_KEY or self.EXCHANGERATE_API_KEY == 'demo_key':
            print('   ВНИМАНИЕ: Используется демо-ключ ExchangeRate-API!')
            print('   Для работы с фиатными валютами зарегистрируйтесь на:')
            print('   https://app.exchangerate-api.com/sign-up')
            print('   и установите переменную окружения EXCHANGERATE_API_KEY')
        
        
        if not all(currency.isalpha() and currency.isupper() 
                  for currency in self.FIAT_CURRENCIES + self.CRYPTO_CURRENCIES):
            raise ValueError('Ошибка: Коды валют должны быть в верхнем регистре и содержать только буквы')
        
        
        data_dir = os.path.dirname(self.RATES_FILE_PATH)
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
                print(f'Создана директория: {data_dir}')
            except OSError as e:
                raise ValueError(f'Ошибка: Не удалось создать директорию {data_dir}: {e}')
        
        return True
    
    def get_coingecko_params(self) -> Dict[str, str]:
        '''
        Получение параметров для запроса к CoinGecko (без ключа)
        '''
        crypto_ids = ','.join(
            self.CRYPTO_ID_MAP[currency] 
            for currency in self.CRYPTO_CURRENCIES 
            if currency in self.CRYPTO_ID_MAP
        )
        
        return {
            'ids': crypto_ids,
            'vs_currencies': self.BASE_CURRENCY.lower()
        }
    
    def get_exchangerate_url(self) -> str:
        '''
        Получение URL для запроса к ExchangeRate-API (требует ключ)
        '''
        return f'{self.EXCHANGERATE_API_URL}/{self.EXCHANGERATE_API_KEY}/latest/{self.BASE_CURRENCY}'
