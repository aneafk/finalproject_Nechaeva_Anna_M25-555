# valutatrade_hub/parser_service/storage.py
from datetime import datetime
from typing import Any, Dict, List

from ..infra.database import db


class ParserStorage:
    '''
    Класс для работы с хранилищем данных парсера
    '''
    
    def save_exchange_rate(self, rate_data: Dict[str, Any]):
        '''
        Сохранение одной записи о курсе в историю
        '''
        def update_history(history: List) -> List:
            rate_data['id'] = self._generate_rate_id(rate_data)
            rate_data['timestamp'] = datetime.now().isoformat()
            
            history.append(rate_data)
            return history[-1000:]
        
        db.update_data('exchange_rates', update_history)
    
    def save_current_rates(self, rates: Dict[str, float], source: str):
        '''
        Сохранение текущих курсов в кеш
        '''
        current_time = datetime.now().isoformat()
        
        rates_data = {
            'pairs': {},
            'last_refresh': current_time,
            'source': source
        }
        
        for pair_key, rate in rates.items():
            rates_data['pairs'][pair_key] = {
                'rate': rate,
                'updated_at': current_time,
                'source': source
            }
        
        db.save_data('rates', rates_data)
    
    def get_historical_rates(self, currency_pair: str, limit: int = 100) -> List[Dict]:
        '''
        Получение исторических данных по паре валют
        '''
        history = db.load_data('exchange_rates') or []
        
        filtered = [
            record for record in history 
            if record.get('from_currency', '').lower() == currency_pair.lower()
        ]
        
        return filtered[-limit:]
    
    def _generate_rate_id(self, rate_data: Dict[str, Any]) -> str:
        '''
        Генерация уникального ID для записи курса
        '''
        from_currency = rate_data.get('from_currency', '')
        to_currency = rate_data.get('to_currency', '')
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return f'{from_currency}_{to_currency}_{timestamp}'
