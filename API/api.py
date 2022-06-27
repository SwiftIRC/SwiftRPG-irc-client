import json
import os
from types import FunctionType
import requests
import string


# The `target` parameter can be either a string (from IRC) or a function (from Discord)


async def post(self, command: FunctionType, target, token: string, endpoint: string, data={}):
    headers = {'Authorization': 'Bearer {}'.format(token),
               'X-Bot-Token': os.getenv('API_TOKEN')}

    response = requests.post("{}/api/{}".format(os.getenv('HOSTNAME'), endpoint),
                             data=data,
                             verify=self.ssl_verify,
                             headers=headers,
                             allow_redirects=False)

    if response.status_code == 302:
        await self.process_response(command, target, "Error: user session expired. Please PM the bot `.logout` and then log back in.")
    elif response.status_code == 403:
        await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown')))
    elif response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            print("ERROR: api.py [29]: ", response.text)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [02]')))
        except Exception as e:
            print("ERROR: api.py [32]: ", e)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [03]')))
    else:
        print("ERROR: api.py [35]: ",
              response.status_code, response.text)


async def get(self, command: FunctionType, target, token: string, endpoint: string):
    headers = {'Authorization': 'Bearer {}'.format(token),
               'X-Bot-Token': os.getenv('API_TOKEN')}

    response = requests.get("{}/api/{}".format(os.getenv('HOSTNAME'), endpoint),
                            verify=self.ssl_verify,
                            headers=headers,
                            allow_redirects=False)

    if response.status_code == 302:
        await self.process_response(command, target, "Error: user session expired. Please PM the bot `.logout` and then log back in.")
    elif response.status_code == 403:
        await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown')))
    elif response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            print("ERROR: api.py [56]: ", response.text)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [04]')))
        except Exception as e:
            print("ERROR: api.py [59]: ", e)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [05]')))
    else:
        print("ERROR: api.py [62]: ",
              response.status_code, response.text)
