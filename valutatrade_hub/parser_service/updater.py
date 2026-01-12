# valutatrade_hub/parser_service/updater.py
from datetime import datetime
from typing import Any, Dict


class ApiRequestError(Exception):
    pass

class ParserStorage:
    '''
    Упрощенное хранилище для тестирования
    '''
    
    def save_exchange_rate(self, rate_data):
        print(f'Saving rate: {rate_data['from_currency']}_{rate_data['to_currency']} = {rate_data['rate']}')
    
    def save_current_rates(self, rates, source):
        print(f'Saving {len(rates)} current rates from {source}')

class RatesUpdater:
    '''
    Основной класс для обновления курсов валют
    '''
    
    def __init__(self, config=None):
        from .api_clients import CoinGeckoClient, ExchangeRateApiClient
        from .config import ParserConfig
        
        self.config = config or ParserConfig.from_env()
        self.config.validate()
        
        self.logger = self._create_simple_logger()
        self.storage = ParserStorage()
        
        self.clients = {
            'coingecko': CoinGeckoClient(self.config),
            'exchangerate': ExchangeRateApiClient(self.config)
        }
    
    def _create_simple_logger(self):
        '''
        Создание простого логгера
        '''
        class SimpleLogger:
            def info(self, msg): print(f'Info: {msg}')
            def warning(self, msg): print(f'Warning: {msg}')
            def error(self, msg): print(f'Error: {msg}')
            def debug(self, msg): print(f'Debug: {msg}')
        return SimpleLogger()
    
    def run_update(self, source: str = None) -> Dict[str, float]:
        '''
        Запуск обновления курсов
        '''
        self.logger.info('Starting rates update...')
        
        all_rates = {}
        successful_sources = []
        
        sources_to_update = [source] if source else list(self.clients.keys())
        
        for source_name in sources_to_update:
            if source_name not in self.clients:
                self.logger.warning(f'Unknown source: {source_name}')
                continue
            
            try:
                self.logger.info(f'Fetching rates from {source_name}...')
                rates = self.clients[source_name].fetch_rates()
                
                if not rates:
                    self.logger.warning(f'No rates returned from {source_name}')
                    continue
                
                for pair_key, rate in rates.items():
                    try:
                        if '_' in pair_key:
                            from_currency, to_currency = pair_key.split('_')
                        else:
                            self.logger.warning(f'Invalid pair format: {pair_key}')
                            continue
                        
                        rate_record = {
                            'from_currency': from_currency,
                            'to_currency': to_currency,
                            'rate': rate,
                            'source': source_name,
                            'meta': {
                                'request_timestamp': datetime.now().isoformat()
                            }
                        }
                        self.storage.save_exchange_rate(rate_record)
                    except Exception as e:
                        self.logger.error(f'Error processing {pair_key}: {e}')
                
                all_rates.update(rates)
                successful_sources.append(source_name)
                self.logger.info(f'Successfully fetched {len(rates)} rates from {source_name}')
                
            except ApiRequestError as e:
                self.logger.error(f'API error from {source_name}: {e}')
            except Exception as e:
                self.logger.error(f'Unexpected error from {source_name}: {e}')
        
        if all_rates:
            self.storage.save_current_rates(all_rates, ','.join(successful_sources))
            self.logger.info(f'Update completed. Total rates: {len(all_rates)}')
            
            self._save_to_files(all_rates, successful_sources)
        else:
            self.logger.warning('No rates were updated')
        
        return all_rates
    
    def _save_to_files(self, rates: Dict[str, float], sources: list):
        '''
        Сохранение курсов в JSON файлы.
        Передаём rates (список полученных валют) в виде словаря а source (источники) в виде списка
        '''
        try:
            import json
            from datetime import datetime
            
            data_to_save = {
                'timestamp': datetime.now().isoformat(),
                'source': ', '.join(sources),
                'base_currency': self.config.BASE_CURRENCY,
                'rates': rates,
                'total_pairs': len(rates)
            }
            
            with open(self.config.RATES_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            print(f'Данные сохранены в {self.config.RATES_FILE_PATH}')
            
            with open(self.config.HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_data = []
            
            if isinstance(existing_data, list):
                existing_data.append(data_to_save)
            else:
                existing_data = [existing_data, data_to_save]
            
            with open(self.config.HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            print(f'Данные добавлены в {self.config.HISTORY_FILE_PATH}')
            
        except Exception as e:
            self.logger.error(f'Error saving to files: {e}')
    
    def get_update_status(self) -> Dict[str, Any]:
        '''
        Получение статуса последнего обновления
        '''
        try:
            import json
            import os
            
            if os.path.exists(self.config.RATES_FILE_PATH):
                with open(self.config.RATES_FILE_PATH, 'r', encoding='utf-8') as f:
                    rates_data = json.load(f)
                
                return {
                    'last_refresh': rates_data.get('timestamp'),
                    'total_pairs': rates_data.get('total_pairs', 0),
                    'source': rates_data.get('source', 'unknown')
                }
            else:
                return {
                    'last_refresh': None,
                    'total_pairs': 0,
                    'source': 'unknown'
                }
                
        except Exception as e:
            self.logger.error(f'Error getting status: {e}')
            return {
                'last_refresh': None,
                'total_pairs': 0,
                'source': 'error'
            }
            
            
