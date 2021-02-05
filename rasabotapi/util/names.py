
class Names:

    INTENTS = "intents"
    INTENT = "intent"
    NEW_INTENT = "new_intent"
    SYNONYMS = "synonym"
    LOOKUP = "lookup"
    EXAMPLES = "examples"
    EXAMPLE = "example"
    NEW_EXAMPLE = "new_example"
    TTYPES = "ttype"
    SENDER = "sender"
    TEXT = "text"
    NEW_TEXT = "new_text"
    MESSAGE = "message"
    SLOTS = "slots"
    NEW_SLOTS = "new_slot"
    SLOT_CONTENT = "slot_content"
    SLOT_ALL_TYPES = "all"
    SLOT_ANY = "any"
    SLOT_TEXT = "text"
    SLOT_BOOL = "bool"
    SLOT_CATEGORICAL = "categorical"
    SLOT_FLOAT = "float"
    SLOT_LIST = "list"
    SLOT_UNFEATURIZED = "unfeaturized"
    SLOT_VALUE_INFLUANCE_CONVERSATION = "influence_conversation"
    SLOT_VALUE_TYPE = "type"
    SLOT_VALUE_INITIAL_VALUE = "initial_value"
    SLOT_VALUE_AUTO_FILL = "auto_fill"
    SLOT_VALUE_MIN_VALUE = "min_value"
    SLOT_VALUE_MAX_VALUE = "max_value"
    SLOT_VALUE_VALUES = "values"
    RESPONSE = "response"
    RESPONSES = "responses"
    NEW_RESPONSE = "new_response"

class Iterator:

    array = []

    def __init__(self):
        self.cursor = 0
        self.size = len(self.array)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cursor == self.size:
            raise StopIteration
        
        elt = self.array[self.cursor]
        self.cursor += 1
        return elt

    def enum(self):
        return self.array

class TTYPES(Iterator):
    array = [Names.INTENT, Names.SYNONYMS, Names.LOOKUP]

class SLOTSTYPES(Iterator):
    array = [Names.SLOT_ANY, Names.SLOT_TEXT, Names.SLOT_BOOL, Names.SLOT_CATEGORICAL, Names.SLOT_FLOAT, Names.SLOT_LIST, Names.SLOT_UNFEATURIZED]

    def verify(self, slot_name, payload):

        if slot_name == Names.SLOT_CATEGORICAL:
            return Names.SLOT_VALUE_VALUES in payload and type(payload[Names.SLOT_VALUE_VALUES]) == list

        return True

    def blueprint(self, slot_name):

        blueprint = [
            {"name": Names.SLOT_VALUE_INFLUANCE_CONVERSATION, "choices":[True, False]},
            {"name": Names.SLOT_VALUE_TYPE, "choices":[slot_name]},
            {"name": Names.SLOT_VALUE_INITIAL_VALUE},
            {"name": Names.SLOT_VALUE_AUTO_FILL, "choices":[True, False]}
        ]
        

        if slot_name == Names.SLOT_FLOAT:
            blueprint.extend([
                {"name": Names.SLOT_VALUE_MIN_VALUE, "type":"float"},
                {"name": Names.SLOT_VALUE_MAX_VALUE, "type":"float"},
            ])
        
        elif slot_name == Names.SLOT_CATEGORICAL:
            blueprint.extend([
                {"name": Names.SLOT_VALUE_VALUES, "type":"list"},
            ])

        return blueprint

    def __is_float(self, x):
        try:
            float(x)
        except:
            return False
        return True

    def clear_key(self, key, payload):
        value = payload[key] if key in payload and payload[key] is not None else None
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif self.__is_float(value):
            return float(value)
        elif value.isdigit():
            return int(value)
        elif value == "":
            return None
        return value

    def clear_float(self, key, payload):
        value = self.clear_key(key, payload)
        if value:
            try:
                return {key: float(value)}
            except ValueError as e:
                raise ValueError( f"{str(e)} for variable {key}")

        return dict()

    def clear_categorical(self, key, payload):
        return self.clear_key(key, payload) or payload[key]

    def clear(self, payload, slot_type=None, all_optional=False):
        result = dict()
        
        slot_type = self.clear_key(Names.SLOT_VALUE_TYPE, payload) or slot_type
        if not all_optional:
            if slot_type is None:
                raise KeyError(f"Missing slot value {Names.SLOT_VALUE_TYPE}")
            elif not slot_type in self.array:
                raise ValueError(f"Wrong value of slot {Names.SLOT_VALUE_TYPE}")
        
        if not slot_type is None and slot_type in self.array:
            result[Names.SLOT_VALUE_TYPE] = slot_type

        value = self.clear_key(Names.SLOT_VALUE_INFLUANCE_CONVERSATION, payload)
        if not all_optional and value is None:
            raise KeyError(f"Missing slot value {Names.SLOT_VALUE_INFLUANCE_CONVERSATION}")
        
        if not value is None:
            result[Names.SLOT_VALUE_INFLUANCE_CONVERSATION] = value

        for generic_slots_value in [Names.SLOT_VALUE_INITIAL_VALUE, Names.SLOT_VALUE_AUTO_FILL]:
            value = self.clear_key(generic_slots_value, payload)
            if not value is None:
                result[generic_slots_value] = value
        
        if slot_type == Names.SLOT_FLOAT:
            for generic_slots_value in [Names.SLOT_VALUE_MIN_VALUE, Names.SLOT_VALUE_MAX_VALUE]:
                result.update(self.clear_float(generic_slots_value, payload))

        elif slot_type == Names.SLOT_CATEGORICAL and Names.SLOT_VALUE_VALUES in payload:
            value = self.clear_categorical(Names.SLOT_VALUE_VALUES, payload)
            if not value is None:
                result[Names.SLOT_VALUE_VALUES] = list(value)
        
        return result

        