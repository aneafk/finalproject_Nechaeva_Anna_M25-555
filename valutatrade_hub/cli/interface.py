# valutatrade_hub/cli/interface.py
import os
import sys

from ..infra.database import db


class InteractiveCLI:
    def __init__(self):
        from ..core.currencies import CurrencyRegistry, initialize_currencies
        from ..core.usecases import PortfolioManager, RateManager, UserManager
        from ..logging_config import setup_logging
        from ..parser_service.config import ParserConfig
        from ..parser_service.scheduler import Scheduler
        from ..parser_service.updater import RatesUpdater
        
        self.parser_config = ParserConfig.from_env()
        self.rates_updater = RatesUpdater(self.parser_config)
        self.scheduler = Scheduler(self.parser_config)

        setup_logging()
        initialize_currencies()
        
        self.user_manager = UserManager()
        self.portfolio_manager = PortfolioManager()
        self.rate_manager = RateManager()
        self.currency_registry = CurrencyRegistry
        
        self.menu_options = {
            'register': ('Register', self.register),
            'login': ('Login', self.login),
            'portfolio': ('Show-portfolio', self.show_portfolio),
            'buy': ('Buy currency', self.buy_currency),
            'sell': ('Sell currency', self.sell_currency),
            'get-rate': ('Get-rate', self.show_rates),
            'show-rates': ('Show-rates', self.show_rates_command),
            'update': ('Update-rates', self.update_rates),
            'parser': ('Status-parser', self.parser_status),
            'autoupdate': ('Run autoupdate', self.start_auto_update),
            'stop': ('Stop autoupdate', self.stop_auto_update),
            'exit': ('Exit', self.exit_app),
            'quit': ('Exit', self.exit_app)
        }
        
        self.digit_mapping = {
            '1': 'register',
            '2': 'login', 
            '3': 'portfolio',
            '4': 'buy',
            '5': 'sell',
            '6': 'get-rate',
            '7': 'show-rates',
            '8': 'update',
            '9': 'parser',
            '10': 'autoupdate',
            '11': 'stop',
            '12': 'exit'
        }
        
        self.menu_options_desc = {
            'register': 'Зарегистрировать новый аккаунт',
            'login': 'Войти в существующий аккаунт',
            'portfolio': 'Просмотреть свое портфолио',
            'buy': 'Купить валюту',
            'sell': 'Продать валюту',
            'get-rate': 'Получить актуальные курсы',
            'show-rates': 'Показать текущие выгруженные курсы',
            'update': 'Обновить текущие курсы',
            'parser': 'Запустить парсер',
            'autoupdate': 'Запустить автообновление',
            'stop': 'Выключить автообновление',
            'exit': 'Выйти из программы',
            'quit': 'Так же выйти из программы'
        }


    def update_rates(self):
        '''
        Ручное обновление курсов
        '''
        self.clear_screen()
        self.print_header('Процедура: Обновление курсов валют')       
        print('Выберите источник для обновления:')
        print('1. Все источники')
        print('2. Только CoinGecko')
        print('3. Только ExchangeRate-API')
        print()
        
        choice = input('Ваш выбор (1-3): ').strip()
        
        source_map = {
            '1': None,
            '2': 'coingecko', 
            '3': 'exchangerate'
        }
        
        source = source_map.get(choice)
        if source is None and choice != '1':
            print('Ошибка: Неверный выбор!')
            self.wait_for_enter()
            return
        
        try:
            print(f'\nОбновление курсов из {source or "всех источников"}...')
            rates = self.rates_updater.run_update(source)
            
            print('Обновление завершено!')
            print(f'Получено курсов: {len(rates)}')
            print(f'Время обновления: {self.rates_updater.get_update_status()['last_refresh']}')
            
        except Exception as e:
            print(f'Ошибка: Ошибка при обновлении: {e}')
        
        self.wait_for_enter()
    
    def parser_status(self):
        '''
        Статус парсера
        '''
        self.clear_screen()
        self.print_header('Процедура: Статус парсера')
        
        try:
            status = self.rates_updater.get_update_status()
            
            print('Статус обновления курсов:')
            print(f'Последнее обновление: {status['last_refresh'] or 'Никогда'}')
            print(f'Количество пар: {status['total_pairs']}')
            print(f'Источник: {status['source']}')
            
            rates_data = db.load_data('rates') or {}
            pairs = list(rates_data.get('pairs', {}).keys())[:5]
            
            print('\nПримеры текущих курсов:')
            for pair in pairs:
                rate_info = rates_data['pairs'][pair]
                print(f'   {pair}: {rate_info['rate']:.6f}')
            
        except Exception as e:
            print(f'Ошибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def start_auto_update(self):
        '''
        Запуск автоматического обновления
        '''
        self.clear_screen()
        self.print_header('Процедура: Автообновление курсов')
        
        try:
            self.scheduler.start()
            print('Автообновление запущено!')
            print(f'Интервал: {self.parser_config.UPDATE_INTERVAL_MINUTES} минут')
            print('Приложение продолжит работу в обычном режиме')
            
        except Exception as e:
            print(f'Ошибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def stop_auto_update(self):
        '''
        Остановка автоматического обновления
        '''
        self.clear_screen()
        self.print_header('Процедура: Остановка автообновления...')
        
        try:
            self.scheduler.stop()
            print('Автообновление успешно остановлено!')
            
        except Exception as e:
            print(f'Ошибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def clear_screen(self):
        '''
        Очистка экрана
        '''
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        '''
        Печать заголовка
        '''
        print('-' * 50)
        print(f'ValutaTrade Hub - {title}')
        print('-' * 50)
        if self.user_manager.current_user:
            print(f'Пользователь: {self.user_manager.current_user.username}')
            print(f'Дата регистрации: {self.user_manager.current_user.registration_date}')
        print()
    
    def wait_for_enter(self):
        '''
        Ожидание нажатия Enter
        '''
        input('\nНажмите Enter для продолжения...')
    
    def get_user_input(self, prompt: str, required: bool = True) -> str:
        '''
        Получение ввода от пользователя
        '''
        while True:
            value = input(prompt).strip()
            if not value and required:
                print('Ошибка: Это поле обязательно для заполнения!')
                continue
            return value
    
    def get_float_input(self, prompt: str) -> float:
        '''
        Получение числового ввода
        '''
        while True:
            try:
                value = float(input(prompt))
                if value <= 0:
                    print('Ошибка: Значение должно быть положительным!')
                    continue
                return value
            except ValueError:
                print('Ошибка: Пожалуйста, введите число!')
    
    def show_main_menu(self):
        '''
        Отображение главного меню с поддержкой цифр и слов
        '''
        print('\n' + '-'*50)
        print('          VALUTATRADE HUB - главное меню')
        print('-'*50)
        
        for digit, command in self.digit_mapping.items():
            print(f'{digit:2} -> {command} - {self.menu_options_desc[command]}')
        
        print('-'*50)
        
    
    def register(self):
        '''
        Регистрация пользователя
        '''
        self.clear_screen()
        self.print_header('Процедура: Регистрация')
        
        username = self.get_user_input('Введите имя пользователя: ')
        password = self.get_user_input('Введите пароль: ')
        
        try:
            user = self.user_manager.register_user(username, password)
            print(f'\nПользователь "{user.username}" успешно зарегистрирован!')
            print(f'ID пользователя: {user.user_id}')
        except Exception as e:
            print(f'\nОшибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def login(self):
        '''
        Вход пользователя
        '''
        self.clear_screen()
        self.print_header('Процедура: Вход в систему')
        
        username = self.get_user_input('Имя пользователя: ')
        password = self.get_user_input('Пароль: ')
        
        try:
            user = self.user_manager.login(username, password)
            print(f'\nУспешный вход! Добро пожаловать, {user.username}!')
        except Exception as e:
            print(f'\nОшибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def show_portfolio(self):
        '''
        Показать портфель
        '''
        if not self.user_manager.current_user:
            print('\nСначала выполните вход!')
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header('Процедура: Ваш портфель')
        
        try:
            portfolio = self.portfolio_manager.get_user_portfolio(
                self.user_manager.current_user.user_id
            )
            
            if not portfolio.wallets:
                print('Ошибка: Ваш портфель пуст.')
                self.wait_for_enter()
                return
            
            base_currency = 'USD'
            total_value = 0.0
            

            print(f'{"Валюта":<10} {"Баланс":<15} {"Стоимость в USD":<20}')
            print('-' * 50)
            

            for currency_code, wallet in portfolio.wallets.items():
                if currency_code == base_currency:
                    value = wallet.balance
                else:
                    try:
                        rate = self.rate_manager.get_rate(currency_code, base_currency)
                        value = wallet.balance * rate
                    except Exception:
                        value = 0.0
                
                total_value += value
                
                balance_str = f'{wallet.balance:.2f}'
                value_str = f'{value:,.2f}' if value >= 1000 else f'{value:.2f}'
                
                print(f'{currency_code:<10} {balance_str:<15} {value_str:<20} {base_currency}')
            
            print('-' * 50)
            print(f'{"ОБЩАЯ СТОИМОСТЬ":<25} {total_value:,.2f} {base_currency}')
            
        except Exception as e:
            print(f'\nОшибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def buy_currency(self):
        '''
        Покупка валюты
        '''
        if not self.user_manager.current_user:
            print('\nОшибка: Сначала выполните вход!')
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header('Процедура: Покупка валюты')
        
        try:
            currency_code = self.get_user_input('Код валюты (например, BTC, EUR): ').upper()
            amount = self.get_float_input('Количество для покупки: ')
            
            if currency_code == 'USD':
                print('Ошибка: Нельзя покупать USD, так как это базовая валюта!')
                self.wait_for_enter()
                return
            
            portfolio = self.portfolio_manager.get_user_portfolio(
                self.user_manager.current_user.user_id
            )
            
            if 'USD' not in portfolio.wallets or portfolio.wallets['USD'].balance <= 0:
                print('Ошибка: У вас нет средств в USD для покупки!')
                self.wait_for_enter()
                return
            
            try:
                rate = self.rate_manager.get_rate(currency_code, 'USD')
            except Exception as e:
                print(f'Ошибка: Не удалось получить курс для {currency_code}: {e}')
                self.wait_for_enter()
                return
            
            cost = amount * rate
            usd_balance = portfolio.wallets['USD'].balance
            
            print('\n Детали покупки:')
            print(f'   Валюта: {currency_code}')
            print(f'   Количество: {amount}')
            print(f'   Текущий курс: 1 {currency_code} = {rate:.6f} USD')
            print(f'   Общая стоимость: {cost:,.2f} USD')
            print(f'   Ваш текущий баланс USD: {usd_balance:,.2f}')
            print(f'   Баланс после покупки: {usd_balance - cost:,.2f} USD')
            
            if cost > usd_balance:
                print('\n Ошибка: Недостаточно средств!')
                print(f'   Требуется: {cost:,.2f} USD')
                print(f'   Доступно: {usd_balance:,.2f} USD')
                self.wait_for_enter()
                return
            
            confirm = input('\nПодтвердить покупку? (y/n): ').lower()
            if confirm == 'y':
                try:   
                    result = self.portfolio_manager.buy_currency(
                        self.user_manager.current_user.user_id,
                        currency_code,
                        amount,
                        'USD'
                    )
                    
                    print('\n Покупка выполнена успешно!')
                    print(f'   Куплено: {amount} {currency_code}')
                    print(f'   Стоимость: {cost:,.2f} USD')
                    print(f'   Новый баланс {currency_code}: {result['new_balance']}')
                    print(f'   Новый баланс USD: {result['base_currency_new_balance']:,.2f}')
                    
                except Exception as e:
                    print(f'\n Ошибка: Ошибка при выполнении операции: {repr(e)}')
                    print(f'Тип ошибки: {type(e).__name__}')
                    print('Полная трассировка ошибки:')
                    import traceback
                    traceback.print_exc()
            else:
                print('\n Покупка отменена.')
        
        except Exception as e:
            print(f'\nОшибка: Общая ошибка: {repr(e)}')
            import traceback
            traceback.print_exc()
        
        self.wait_for_enter()
    
    def sell_currency(self):
        '''
        Продажа валюты
        '''
        if not self.user_manager.current_user:
            print('\nОшибка: Сначала выполните вход!')
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header('Процедура: Продажа валюты')
        
        try:
            portfolio = self.portfolio_manager.get_user_portfolio(
                self.user_manager.current_user.user_id
            )
            
            if not portfolio.wallets:
                print('Ошибка: Ваш портфель пуст.')
                self.wait_for_enter()
                return
            
            available_currencies = []
            print('Доступные валюты для продажи:')
            for currency_code, wallet in portfolio.wallets.items():
                if wallet.balance > 0 and currency_code != 'USD':
                    available_currencies.append(currency_code)
                    balance_str = f'{wallet.balance:.8f}' if currency_code in ['BTC', 'ETH'] else f'{wallet.balance:.4f}'
                    print(f'  {currency_code}: {balance_str}')
            
            if not available_currencies:
                print('Ошибка: У вас нет валют для продажи!')
                self.wait_for_enter()
                return
            
            print()
            currency_code = self.get_user_input('Код валюты для продажи: ').upper()
            
            if currency_code not in available_currencies:
                print(f'\nОшибка: У вас нет валюты {currency_code} для продажи или валюта недоступна!')
                self.wait_for_enter()
                return
            
            wallet = portfolio.wallets[currency_code]
            max_amount = wallet.balance
            
            print(f'\nДоступно для продажи: {max_amount} {currency_code}')
            amount = self.get_float_input('Количество для продажи: ')
            
            if amount > max_amount:
                print(f'\n Ошибка: Недостаточно средств! Доступно: {max_amount} {currency_code}')
                self.wait_for_enter()
                return
            
            try:
                rate = self.rate_manager.get_rate(currency_code, 'USD')
                revenue = amount * rate
                
                current_usd_balance = portfolio.wallets['USD'].balance if 'USD' in portfolio.wallets else 0
                
                print('\n Детали продажи:')
                print(f'   Валюта: {currency_code}')
                print(f'   Количество: {amount}')
                print(f'   Текущий курс: 1 {currency_code} = {rate:.6f} USD')
                print(f'   Общая выручка: {revenue:,.2f} USD')
                print(f'   Текущий баланс USD: {current_usd_balance:,.2f}')
                print(f'   Баланс USD после продажи: {current_usd_balance + revenue:,.2f}')
                
            except Exception as e:
                print(f'Ошибка: Не удалось получить курс для {currency_code}: {e}')
                self.wait_for_enter()
                return
            
            confirm = input('\nПодтвердить продажу? (y/n): ').lower()
            if confirm == 'y':
                try:
                    
                    result = self.portfolio_manager.sell_currency(
                        self.user_manager.current_user.user_id,
                        currency_code,
                        amount,
                        'USD'
                    )
                    
                    print('\n Продажа выполнена успешно!')
                    print(f'   Продано: {amount} {currency_code}')
                    print(f'   Выручка: {revenue:,.2f} USD')
                    print(f'   Новый баланс {currency_code}: {result['new_balance']}')
                    print(f'   Новый баланс USD: {result['base_currency_new_balance']:,.2f}')
                    
                except Exception as e:
                    print(f'\n Ошибка: Ошибка при выполнении операции: {repr(e)}')
                    print(f'Тип ошибки: {type(e).__name__}')
                    print('Полная трассировка ошибки:')
                    import traceback
                    traceback.print_exc()
            else:
                print('\n Продажа отменена.')
        
        except Exception as e:
            print(f'\n Ошибка: Общая ошибка: {repr(e)}')
            import traceback
            traceback.print_exc()
        
        self.wait_for_enter()
    

    def show_rates_command(self):
        '''
        Обработка команды show-rates с аргументами
        '''
        self.clear_screen()
        self.print_header('Процедура: Показать курсы валют')
        
        print('Доступные фильтры:')
        print('  - Укажите валюту (например: BTC)')
        print('  - Укажите количество топовых (например: 10)')
        print('  - Оставьте пустым для всех курсов')
        
        currency = input('Валюта (оставьте пустым для всех): ').strip() or None
        top_input = input('Топ N (оставьте пустым для всех): ').strip()
        
        top = None
        if top_input:
            try:
                top = int(top_input)
                if top <= 0:
                    print('Ошибка: Число должно быть положительным!')
                    self.wait_for_enter()
                    return
            except ValueError:
                print('Ошибка: Неверный формат числа')
                self.wait_for_enter()
                return
    
        self.show_rates(currency=currency, top=top)

    def show_rates(self, currency: str = None, top: int = None):
        '''
        Показать список актуальных курсов с возможностью фильтрации
        '''
        
        try:
            rates_data = db.load_data('rates') or {'rates': {}, 'timestamp': None}
            rates = rates_data.get('rates', {})
            timestamp = rates_data.get('timestamp')
            
            if not rates:
                print('Ошибка: Нет данных о курсах. Выполните обновление данных.')
                self.wait_for_enter()
                return
            
            currency_rates = []
            base_currency = 'USD'
            
            for pair, rate in rates.items():
                if '_' in pair:
                    from_curr, to_curr = pair.split('_', 1)
                    
                    if to_curr == base_currency:
                        currency_rates.append({
                            'currency': from_curr,
                            'rate': rate,
                            'pair': pair
                        })
                    elif from_curr == base_currency:
                        currency_rates.append({
                            'currency': to_curr,
                            'rate': 1 / rate if rate != 0 else 0,
                            'pair': pair
                        })
            filtered_rates = currency_rates
            
            if currency:
                filtered_rates = [r for r in filtered_rates 
                                if r['currency'].upper() == currency.upper()]
                if not filtered_rates:
                    print(f'Ошибка: Валюта "{currency}" не найдена.')
                    self.wait_for_enter()
                    return
            
            if top:
                filtered_rates.sort(key=lambda x: x['rate'], reverse=True)
                filtered_rates = filtered_rates[:top]
            else:
                filtered_rates.sort(key=lambda x: x['currency'])
            
            self._display_rates_table(filtered_rates, base_currency, timestamp)
            
        except Exception as e:
            print(f'Ошибка: Ошибка при получении курсов: {e}')
        
        self.wait_for_enter()

    def _display_rates_table(self, rates, base_currency, timestamp):
        '''
        Отображение таблицы с курсами валют
        '''
        from prettytable import PrettyTable
        
        if not rates:
            print('Ошибка: Нет данных для отображения.')
            return
        
        table = PrettyTable()
        table.field_names = ['Валюта', f'Курс ({base_currency})', 'Обновлено']
        table.align['Валюта'] = 'l'
        table.align[f'Курс ({base_currency})'] = 'r'
        
        for rate_info in rates:
            currency = rate_info['currency']
            rate = rate_info['rate']
            
            if rate >= 1:
                formatted_rate = f'{rate:,.2f}'
            else:
                formatted_rate = f'{rate:.6f}'
            
            update_time = 'Недавно'
            if timestamp:
                from datetime import datetime
                try:
                    update_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    update_time = update_dt.strftime('%H:%M:%S')
                except (ValueError, AttributeError):
                    update_time = timestamp
            
            table.add_row([currency, formatted_rate, update_time])
        
        print('\n' + '-'*50)
        print('КУРСЫ ВАЛЮТ')
        print('-'*50)
        if not self.rate_manager.is_rates_data_fresh():
               print('Предупреждение: Данные о курсах могут быть устаревшими. Рекомендуется обновить курсы.')
        print(table)
        print(f'\nВсего валют: {len(rates)}')
    
    def show_currency_info(self):
        '''
        Показать информацию о валютах с проверкой актуальности
        '''
        self.clear_screen()
        self.print_header('Процедура: Информация о валютах')
        
        try:
            
            currencies = self.currency_registry.get_all_currencies()
            
            print('Информация о валютах:')
            print('-' * 80)
            
            for code, currency in currencies.items():
                print(currency.get_display_info())
                print('-' * 80)
                
        except Exception as e:
            print(f'\n Ошибка: Произошла ошибка: {e}')
        
        self.wait_for_enter()
    
    def exit_app(self):
        '''
        Выход из приложения
        '''
        print('\nВыход из программы ValutaTrade Hub!')
        sys.exit(0)


    def get_command(self, user_input):
        '''
        Определяет команду по вводу пользователя
        '''
        if not user_input:
            return None
            
        user_input = user_input.strip().lower()
        
        if user_input in self.digit_mapping:
            return self.digit_mapping[user_input]
        
        if user_input in self.menu_options:
            return user_input
        
        matches = [cmd for cmd in self.menu_options.keys() 
                   if cmd.startswith(user_input) and len(user_input) >= 2]
        
        if len(matches) == 1:
            return matches[0]
        
        return None
    
    def run(self):
        '''
        Запуск интерактивного интерфейса
        '''
        while True:
            try:
                self.show_main_menu()
                
                choice = input('Список доступных команд (введите текстовую команду или число 1-12): ').strip()
                
                command = self.get_command(choice)
                
                if command:
                    _, handler = self.menu_options[command]
                    handler()
                else:
                    print(f'\n Ошибка: Неверный выбор: "{choice}"! Пожалуйста, выберите от 1 до 12 или используйте команды из меню.')
                    self.wait_for_enter()
            
            except KeyboardInterrupt:
                print('\n\nОшибка: Прервано пользователем.')
                self.exit_app()
            except Exception as e:
                print(f'\nОшибка: Неожиданная ошибка: {e}')
                self.wait_for_enter()
                
                
