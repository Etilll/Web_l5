from datetime import date,datetime,timedelta
from CodeCrafters_assistant.utils import Utils, Translate
import pathlib
import json
import aiohttp
import asyncio
import platform

class WebManager(Utils, Translate):
    def __init__(self, parent_class):
        self.parent = parent_class
        self.parent.modules.append(self)
        self.parent.module_chosen = len(self.parent.modules) - 1
        self.reinit(mode='first')
        self.file = f"{pathlib.Path(__file__).parent.resolve()}/storage.json"

    def reinit(self, mode=None):
        tmp = None
        if type(self.parent.module_chosen) == int:
            tmp = self.parent.module_chosen
        if mode != 'first':
            self.parent.module_chosen = self.parent.modules.index(self)
        self.options_list = ['options_exchange']
        self.options = {}
        self.load_exchange_options()
        self.confirmation = f"{self.translate_string('please_enter_confirm_p0')} {self.translate_string('confirm','red','cyan')}/{self.translate_string('confirm_long','red','cyan')} {self.translate_string('please_enter_confirm_p1')} {self.translate_string('please_enter_confirm_p2')} {self.translate_string('deny','red','cyan')}/{self.translate_string('deny_long','red','cyan')} {self.translate_string('please_enter_confirm_p3')}"
        self.opnng = f"{self.translate_string('please_enter_p0','cyan')} "
        self.opnng_alt = f"{self.translate_string('please_enter_p0_1','cyan')} "
        self.non_obligatory = f"{self.CYAN} ({self.translate_string('please_enter_p1')} '{self.translate_string('deny','red','cyan')}/{self.translate_string('deny_long','red','cyan')}'{self.translate_string('please_enter_p3')})"
        self.method_table = {'__localization':{
                                'name':"module_name",
                                'description':"module_desc"},
                            'exchange':{
                                'description':"exchange_desc", 
                                'methods':{
                                    self.exchange_starter:{}}},
                            'settings':{
                                'description':"settings_desc", 
                                'methods':{
                                    self.settings_starter:{}}}}
        if mode != 'first':
            self.parent.module_chosen = tmp
  
    def load_exchange_options(self):
        default_set = {0:['USD', True], 1:['EUR', True], 2:['AUD', False], 3:['AZN', False], 4:['BYN', False], 5:['CAD', False], 6:['CHF', False], 7:['CNY', False],
                        8:['CZK', False], 9:['DKK', False], 10:['GBP', False], 11:['GEL', False], 12:['HUF', False], 13:['ILS', False], 14:['JPY', False], 15:['KZT', False],
                        16:['MDL', False], 17:['NOK', False], 18:['PLN', False], 19:['SEK', False], 20:['SGD', False], 21:['TMT', False], 22:['TRY', False], 23:['UZS', False],
                        24:['XAU', False]}
        stor = pathlib.Path(f"{pathlib.Path(__file__).parent.resolve()}/configs.json")
        if not stor.exists():
            with open(stor, 'w') as ini:
                json.dump(default_set, ini, indent=2)
                self.options['exchange'] = default_set
        else:
            with open(stor, 'r') as ini:
                tmp = json.load(ini)
                self.options['exchange'] = {}
                for k,v in tmp.items():
                    self.options['exchange'][int(k)] = v

    def save_exchange_options(self):
        stor = pathlib.Path(f"{pathlib.Path(__file__).parent.resolve()}/configs.json")
        with open(stor, 'w') as ini:
            json.dump(self.options['exchange'], ini, indent=2)

    def settings_starter(self):
        cfg = {   0:{ "type":"show", "checks":{}, "string":{self.show_settings_options:[]}},
                    1:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('choose_options_command')}", "checks":{self.correct_command:[]}, "actions":{self.open_options_menu:[]}},
                }
        self.dialogue_constructor(cfg)

    def show_settings_options(self):
        string = self.translate_string('settings_options','green')
        for item in self.options_list:
            string += f"\n{self.RED}{self.options_list.index(item)}{self.GREEN}. {self.translate_string(item,'green')}"
        return string
    
    def correct_command(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        elif user_input <= (len(self.options_list) - 1):
            return True
        else:
            return self.translate_string('wrong_day','yellow', 'green')
    
    def open_options_menu(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        dependencies = {0:self.options_exchange}
        dependencies[user_input]()
    
    def options_exchange(self):
        cfg = {   0:{ "type":"show", "checks":{}, "string":{self.show_exchange_options:[]}},
                    1:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('choose_curr')}", "checks":{self.correct_curr:[]}, "actions":{self.adjust_exchange_settings:[]}},
                }
        self.dialogue_constructor(cfg)

    def show_exchange_options(self):
        string = self.translate_string('currency_choose','green')
        for id,data in self.options['exchange'].items():
            string += f"\n{self.RED}{id}{self.GREEN}. {data[0]} - {self.currency_status(data[1])}"
        string += f"\n{self.translate_string('currency_back','green')} '{self.RED}cancel{self.GREEN}'"
        return string
    
    def adjust_exchange_settings(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        elif self.options['exchange'][user_input][1]:
            self.options['exchange'][user_input][1] = False
        else:
            self.options['exchange'][user_input][1] = True
        print(self.translate_string('options_exchange_edited','yellow', 'green'))
        self.save_exchange_options()
        self.options_exchange()

    def correct_curr(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if user_input in self.options['exchange'].keys():
            return True
        else:
            return self.translate_string('wrong_id_error','yellow', 'green')

    def currency_status(self, status):
        if status:
            return self.translate_string('currency_enabled','yellow','green')
        else:
            return self.translate_string('currency_disabled','red','green')

    def exchange_starter(self):
        cfg = {   0:{ "type":"show", "checks":{}, "string":{self.show_exchange_dates:[]}},
                    1:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('choose_date')}", "checks":{self.correct_days:[]}, "actions":{self.branch_exchange:[]}}
                }
        self.dialogue_constructor(cfg)

    def show_exchange_dates(self):
        string = self.translate_string('days_list','green')
        for day in range(0,11):
            date_back = (datetime(date.today().year,date.today().month,date.today().day) - timedelta(days=day)).date()
            string += f"\n{self.RED}{day}{self.GREEN}. {self.translate_string('see_for','green')} {str(date_back)}"
        string += f"\n{self.RED}11{self.GREEN}. {self.translate_string('see_free_number','green')}"
        return string
    
    def correct_days(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        elif user_input <= 11:
            return True
    
    def set_session(self, user_input):
        user_input = user_input[0]
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        date_back = (datetime(date.today().year,date.today().month,date.today().day) - timedelta(days=user_input)).date()
        today_day = self.day_format(date_back.day)
        today_month = self.day_format(date_back.month)
        today_year = self.day_format(date_back.year)

        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(self.connect(today_day=today_day,today_month=today_month,today_year=today_year))
        if result == 'abort':
            return result
        return ""

    def show_server_response(self):
        string = self.translate_string('currency_show', 'green')
        for key,value in self.options['exchange'].items():
            if value[1]:
                for item in self.session_response:
                    if item['currency'] == value[0]:
                        string += f"\n{self.RED}{key}. {value[0]}{self.GREEN}: {self.translate_string('currency_sell')} - {item['saleRateNB']}, {self.translate_string('currency_buy')} - {item['purchaseRateNB']}"
        return string
    
    def day_format(self, var):
        if len(str(var)) == 1:
            return f'0{str(var)}'
        else:
            return str(var)

    def branch_exchange(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        cfg = None
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        elif user_input != 11:
            cfg = {   0:{ "type":"show", "checks":{}, "string":{self.set_session:[user_input], self.show_server_response:[]}}
                    }
        else:
            cfg = {   0:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('days_enter')}", "checks":{self.correct_days_free:[]}, "actions":{self.set_session_free:[]}},
                        1:{ "type":"show", "checks":{}, "string":{self.show_server_response_free:[]}},
                    }

        self.dialogue_constructor(cfg)

    def correct_days_free(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        elif user_input <= 10:
            return True
    
    def set_session_free(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        self.session_response = {}
        days_list = []
        if type(user_input) != int:
            return self.translate_string('wrong_id_error','yellow', 'green')
        elif user_input != 0:
            for num in range(0,user_input + 1):
                date_back = (datetime(date.today().year,date.today().month,date.today().day) - timedelta(days=num)).date()
                today_day = self.day_format(date_back.day)
                today_month = self.day_format(date_back.month)
                today_year = self.day_format(date_back.year)
                days_list.append([today_day, today_month, today_year])
        else:
            today_day = self.day_format(date.today().day)
            today_month = self.day_format(date.today().month)
            today_year = self.day_format(date.today().year)
            days_list.append([today_day, today_month, today_year])

    
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(self.connect(days_list=days_list))
        if result == 'abort':
            return result
        
    def show_server_response_free(self):
        result_list = []
        for day,rates in self.session_response.items():
            data_to_append = {day:{}}
            for key,value in self.options['exchange'].items():
                if value[1]:
                    for item in rates:
                        if item['currency'] == value[0]:
                            data_to_append[day][value[0]] = {}
                            data_to_append[day][value[0]]['sale'] = item['saleRateNB']
                            data_to_append[day][value[0]]['purchase'] = item['purchaseRateNB']
                            break
            result_list.append(data_to_append)
        return result_list
    
    async def connect(self, today_day=None,today_month=None,today_year=None,days_list=None):
        self.session = aiohttp.ClientSession()
        if days_list == None and (today_day and today_month and today_year):
            async with self.session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={today_day}.{today_month}.{today_year}') as response:
                if response.status < 400:
                    result = await response.json()
                    self.session_response = result['exchangeRate']
                else:
                    print(f"{self.YELLOW}Network error. Aborting the operation.{self.DEFAULT}")
                    return 'abort'
        elif days_list != None:
            async def req_send(day_list):
                async with self.session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={day_list[0]}.{day_list[1]}.{day_list[2]}') as response:
                    if response.status < 400:
                        result = await response.json()
                        self.session_response[f"{day_list[1]}.{day_list[0]}.{day_list[2]}"] = result['exchangeRate']
                        return
                    else:
                        print(f"{self.YELLOW}Network error. Aborting the operation.{self.DEFAULT}")
                        return 'abort'
                    
            [await asyncio.create_task(req_send(day_list)) for day_list in days_list]
        await self.session.close()
        
    
