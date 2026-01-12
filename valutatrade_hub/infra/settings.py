# valutatrade_hub/infra/settings.py
import os
from typing import Any, Dict


class SettingsLoader:
    '''
    Singleton для загрузки и управления настройками приложения
    '''
    _instance = None
    _settings: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        '''
        Загрузка настроек из различных источников
        '''
        default_settings = {
            'data_directory': 'data',
            'rates_ttl_seconds': 300,
            'default_base_currency': 'USD',
            'log_level': 'INFO',
            'log_file': 'logs/valutatrade.log',
            'supported_currencies': ['USD', 'EUR', 'GBP', 'RUB', 'BTC', 'ETH', 'SOL'],
            'api_timeout': 10
        }
        
        self._settings.update(default_settings)
        
        try:
            if os.path.exists('pyproject.toml'):
                pass
        except Exception:
            pass
        
        env_mapping = {
            'VALUTATRADE_DATA_DIR': 'data_directory',
            'VALUTATRADE_RATES_TTL': 'rates_ttl_seconds',
            'VALUTATRADE_LOG_LEVEL': 'log_level',
        }
        
        for env_var, setting_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                if setting_key == 'rates_ttl_seconds':
                    self._settings[setting_key] = int(value)
                else:
                    self._settings[setting_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        '''
        Получение значения настройки
        '''
        return self._settings.get(key, default)
    
    def reload(self):
        '''
        Перезагрузка настроек
        '''
        self._settings.clear()
        self._load_settings()
    
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        self._settings[key] = value


settings = SettingsLoader()
