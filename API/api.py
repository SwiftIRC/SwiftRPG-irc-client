import json
import os
from types import FunctionType
import requests
import string


async def post(self, command: FunctionType, target, token: string, endpoint: string, data={}):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(token),
        'X-Bot-Token': os.getenv('API_TOKEN'),
    }

    try:
        response = requests.post("{}/api/{}".format(os.getenv('API_HOSTNAME'), endpoint),
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
    except Exception as e:
        await self.process_response(command, target, "Error: {}".format(e))
        return

    if response.status_code == 401:
        await self.process_response(command, target, "Error: user session expired. Please `.login` again.")
    elif response.status_code == 404:
        await self.process_response(command, target, "Error: 404 resource not found!")
    elif response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            print("ERROR: api.py [01]: ", response.text)
            await self.process_response(command, target, "Error: {} [02]".format(response.text))
        except Exception as e:
            print("ERROR: api.py [03]: ", e)
            await self.process_response(command, target, "Error: {} [04]".format(response.text))
    else:
        print("ERROR: api.py [05]: ",
              response.status_code, response.text)


async def get(self, command: FunctionType, target, token: string, endpoint: string):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(token),
        'X-Bot-Token': os.getenv('API_TOKEN')
    }

    try:
        response = requests.get("{}/api/{}".format(os.getenv('API_HOSTNAME'), endpoint),
                                verify=self.ssl_verify,
                                headers=headers,
                                allow_redirects=False)
    except requests.exceptions.SSLError:
        await self.process_response(command, target, "Error: encountered an SSL error.")
        return
    except requests.exceptions.ConnectionError:
        await self.process_response(command, target, "Error: connection error. Please try again in a few minutes.")
        return
    except Exception as e:
        await self.process_response(command, target, "Error: {}".format(e))
        return

    if response.status_code == 401:
        await self.process_response(command, target, "Error: user session expired. Please PM the bot `.login <username> <password>`.")
    elif response.status_code == 404:
        await self.process_response(command, target, "Error: 404 resource not found!")
    elif response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            print("ERROR: api.py [06]: ", response.text)
            await self.process_response(command, target, "Error: {} [07]".format(response.text))
        except Exception as e:
            print("ERROR: api.py [08]: ", e)
            await self.process_response(command, target, "Error: {} [09]".format(response.text))
    else:
        print("ERROR: api.py [10]: ",
              response.status_code, response.text)
