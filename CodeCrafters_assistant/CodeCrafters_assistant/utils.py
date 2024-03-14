class IdFormat:
    def input_to_id(self, text):
        map = {' ':'','\n':'','\t':'','\r':''}
        new_line = text.translate(map)
        try:
            if int(new_line) >= 0:
                return int(new_line)
            else:
                return self.translate_string('negative_id_error','yellow','green')
        except ValueError:
            return self.translate_string('wrong_id_error','yellow','green')

class DialogueConstructor:
    def dialogue_constructor(self,cfg:dict):
        self.args = None
        for phrase_data in cfg.values():
            if phrase_data["type"] == 'show':
                result = self.phrase_show(phrase_data)
                if result == "abort":
                    #Might create crashes, be mindful
                    self.ongoing = None
                    self.field_id = None
                    #
                    break
            else:
                result = self.phrase_act(phrase_data)
                while result != True and result != "abort":
                    if type(result) == str:
                        print(result)
                    result = self.phrase_act(phrase_data)
                if result == "abort":
                    #Might create crashes, be mindful
                    self.ongoing = None
                    self.field_id = None
                    #
                    break
    
    def phrase_act(self, phrase_data):
        self.phrase_started = False
        if self.__class__.__name__ != "InputManager":
            self.parent.technical_actions['default']["get_input"] = { 
                                            'technical':True,
                                                'methods':{self.args_dummy:{'prompt':phrase_data["prompt"]}}}
            self.parent.start_script('get_input', mode='technical') #get input here
        else:
            self.technical_actions['default']["get_input"] = { 
                                            'technical':True,
                                                'methods':{self.args_dummy:{'prompt':phrase_data["prompt"]}}}
            self.start_script('get_input', mode='technical') #get input here
        if self.args == None or 'leave' in self.args or 'cancel' in self.args:
            return "abort"
        result = None
        if phrase_data["checks"] == {}:
            for method,arguments in phrase_data["actions"].items():
                args = []
                args.append(self.args)
                if arguments != []:
                    args.append(arguments)
                    result = method(args) #execute action
                result = method(args) #execute action
                if type(result) == str:
                    return result
            self.args = None
            if type(result) != str:
                return True #True if passed ALL checks, False if failed at least one, i.e. needs to be restarted, "abort" if needs to be halted
        else:
            for method,arguments in phrase_data["checks"].items():
                args = []
                args.append(self.args)
                if arguments != []:
                    args.append(arguments)
                if method(args) != True:
                    self.args = None
                    return method(args)
            for method,arguments in phrase_data["actions"].items():
                args = []
                args.append(self.args)
                if arguments != []:
                    args.append(arguments)
                    result = method(args) #execute action
                result = method(args) #execute action
                if type(result) == str:
                    return result
            self.args = None
            if type(result) != str:
                return True #True if passed ALL checks, False if failed at least one, i.e. needs to be restarted, "abort" if needs to be halted

    def phrase_show(self, phrase_data):
        if phrase_data["checks"] == {}:
            if type(phrase_data["string"]) == str:
                print(phrase_data["string"])
            elif type(phrase_data["string"]) == dict:
                for method,arguments in phrase_data["string"].items():
                    if arguments != []:
                        print(method(arguments))
                    else:
                        print(method())
            return True
        else:
            for method,arguments in phrase_data["checks"].items():
                if arguments != []:
                    if type(method(arguments)) == str:
                        if method(arguments) != "abort":
                            print(method(arguments))
                        return "abort"
                else:
                    if type(method()) == str:
                        if method() != "abort":
                            print(method())
                        return "abort"
            
            if type(phrase_data["string"]) == str:
                print(phrase_data["string"])
            elif type(phrase_data["string"]) == dict:
                for method,arguments in phrase_data["string"].items():
                    if arguments != []:
                        print(method(arguments))
                    else:
                        print(method())

    def args_dummy(self, *args):
        self.phrase_started = True
        self.args = []
        for k in args:
            self.args.append(k) #saves user input

class Translate:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    DEFAULT = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    def translate_string(self,string:str,st_color=None,end_color=None, mode=None):
        string = str(string).strip().lower()
        local = None
        local_def = None
        if self.__class__.__name__ == "InputManager":
            local = self.localization[0]
            local_def = self.localization[0]
            if type(mode) == int and mode < len(self.modules):
                local = self.localization[int(mode) + 1]
            elif type(self.module_chosen) == int and self.module_chosen < len(self.modules):
                local = self.localization[self.module_chosen + 1]
        else:
            local = self.parent.localization[0]
            local_def = self.parent.localization[0]
            if type(mode) == int and mode < len(self.parent.modules):
                local = self.parent.localization[int(mode) + 1]
            elif type(self.parent.module_chosen) == int and self.parent.module_chosen < len(self.parent.modules):
                local = self.parent.localization[self.parent.module_chosen + 1]
        colors = {'header':'\033[95m',
                  'blue':'\033[94m',
                  'cyan':'\033[96m',
                  'green':'\033[92m',
                  'yellow':'\033[93m',
                  'red':'\033[91m',
                  'default':'\033[0m',
                  'bold':'\033[1m',
                  'underline':'\033[4m'}
        return_string = ""
        if st_color and st_color in colors.keys():
            return_string += colors[st_color]
        if local.find(string) != None and local.find(string).attrib['text'] != None:
            return_string += local.find(string).attrib['text']
        elif local_def.find(string) != None and local_def.find(string).attrib['text'] != None:
            return_string += local_def.find(string).attrib['text']
        else:
            if local_def.find("local_not_found_1") and local_def.find("local_not_found_2"):
                print(f"{colors['yellow']}{local.find('local_not_found_1').attrib['text']} {colors['red']}{string}{colors['yellow']} {local.find('local_not_found_2').attrib['text']}{colors['green']}")
            else:
                print(f"{colors['yellow']}Item {colors['red']}{string}{colors['yellow']} not found in the XML-file!{colors['green']}")
            return_string += string
        if end_color and end_color in colors.keys():
            return_string += colors[end_color]
        return return_string

class DataSaver:
    def update_json_file(self,data:dict):
        from datetime import datetime
        import json
        from pathlib import Path
        file = Path('storage/data.json')
        file_contents = {}
        if not file.exists():
            with open(file, 'w') as storage:
                pass
        else:
            if file.stat().st_size != 0:
                with open(file, 'r') as storage:
                    file_contents = json.load(storage)

        file_contents[str(datetime.now())] = data
        with open(file, 'w') as storage:
            json.dump(file_contents,storage, indent=2)

        return file_contents

class Utils(DataSaver, IdFormat, DialogueConstructor):
    def dialogue_check(self,variable):
        variable = self.single_param(variable)
        if not variable.lower() in self.parent.deny:
            return True
        return False

    def single_param(self, param):
        return param[0][0]
