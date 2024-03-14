from datetime import date,datetime,timedelta
from CodeCrafters_assistant.utils import Utils, Translate

class DialogueBranches:
    def set_edit_object(self, *args):
        if self.field_id != 4:
            cfg = {   0:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('enter_new_text')}", "checks":{}, "actions":{self.edit_contact:[]}}
                    }
            self.dialogue_constructor(cfg)
        else:
            cfg = {   0:{ "type":"show", "checks":{}, "string":self.print_edit_phone_options()},
                        1:{ "type":"act", "prompt":f"{self.opnng_alt}{self.translate_string('choose_phone_edit_option')}", "checks":{self.correct_edit_dict_option:[]}, "actions":{self.set_edit_phone_option:[]}},
                    }
            self.dialogue_constructor(cfg)

    def set_edit_phone_option(self, option):
        option = self.input_to_id(self.single_param(option))
        if option == 0:
            cfg = {   0:{ "type":"show", "checks":{self.contact_has_phones:[]}, "string":{self.print_contact_phones:[]}},
                        1:{ "type":"act", "prompt":f"{self.opnng_alt}{self.translate_string('choose_contact_phone')}", "checks":{self.correct_phone_id:[]}, "actions":{self.set_current_field_id:[]}},
                        2:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('enter_new_phone')}", "checks":{}, "actions":{self.edit_phones:[], self.current_reset_and_save:[]}},
                    }
            self.dialogue_constructor(cfg)
        else:
            cfg = {   0:{ "type":"act", "prompt":f"{self.opnng}{self.translate_string('phone_number_add')}", "checks":{}, "actions":{self.add_phone:[], self.current_reset_and_save:[]}},
                    }
            self.dialogue_constructor(cfg)

    def set_remove_option(self, option):
        option = self.input_to_id(self.single_param(option))
        if option == 0:
            cfg = {     0:{ "type":"show", "checks":{}, "string":{self.remove_record_ask:[self.translate_string('contact_remove_submit','green')]}},
                        1:{ "type":"act", "prompt":self.confirmation, "checks":{}, "actions":{self.remove_contact_submit:[]}},
                    }
            self.dialogue_constructor(cfg)
        else:
            cfg = {     0:{ "type":"show", "checks":{}, "string":{self.print_record_attributes:[]}},
                        1:{ "type":"act", "prompt":f"{self.opnng_alt}{self.translate_string('enter_remove')}", "checks":{self.correct_field_id:[]}, "actions":{self.set_current_field_id:[], self.set_remove_object:[]}},
                    }
            self.dialogue_constructor(cfg)

    def set_remove_object(self, *args):
        if self.field_id != 4:
            cfg = {     0:{ "type":"show", "checks":{}, "string":{self.remove_attribute_ask:[]}},
                        1:{ "type":"act", "prompt":self.confirmation, "checks":{}, "actions":{self.remove_attribute_submit:[]}},
                    }
            self.dialogue_constructor(cfg)
        else:
            cfg = {     0:{ "type":"show", "checks":{self.contact_has_phones:[]}, "string":{self.print_contact_phones:[]}},
                        1:{ "type":"act", "prompt":f"{self.opnng_alt}{self.translate_string('choose_phone_to_delete')}", "checks":{self.correct_phone_id:[]}, "actions":{self.set_current_field_id:[]}},
                        2:{ "type":"show", "checks":{}, "string":{self.remove_phone_ask:[]}},
                        3:{ "type":"act", "prompt":self.confirmation, "checks":{}, "actions":{self.remove_phone_submit:[]}},
                    }
            self.dialogue_constructor(cfg)

class ContactBookActions():
    def print_edit_phone_options(self, *args):
        string = f"{self.translate_string('how_to_edit_phone_p0','green')}\n{self.RED}0{self.GREEN}. {self.translate_string('how_to_edit_phone_p1')}\n{self.RED}1{self.GREEN}. {self.translate_string('how_to_edit_phone_p2')}\n"
        return string
           
    def remove_contact_submit(self, answer:str):
        answer = self.single_param(answer)
        if answer.lower().strip() in self.parent.confirm:
            print(self.translate_string('contact_removed','yellow','green'))
            self.update_file(mode="del", r_id=self.ongoing)
            self.ongoing = None
            return
        elif answer.lower().strip() in self.parent.deny:
            print(self.translate_string('contact_remove_abort','yellow','green'))
            return

        return ' '
   
    def remove_attribute_submit(self, answer:str):
        answer = self.single_param(answer)
        record = self.data[self.ongoing]
        if answer.lower().strip() in self.parent.confirm:
            if self.field_id == 0:
                record.remove_name()
            elif self.field_id == 1:
                record.remove_birthday()
            elif self.field_id == 2:
                record.remove_email()
            elif self.field_id == 3:
                record.remove_address()

            self.current_reset_and_save()
            return
        elif answer.lower().strip() in self.parent.deny:
            print(self.translate_string('contact_remove_abort','yellow','green'))
            return

        return ' '

    def remove_phone_ask(self):
        return f"{self.translate_string('remove_attribute_ask_p0','yellow','red')} {self.translate_string('attr_4_1','red')} {self.translate_string('remove_attribute_ask_p1','yellow','red')} ( {self.data[self.ongoing].data['Phones'][self.field_id]} )"

    def remove_phone_submit(self, answer:str):
        answer = self.single_param(answer)
        record = self.data[self.ongoing]
        if answer.lower().strip() in self.parent.confirm:
            record.phone_check_and_set(mode='del',phone=record.data['Phones'][self.field_id])
            record.rearrange_phones()
            self.current_reset_and_save()
            return
        elif answer.lower().strip() in self.parent.deny:
            print(self.translate_string('contact_remove_abort','yellow','green'))
            return

        return ' '
    
    def print_contact_phones(self, *args):
        string = self.translate_string('choose_the_phone','green')
        string += ":\n" + "".join(f'{self.RED}{phone_id}{self.GREEN}. {phone_number};\n' for phone_id, phone_number in self.data[self.ongoing].data['Phones'].items())
        return string

    def contactbook_error(func):
        def true_handler(self,arg):
            try:
                result = func(self,arg)
            except ValueError as error_text:
                return str(error_text)
        return true_handler

    @contactbook_error
    def add_name(self,name):
        name = self.single_param(name)
        record = self.data[self.ongoing]
        if self.dialogue_check(name):
            record.add_name(name)

    @contactbook_error
    def add_birthday(self,birthday):
        birthday = self.single_param(birthday)
        record = self.data[self.ongoing]
        if self.dialogue_check(birthday):
            record.add_birthday(birthday)

    @contactbook_error
    def add_email(self,email):
        email = self.single_param(email)
        record = self.data[self.ongoing]
        if self.dialogue_check(email):
            record.add_email(email)

    @contactbook_error
    def add_address(self,address):
        address = self.single_param(address)
        record = self.data[self.ongoing]
        if self.dialogue_check(address):
            record.add_address(address)

    @contactbook_error
    def add_phone(self,phone):
        phone = self.single_param(phone)
        record = self.data[self.ongoing]
        if self.dialogue_check(phone):
            record.phone_check_and_set(mode='add', phone=phone)

    @contactbook_error
    def edit_phones(self, new_text):
        new_text = self.single_param(new_text)
        record = self.data[self.ongoing]
        record.phone_check_and_set(mode='ed', phone=record.data['Phones'][self.field_id], new_phone=new_text)
        print(f"{self.translate_string('attr_4_1','yellow')} {self.translate_string('edit_contact_p1',end_color='green')}")

    @contactbook_error
    def edit_contact(self, new_text):
        new_text = self.single_param(new_text)
        if self.field_id == 0:
            self.data[self.ongoing].add_name(new_text)
        elif self.field_id == 1:
            self.data[self.ongoing].add_birthday(new_text)
        elif self.field_id == 2:
            self.data[self.ongoing].add_email(new_text)
        elif self.field_id == 3:
            self.data[self.ongoing].add_address(new_text)
        
        print(f"{self.translate_string(f'attr_{self.field_id}','yellow')} {self.translate_string('edit_contact_p1','yellow','green')}")
        self.current_reset_and_save()

    def find_hub(self, text):
        text = self.single_param(text)
        string = ""
        check = False
        mode = None
        if self.field_id != 5:
            mode = self.field_id
        else:
            mode = "all"
        for contact_id,class_instance in self.data.items():
            elements = { "intro":f"{self.RED}{contact_id}{self.GREEN}. ", 
                        "what":text, 
                        "where":mode, 
                        0:[self.translate_string('attr_0','red','green'),f"{class_instance.data['Name']}; "], 
                        1:[self.translate_string('attr_1','red','green'),f"{class_instance.data['Birthday']}; "], 
                        2:[self.translate_string('attr_2','red','green'),f"{class_instance.data['Email']}; "], 
                        3:[self.translate_string('attr_3','red','green'),f"{class_instance.data['Address']}; "], 
                        4:[self.translate_string('attr_4','red','green'),f"{'; '.join(f'{phone_number}' for phone_number in class_instance.data['Phones'].values())};\n"]
                        }
            result = self.constructor(elements)
            if result:
                string += result
                check = True

        if check != False:
            print(f"{self.translate_string('find_hub_intro','green')}:\n{string}")
        else:
            print(self.translate_string('find_hub_fail','yellow','green'))

class ContactBookChecks():
    def contact_has_phones(self):
        if len(self.data[self.ongoing].data['Phones']) > 0:
            return True
        else:
            return self.translate_string('no_phone_numbers_error','yellow','green')

    def correct_phone_id(self, field_id):
        field_id = self.input_to_id(self.single_param(field_id))
        record = self.data[self.ongoing]
        if (type(field_id) == int) and (field_id <= (len(record.data['Phones']) - 1)):
            return True
        elif type(field_id) == str:
            return field_id
        else:
            return self.translate_string('wrong_id_error','yellow','green')

class WebManager(ContactBookActions, ContactBookChecks, DialogueBranches, Utils, Translate):
    def __init__(self, parent_class):
        self.parent = parent_class
        self.parent.modules.append(self)
        self.parent.module_chosen = len(self.parent.modules) - 1
        self.reinit(mode='first')
        import pathlib
        self.file = f"{pathlib.Path(__file__).parent.resolve()}/storage.json"
        self.update_file("load")

    def reinit(self, mode=None):
        tmp = None
        if type(self.parent.module_chosen) == int:
            tmp = self.parent.module_chosen
        if mode != 'first':
            self.parent.module_chosen = self.parent.modules.index(self)
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
                                    self.exchange_starter:{}}}}
        if mode != 'first':
            self.parent.module_chosen = tmp
  
    def exchange_starter(self):
        cfg = {   0:{ "type":"show", "checks":{}, "string":{self.show_exchange_dates:[]}},
                    1:{ "type":"act", "prompt":f"{self.opnng_alt}{self.translate_string('days_enter')}", "checks":{self.correct_days:[]}, "actions":{self.set_session:[]}},
                    2:{ "type":"show", "checks":{}, "string":{self.show_server_response:[]}},
                }
        self.dialogue_constructor(cfg)

    def show_exchange_dates(self):
        string = self.translate_string('days_list','green')
        today = date()
        for day in range(0,10):
            date_back = (datetime(date.today().year,date.today().month,date.today().day) - timedelta(days=day)).date()
            string += f"\n{self.RED}{day}{self.GREEN}. {self.translate_string('see_for','green')} {str(date_back)}"
        return string
    
    def correct_days(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        if user_input <= 9 and user_input >= 0:
            return True
        else:
            return self.translate_string('wrong_day','yellow', 'green')
    
    def set_session(self, user_input):
        user_input = self.input_to_id(self.single_param(user_input))
        self.session_response = None #to be filled by a server response
        pass

    def show_server_response(self):
        return "123"