
from flask import Flask
from flask_cors import CORS
from flask_restplus import Resource, Api, fields

from util.nlu import NluManager
from util.chat import ChatManager
from util.domain import DomainManager

from util.names import *

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={"/*": {"origins": "*"}})

api_namespace_nlu = api.namespace('nlu', description="")
api_namespace_names = api.namespace('names', description='Some constantes')
api_namespace_chat = api.namespace('chat', description='Tchat with your bot')
api_namespace_texts = api.namespace('texts', description='Intentions managements on domain and nlu')
api_namespace_slots = api.namespace('slots', description='slots on domain')
api_namespace_responses = api.namespace('responses', description="responses on domain")

api_model_chat = api.model(
    "POST chat", {
        Names.SENDER: fields.String(description=Names.SENDER),
        Names.MESSAGE: fields.String(description=Names.MESSAGE),
    }
)

api_model_payload_examples = api.model(
    "When you need to add one example on the payload", {
        Names.EXAMPLES: fields.String(description="one exemple (facultative)", required=False, default=None)
    }
)

api_model_put = api.model(
    "PUT intent", {
        Names.NEW_INTENT: fields.String(description="the new intent")
    }
)

api_model_put_text = api.model(
    "PUT intent text", {
        Names.EXAMPLE: fields.String(description="single exemple"),
        Names.NEW_EXAMPLE: fields.String(description="single exemple")
    }
)

api_model_slot_content = api.model(
    "api_model_slot_content", {
        Names.SLOT_VALUE_INFLUANCE_CONVERSATION: fields.Boolean(description=Names.SLOT_VALUE_INFLUANCE_CONVERSATION),
        Names.SLOT_VALUE_INITIAL_VALUE: fields.String(description=Names.SLOT_VALUE_INITIAL_VALUE),
        Names.SLOT_VALUE_AUTO_FILL: fields.Boolean(description=Names.SLOT_VALUE_AUTO_FILL),
        Names.SLOT_VALUE_MIN_VALUE: fields.Float(description=Names.SLOT_VALUE_MIN_VALUE),
        Names.SLOT_VALUE_MAX_VALUE: fields.Float(description=Names.SLOT_VALUE_MAX_VALUE),
        Names.SLOT_VALUE_VALUES: fields.String(description="list of categories"),
        Names.SLOT_VALUE_TYPE: fields.String(description=Names.SLOT_VALUE_TYPE)
    }
)

api_model_put_slot_content = api.model(
    "api_model_put_slot_content", {
        Names.NEW_SLOTS: fields.String(description=Names.NEW_SLOTS),
        Names.SLOT_VALUE_INFLUANCE_CONVERSATION: fields.Boolean(description=Names.SLOT_VALUE_INFLUANCE_CONVERSATION),
        Names.SLOT_VALUE_INITIAL_VALUE: fields.String(description=Names.SLOT_VALUE_INITIAL_VALUE),
        Names.SLOT_VALUE_AUTO_FILL: fields.Boolean(description=Names.SLOT_VALUE_AUTO_FILL),
        Names.SLOT_VALUE_MIN_VALUE: fields.Float(description=Names.SLOT_VALUE_MIN_VALUE),
        Names.SLOT_VALUE_MAX_VALUE: fields.Float(description=Names.SLOT_VALUE_MAX_VALUE),
        Names.SLOT_VALUE_VALUES: fields.String(description="list of categories"),
        Names.SLOT_VALUE_TYPE: fields.String(description=Names.SLOT_VALUE_TYPE)
    }
)

api_model_responses_content = api.model(
    "api_model_responses_content", {
        Names.TEXT: fields.String(description=Names.TEXT)
    }
)

api_model_put_responses_content = api.model(
    "api_model_put_responses_content", {
        Names.NEW_TEXT: fields.String(description=Names.NEW_TEXT),
        Names.TEXT: fields.String(description=Names.TEXT)
    }
)

@api_namespace_chat.route('/')
class Chat(Resource):

    @api_namespace_chat.response(200, 'ok')
    @api.expect(api_model_chat)
    def post(self):
        sender = api.payload[Names.SENDER]
        message = api.payload[Names.MESSAGE]
        return ChatManager().post(sender=sender, message=message)

@api_namespace_names.route('/ttypes/')
class Ttypes(Resource):

    @api_namespace_names.response(200, 'ok')
    def get(self): ## act like a list
        return {"ttypes": TTYPES().enum()}, 200

@api_namespace_nlu.route('/')
class Intentions(Resource):
    
    @api_namespace_nlu.response(200, 'ok')
    def get(self): ## act like a list
        return {Names.INTENT: DomainManager().list_intentions()}, 200

@api_namespace_nlu.route('/<string:ttype>/<string:intent>')
class Intentions(Resource):
    @api_namespace_nlu.response(200, 'ok')
    @api.expect(api_model_payload_examples)
    def post(self, ttype, intent):
        examples = api.payload[Names.EXAMPLES] if Names.EXAMPLES in api.payload else list()
        
        if ttype == Names.INTENT:
            DomainManager().post_intent(intent)
        
        NluManager().post_intent(ttype=ttype, intent=intent, examples=examples)
        return {Names.INTENT: intent}, 201

    @api_namespace_nlu.response(200, 'ok')
    @api_namespace_nlu.response(404, 'do not exists')
    def delete(self, ttype, intent):

        try:
            if ttype == Names.INTENT:
                DomainManager().delete_intent(intent)

            old = NluManager().delete_intent(ttype=ttype, intent=intent)

        except ValueError as e:
            return str(e), 404

        return {intent: old}, 200

    @api_namespace_nlu.response(200, 'ok')
    @api_namespace_nlu.response(404, 'do not exists')
    @api.expect(api_model_put)
    def put(self, ttype, intent):
        new_intent = api.payload[Names.NEW_INTENT]

        try:
            if ttype == Names.INTENT:
                DomainManager().delete_intent(intent)
                DomainManager().post_intent(new_intent)

            old = NluManager().delete_intent(ttype=ttype, intent=intent)
            NluManager().post_intent(ttype=ttype, intent=new_intent, examples=old)

        except ValueError as e:
            return str(e), 404

        return {Names.NEW_INTENT: new_intent}, 200

@api_namespace_texts.route('/<string:ttype>')
class IntentionTtypes(Resource):

    @api_namespace_texts.response(200, 'ok')
    def get(self, ttype): ## act like a list
        return {ttype: NluManager().list_intent_text(ttype=ttype)}, 200

@api_namespace_texts.route('/<string:ttype>/<string:intent>')
class IntentionIntents(Resource):

    @api_namespace_texts.response(200, 'ok')
    def get(self, ttype, intent): ## act like a list
        return {intent: NluManager().list_intent_text(ttype=ttype, intent=intent)}, 200

    @api_namespace_texts.response(200, 'ok')
    @api.expect(api_model_payload_examples)
    def post(self, ttype, intent):
        example = api.payload[Names.EXAMPLES] if Names.EXAMPLES in api.payload else list()
        
        new = NluManager().post_intent_text(ttype=ttype, intent=intent, example=example)
        return {intent: new}, 201

    @api_namespace_texts.response(200, 'ok')
    @api_namespace_texts.response(404, 'do not exists')
    @api.expect(api_model_payload_examples)
    def delete(self, ttype, intent):
        print(api.payload)
        examples = api.payload[Names.EXAMPLES]

        try:
            old = NluManager().delete_intent_text(ttype=ttype, intent=intent, examples=examples)
        except ValueError as e:
            return str(e), 404

        return {intent: old}, 201

    @api_namespace_texts.response(200, 'ok')
    @api_namespace_texts.response(404, 'do not exists')
    @api.expect(api_model_put_text)
    def put(self, ttype, intent):
        old_example = api.payload[Names.EXAMPLE]
        new_example = api.payload[Names.NEW_EXAMPLE]
        
        try:
            NluManager().put_intent_text(ttype=ttype, intent=intent, example=old_example, new_example=new_example)
        except ValueError as e:
            return str(e), 404

        return {intent: new_example}, 200

@api_namespace_names.route('/slots/')
class Slotstypes(Resource):

    @api_namespace_names.response(200, 'ok')
    def get(self): ## act like a list
        return {"slots": SLOTSTYPES().enum()}, 200

@api_namespace_names.route('/slots/<string:slottype>')
class SlotstypesBlueprint(Resource):

    @api_namespace_names.response(200, 'ok')
    def get(self, slottype): ## act like a list
        return {"slots": SLOTSTYPES().blueprint(slottype)}, 200

@api_namespace_slots.route('/')
class Slots(Resource):

    @api_namespace_slots.response(200, 'ok')
    def get(self): ## act like a list
        return {Names.SLOTS: DomainManager().list_slots()}, 200

@api_namespace_slots.route('/<string:slottype>')
class SlotsByTypes(Resource):

    @api_namespace_slots.response(200, 'ok')
    def get(self, slottype): ## act like a list
        return {Names.SLOTS: DomainManager().list_slots(by_type=slottype)}, 200

@api_namespace_slots.route('/<string:slots>')
class SlotsSlots(Resource):

    @api_namespace_slots.response(200, 'ok')
    def get(self, slots):
        return {slots: DomainManager().get_slot(slot=slots)}, 200

    @api_namespace_slots.response(200, 'ok')
    @api.expect(api_model_slot_content)
    def post(self, slots):
        slot_content = api.payload

        if SLOTSTYPES().verify(slot_name=slots, payload=slot_content):

            try:
                slot_content = SLOTSTYPES().clear(slot_content)
            except Exception as e:
                return {"message": str(e)}, 400
            
            new = DomainManager().post_slot(slot=slots, slot_content=slot_content)
            return {slots: slot_content}, 201

        return {"message": "Required slots for this slots are missing"}, 400

    @api_namespace_slots.response(200, 'ok')
    @api_namespace_slots.response(404, 'do not exists')
    def delete(self, slots):
            
        new = DomainManager().delete_slot(slot=slots)
        return {Names.SLOTS: slots}, 201

    @api_namespace_slots.response(200, 'ok')
    @api_namespace_slots.response(404, 'do not exists')
    @api.expect(api_model_put_slot_content)
    def put(self, slots):
        slot_content = api.payload
        new_slot = api.payload[Names.NEW_SLOTS] if Names.NEW_SLOTS in api.payload else slots
        slot_type = DomainManager().get_slot(slot=slots)[Names.SLOT_VALUE_TYPE]

        if SLOTSTYPES().verify(slot_name=slots, payload=slot_content):
            try:
                slot_content = SLOTSTYPES().clear(slot_content, slot_type=slot_type, all_optional=True)
            except Exception as e:
                return {"message": str(e)}, 400
            
            new = DomainManager().put_slot(slot=slots, new_slot=new_slot, slot_content=slot_content)
            return {slots:  slot_content}, 201

        return {"message": "Required slots for this slots are missing"}, 400

@api_namespace_responses.route('/')
class Responses(Resource):

    @api_namespace_responses.response(200, 'ok')
    def get(self): ## act like a list
        return {Names.RESPONSES: DomainManager().list_responses()}, 200

@api_namespace_responses.route('/<string:response>')
class ResponsesResponses(Resource):

    @api_namespace_responses.response(200, 'ok')
    @api.expect(api_model_responses_content)
    def post(self, response):
        content = api.payload 
        new = DomainManager().post_responses(response=response)
        return {Names.RESPONSE: response}, 201

    @api_namespace_responses.response(200, 'ok')
    @api_namespace_responses.response(404, 'do not exists')
    def delete(self, response):
        new = DomainManager().delete_responses(response=response)
        return {Names.RESPONSE: response}, 201

    @api_namespace_responses.response(200, 'ok')
    @api_namespace_responses.response(404, 'do not exists')
    @api.expect(api_model_put_responses_content)
    def put(self, response):
        content = api.payload
        new_response = content[Names.NEW_RESPONSE]
        new = DomainManager().put_responses(response=response, new_response=new_response)
        return {Names.RESPONSE:  new_response}, 201
        
@api_namespace_responses.route('/text/<string:response>')
class ResponsesResponsesText(Resource):    
    
    @api_namespace_responses.response(200, 'ok')
    def get(self, response):
        return {response: DomainManager().get_responses(response=response)}, 200

    @api_namespace_responses.response(200, 'ok')
    @api.expect(api_model_responses_content)
    def post(self, response):
        content = api.payload[Names.TEXT]
        new = DomainManager().post_responses(response=response, content=content)
        return {response: new}, 201

    @api_namespace_responses.response(200, 'ok')
    @api_namespace_responses.response(404, 'do not exists')
    @api.expect(api_model_responses_content)
    def delete(self, response):
        content = api.payload[Names.TEXT]
        new = DomainManager().delete_responses(response=response, text=content)
        return {Names.RESPONSE: response}, 201

    @api_namespace_responses.response(200, 'ok')
    @api_namespace_responses.response(404, 'do not exists')
    @api.expect(api_model_put_responses_content)
    def put(self, response):
        content = api.payload
        new_response = content[Names.RESPONSE] if Names.RESPONSE in content else response
        old_text = content[Names.TEXT] if Names.TEXT in content else None
        new_text = content[Names.NEW_TEXT]if Names.NEW_TEXT in content else None
        new = DomainManager().put_responses(response=response, new_response=new_response, old_text=old_text, new_text=new_text)
        return {response:  content}, 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=11000)