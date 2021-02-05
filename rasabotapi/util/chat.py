
import os
import json
import requests

from dotenv import load_dotenv
from util.names import Names

load_dotenv(dotenv_path=".env")

class ChatManager():

    def post(self, sender, message):

        data = {Names.SENDER: sender, Names.MESSAGE: message}
        headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}

        response = requests.post(
            url=os.getenv("CHAT"),
            headers=headers,
            data=json.dumps(data)
        )

        return json.loads(response.text), response.status_code

