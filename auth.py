#!/usr/bin/env python3

import requests

class Auth:
    auth = {}

    def __init__(self):
        pass

    def login(self, nick, username, password):
        if '{}'.format(nick) in self.auth and self.auth[nick]['character'].lower() == username.lower():
            return True
        response = requests.post("https://rpg.swiftirc.net/me", data={'name': username, 'password': password}, verify=False)
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