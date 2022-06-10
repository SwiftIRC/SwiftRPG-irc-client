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

        headers = {'Authorization': 'Bearer {}'.format(os.getenv('API_TOKEN'))}

        response = requests.post("https://rpg.swiftirc.net/api/auth", data={'name': username, 'password': password}, verify=self.ssl_verify, headers=headers)

        if response.status_code == 200:
            self.auth[nick] = {'character': username}
            return True
        return False

    def check(self, nick):
        return (True if '{}'.format(nick) in self.auth else False)

    def logout(self, nick):
        del self.auth[nick]

    def rename(self, nick, newnick):
        self.auth[newnick] = self.auth[nick]
        del self.auth[nick]