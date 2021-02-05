
import os
import yaml
from dotenv import load_dotenv

from util.names import Names
from util.names import TTYPES

load_dotenv(dotenv_path=".env")

class NluManager():

    def read(self):
        with open(os.getenv("NLU"), 'r') as file:
            ytext = yaml.load(file)
        
        result = {
            "version": ytext["version"], 
            "nlu": {ttype: {} for ttype in TTYPES()}
        }

        for elt in ytext['nlu']:
            for ttype in TTYPES():
                if ttype in elt:
                    key = elt[ttype]
                    examples = list(map(lambda x : x[2:] ,elt['examples'].split("\n")))[:-1]
                    result['nlu'][ttype][key] = examples

        return result

    def write(self, content):
        with open(os.getenv("NLU"), 'w') as file:
            file.write(f"version: {content['version']}\n")
            file.write("nlu:\n")
            for ttype in TTYPES():
                for key, examples in content['nlu'][ttype].items():
                    file.write(f"- {ttype}: {key}\n  examples: |\n")
                    for example in examples:
                        file.write(f"    - {example}\n")
                file.write("\n")

    def post_intent(self, ttype, intent, examples=[]):

        if type(examples) == str:
            examples = [examples]

        new_yaml = self.read()
        new_yaml['nlu'][ttype][intent] = examples
        self.write(new_yaml)
    
    def delete_intent(self, ttype, intent):

        new_yaml = self.read()
        old = new_yaml['nlu'][ttype][intent]
        del(new_yaml['nlu'][ttype][intent])
        self.write(new_yaml)
        return old

    def list_intent_text(self, ttype, intent=None):

        new_yaml = self.read()
        return new_yaml['nlu'][ttype][intent]  if intent else list(new_yaml['nlu'][ttype].keys())

    def post_intent_text(self, ttype, intent, example):

        new_yaml = self.read()
        new_yaml['nlu'][ttype][intent].append(example)
        self.write(new_yaml)
        return example

    def delete_intent_text(self, ttype, intent, examples):

        if type(examples) == str:
            examples = [examples]
        
        new_yaml = self.read()
        old_examples = new_yaml['nlu'][ttype][intent]
        for example in examples:
            index = old_examples.index(example)
            del (old_examples[index])
        
        new_yaml['nlu'][ttype][intent] = old_examples
        self.write(new_yaml)
        return examples

    def put_intent_text(self, ttype, intent, example, new_example):
        
        new_yaml = self.read()
        old_examples = new_yaml['nlu'][ttype][intent]
        index = old_examples.index(example)
        old_examples[index] = new_example
        new_yaml['nlu'][ttype][intent] = old_examples
        self.write(new_yaml)
        return new_example