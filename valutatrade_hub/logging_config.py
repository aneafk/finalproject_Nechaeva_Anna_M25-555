# valutatrade_hub/logging_config.py
import logging as lg
import logging.handlers as hd
import os


# Функция для системы логирования
def setup_logging():
    '''
    Настройка системы логирования
    '''
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    formatter = lg.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = hd.RotatingFileHandler(
        filename=os.path.join(log_dir, 'valutatrade.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    console_handler = lg.StreamHandler()
    console_handler.setFormatter(formatter)
    
    root_logger = lg.getLogger()
    root_logger.setLevel(lg.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    actions_logger = lg.getLogger('actions')
    actions_handler = hd.RotatingFileHandler(
        filename=os.path.join(log_dir, 'actions.log'),
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    actions_handler.setFormatter(formatter)
    actions_logger.addHandler(actions_handler)
    actions_logger.setLevel(lg.INFO)
    actions_logger.propagate = False


# Функция для логгера
def get_logger(name: str) -> lg.Logger:
    return lg.getLogger(name)
    
    
