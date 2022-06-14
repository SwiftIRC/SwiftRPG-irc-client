import os
import requests


async def post(self, command, target, token, endpoint, data={}):
    headers = {'Authorization': 'Bearer {}'.format(token),
               'X-Bot-Token': os.getenv('API_TOKEN')}

    response = requests.post("{}/api/{}".format(os.getenv('HOSTNAME'), endpoint),
        data=data,
        verify=self.ssl_verify,
        headers=headers)

    if response.status_code == 419:
        await self.process_response(command, target, "Error: user session expired")
    elif response.status_code == 403:
        print(response.text)
        await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown')))
    elif response.status_code == 200:
        return response.json()
    else:
        print("ERROR: game.py [145]: ",
              response.status_code, response.text)


async def get(self, command, target, token, endpoint):
    headers = {'Authorization': 'Bearer {}'.format(token),
        'X-Bot-Token': os.getenv('API_TOKEN')}

    response = requests.get("{}/api/{}".format(os.getenv('HOSTNAME'), endpoint),
        verify=self.ssl_verify,
        headers=headers)

    if response.status_code == 419:
        await self.process_response(command, target, "Error: user session expired")
    elif response.status_code == 403:
        print(response.text)
        await self.process_response(command, target, "Error: {}".format(response.json().get('error', 'unknown')))
    elif response.status_code == 200:
        return response.json()
    else:
        print("ERROR: game.py [164]: ",
              response.status_code, response.text)
