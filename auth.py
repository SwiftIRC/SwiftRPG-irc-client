#!/usr/bin/env python3

import string
import requests
import os

import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class Auth:
    auth = {}
    ssl_verify = True

    def __init__(self):
        if os.getenv('SSL_VERIFY'):
            self.ssl_verify = bool(int(os.getenv('SSL_VERIFY')))
        self.read_cache()

    def get_cipher(self):
        token = bytes(os.getenv('API_TOKEN'), 'latin-1')

        key = (token * 16)[:32]
        iv = key[:16]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=default_backend())

        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()

        return encryptor, decryptor

    def write_cache(self):
        filename = os.getenv('CACHE_FILE', '.cache')
        encryptor, _ = self.get_cipher()

        with open(filename, 'wb') as f:
            JSON = json.dump(self.auth)
            encrypted_json = (encryptor.update(JSON) +
                              encryptor.finalize()).decode('latin-1')
            encrypted_bytes = bytes(encrypted_json, 'latin-1')
            f.write(encrypted_bytes)

    def read_cache(self):
        filename = os.getenv('CACHE_FILE', '.cache')
        _, decryptor = self.get_cipher()

        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                encrypted_bytes = f.read()
                encrypted_json = decryptor.update(
                    encrypted_bytes) + decryptor.finalize()
                JSON = encrypted_json.decode('latin-1')
                self.auth = json.loads(JSON)

    def login(self, nick: string, username: string, password: string):
        if '{}'.format(nick) in self.auth and self.auth[nick]['character'].lower() == username.lower():
            return True

        headers = {'X-Bot-Token': os.getenv('API_TOKEN')}

        response = requests.post("{}/api/auth".format(os.getenv('HOSTNAME')),
                                 data={'name': username,
                                       'password': password},
                                 verify=self.ssl_verify,
                                 headers=headers)

        if response.status_code == 200:
            self.auth[nick] = {'character': username,
                               'token': response.json().get('token', '')}
            self.write_cache()
            return True
        return False

    def check(self, nick):
        return (True if '{}'.format(nick) in self.auth else False)

    def logout(self, nick):
        del self.auth[nick]
        self.write_cache()

    def rename(self, nick, newnick):
        self.auth[newnick] = self.auth[nick]
        del self.auth[nick]
        self.write_cache()

    async def get_character(self, nick):
        return self.auth.get(nick, {}).get('character', None)

    async def get_token(self, nick):
        return self.auth.get(nick, {}).get('token', None)
