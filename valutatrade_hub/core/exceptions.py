# valutatrade_hub/core/exceptions.py



class ValutaTradeError(Exception):
    '''
    Базовое исключение для приложения
    '''
    pass


class InsufficientFundsError(ValutaTradeError):
    '''
    Обработка исключения - не можешь списать денег больше чем у тебя есть (купить/продать)
    '''
    def __init__(self, available: float, required: float, code: str):
        self.available = available
        self.required = required
        self.code = code
        super().__init__(f'Ошибка: Недостаточно средств: доступно {available} {code}, требуется {required} {code}')


class CurrencyNotFoundError(ValutaTradeError):
    '''
    Проверяет существует ли данная валюта или нет
    '''
    def __init__(self, code: str):
        self.code = code
        super().__init__(f'Ошибка: Неизвестная валюта "{code}"')


class ApiRequestError(ValutaTradeError):
    '''
    Обрабатывает ошибки от apu
    '''
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f'Ошибка: Ошибка при обращении к внешнему API: {reason}')


class UserNotFoundError(ValutaTradeError):
    '''
    Обрабатывает вход пользователя, если не найден возвращает ошибку
    '''
    def __init__(self, username: str):
        super().__init__(f'Ошибка: Пользователь "{username}" не найден')


class AuthenticationError(ValutaTradeError):
    '''
    Обрабатывает вход пользователя - проверяет пароль и если пароль неверный, возвращает ошибку
    '''
    def __init__(self):
        super().__init__('Ошибка: Неверный пароль')


class UsernameTakenError(ValutaTradeError):
    '''
    Обрабатывает регистрацию (если пользователь с таким именем уже существует - вернет ошибку)
    '''
    def __init__(self, username: str):
        super().__init__(f'Ошибка: Имя пользователя "{username}" уже занято')


class UsernamePasswordError(ValutaTradeError):
    '''
    Обрабатывает неверно введеный пароль
    '''
    def __init__(self):
        super().__init__('Ошибка: Минимальная длина пароля - 4 символа')
        
        
