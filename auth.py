#!/usr/bin/env python3

import requests
import os


class Auth:
    auth = {}
    ssl_verify = True

    def __init__(self):
        if os.getenv('SSL_VERIFY'):
            self.ssl_verify = bool(int(os.getenv('SSL_VERIFY')))

    def login(self, nick, username, password):
        if '{}'.format(nick) in self.auth and self.auth[nick]['character'].lower() == username.lower():
            return True

        headers = {'X-Bot-Token': os.getenv('API_TOKEN')}

        response = requests.post("{}/api/auth".format(os.getenv('HOSTNAME')),
                                 data={'name': username, 'password': password},
                                 verify=self.ssl_verify,
                                 headers=headers)

        if response.status_code == 200:
            self.auth[nick] = {'character': username,
                               'token': response.json().get('token', '')}
            return True
        return False

    def check(self, nick):
        return (True if '{}'.format(nick) in self.auth else False)

    def logout(self, nick):
        del self.auth[nick]

    def rename(self, nick, newnick):
        self.auth[newnick] = self.auth[nick]
        del self.auth[nick]

    async def get_character(self, nick):
        return self.auth.get(nick, {}).get('character', None)

    async def get_token(self, nick):
        return self.auth.get(nick, {}).get('token', None)
