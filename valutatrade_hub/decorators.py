# valutatrade_hub/decorators.py
import functools
from datetime import datetime
from typing import Any, Callable

from .logging_config import get_logger


# Функция декоратора для логирования действий
def log_action(user_action: str, verbose: bool = False):
    '''
    Декоратор для логирования действий пользователя
    '''
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger('actions')
            
            user_info = "unknown"
            currency_code = kwargs.get('currency_code', '')
            amount = kwargs.get('amount', 0)
            
            for arg in args:
                if hasattr(arg, 'user_id'):
                    user_info = f"user_id={arg.user_id}"
                elif hasattr(arg, '_user_id'):
                    user_info = f"user_id={arg._user_id}"
                elif isinstance(arg, int) and arg > 0:
                    user_info = f"user_id={arg}"
            
            extra_info = {
                'action': user_action,
                'user': user_info,
                'currency': currency_code,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                result = func(*args, **kwargs)
                extra_info['result'] = 'OK'
                
                if verbose:
                    if hasattr(result, '__dict__'):
                        extra_info['details'] = str(result.__dict__)
                
                logger.info(f"{user_action} completed successfully", extra=extra_info)
                return result
                
            except Exception as e:
                extra_info['result'] = 'ERROR'
                extra_info['error_type'] = type(e).__name__
                extra_info['error_message'] = str(e)
                logger.error(f"{user_action} failed: {e}", extra=extra_info)
                raise
        
        return wrapper
    return decorator
    
    
