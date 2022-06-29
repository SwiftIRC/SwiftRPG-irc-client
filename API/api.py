import json
import os
from types import FunctionType
import requests
import string


# The `target` parameter can be either a string (from IRC) or a function (from Discord)
async def post(self, command: FunctionType, target, token: string, endpoint: string, data={}):
    headers = {'Authorization': 'Bearer {}'.format(token),
               'X-Bot-Token': os.getenv('API_TOKEN')}

    try:
        response = requests.post("{}/api/{}".format(os.getenv('HOSTNAME'), endpoint),
                                 data=data,
                                 verify=self.ssl_verify,
                                 headers=headers,
                                 allow_redirects=False)
    except requests.exceptions.SSLError:
        await self.process_response(command, target, "Error: encountered an SSL error!")
        return
    except requests.exceptions.ConnectionError:
        await self.process_response(command, target, "Error: connection error. Please try again in a few minutes.")
        return

    if response.status_code == 302:
        await self.process_response(command, target, "Error: user session expired. Please PM the bot `.logout` and then log back in.")
    elif response.status_code == 403:
        await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown')))
    elif response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            print("ERROR: api.py [01]: ", response.text)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [02]')))
        except Exception as e:
            print("ERROR: api.py [02]: ", e)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [03]')))
    else:
        print("ERROR: api.py [03]: ",
              response.status_code, response.text)


async def get(self, command: FunctionType, target, token: string, endpoint: string):
    headers = {'Authorization': 'Bearer {}'.format(token),
               'X-Bot-Token': os.getenv('API_TOKEN')}

    try:
        response = requests.get("{}/api/{}".format(os.getenv('HOSTNAME'), endpoint),
                                verify=self.ssl_verify,
                                headers=headers,
                                allow_redirects=False)
    except requests.exceptions.SSLError:
        await self.process_response(command, target, "Error: encountered an SSL error.")
        return
    except requests.exceptions.ConnectionError:
        await self.process_response(command, target, "Error: connection error. Please try again in a few minutes.")
        return

    if response.status_code == 302:
        await self.process_response(command, target, "Error: user session expired. Please PM the bot `.logout` and then log back in.")
    elif response.status_code == 403:
        await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown')))
    elif response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            print("ERROR: api.py [04]: ", response.text)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [04]')))
        except Exception as e:
            print("ERROR: api.py [05]: ", e)
            await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown [05]')))
    else:
        print("ERROR: api.py [06]: ",
              response.status_code, response.text)
