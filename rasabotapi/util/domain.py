
import os
import yaml
from dotenv import load_dotenv

from util.names import Names
from util.names import SLOTSTYPES

load_dotenv(dotenv_path=".env")

class DomainManager():

    def read(self):
        with open(os.getenv("DOMAIN"), 'r') as file:
            return yaml.load(file)
        
    def write(self, content):
        with open(os.getenv("DOMAIN"), 'w') as file:
            file.write(yaml.dump(content))

    def list_intentions(self):
        return self.read()[Names.INTENTS]

    def post_intent(self, intent):
        new_yaml = self.read()
        new_yaml[Names.INTENTS].append(intent)
        self.write(new_yaml)
        return intent
    
    def delete_intent(self, intent):
        new_yaml = self.read()
        del(new_yaml[Names.INTENTS][new_yaml[Names.INTENTS].index(intent)])
        self.write(new_yaml)
        return intent

    def list_slots(self, by_type=None):

        if by_type:
            slots_list = self.read()[Names.SLOTS]
            result = {slot_name: [] for slot_name in SLOTSTYPES.array}
            for slots_list_name, slots_list_items in slots_list.items():
                slots_list_items["name"] = slots_list_name
                result[slots_list_items["type"]].append(slots_list_items)

            if by_type == Names.SLOT_ALL_TYPES:
                return result

            return {by_type: result[by_type]}

        return list(self.read()[Names.SLOTS].keys())

    def get_slot(self, slot):
        return self.read()[Names.SLOTS][slot]
    
    def post_slot(self, slot, slot_content):
        new_yaml = self.read()
        new_yaml[Names.SLOTS][slot] = {k:v for k,v in slot_content.items() if not v == ""}
        self.write(new_yaml)
        return slot
    
    def delete_slot(self, slot):
        new_yaml = self.read()
        del (new_yaml[Names.SLOTS][slot])
        self.write(new_yaml)
        return slot
    
    def put_slot(self, slot, new_slot, slot_content):
        new_yaml = self.read()
        old_slot_content = new_yaml[Names.SLOTS][slot]

        for slot_c, value in slot_content.items():
            if value == "" and slot_c in old_slot_content:
                del (old_slot_content[slot_c])
            else:
                old_slot_content[slot_c] = value

        new_yaml[Names.SLOTS][new_slot] = old_slot_content
        
        if slot != new_slot:
            del new_yaml[Names.SLOTS][slot]

        self.write(new_yaml)
        return new_slot

    def list_responses(self):
        return list(self.read()[Names.RESPONSES].keys())

    def get_responses(self, response):
        return self.read()[Names.RESPONSES][response]

    def post_responses(self, response, content=None):
        new_yaml = self.read()

        if not response in new_yaml[Names.RESPONSES]:
            new_yaml[Names.RESPONSES][response] = list()
        if content:
            new_yaml[Names.RESPONSES][response].append({"text": content})
        self.write(new_yaml)
        return content

    def delete_responses(self, response, text=None):
        new_yaml = self.read()

        if not text:
            del new_yaml[Names.RESPONSES][response]
        else:
            index = list(map(lambda x : x['text']==text, new_yaml[Names.RESPONSES][response])).index(True)
            del new_yaml[Names.RESPONSES][response][index]

        self.write(new_yaml)
        return response

    def put_responses(self, response, new_response, old_text=None, new_text=None):
        new_yaml = self.read()
        old_responses_content = new_yaml[Names.RESPONSES][response]
        for r in old_responses_content:
            if r["text"] == old_text:
                r['text'] = new_text
                
        new_yaml[Names.RESPONSES][new_response] = old_responses_content
        
        if response != new_response:
            del new_yaml[Names.RESPONSES][response]

        self.write(new_yaml)
        return old_responses_content
