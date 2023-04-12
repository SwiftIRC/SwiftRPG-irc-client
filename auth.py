#!/usr/bin/env python3

import datetime
import json
import os
import requests
import string

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
            json_bytes = bytes(json.dumps(self.auth), 'utf-8')
            padding = (16 - len(json_bytes) % 16) * b' '
            encrypted_json = (encryptor.update(json_bytes + padding) +
                              encryptor.finalize()).decode('latin-1')
            encrypted_bytes = bytes(encrypted_json, 'latin-1')
            f.write(encrypted_bytes)

    def read_cache(self):
        filename = os.getenv('CACHE_FILE', '.cache')
        _, decryptor = self.get_cipher()

        try:
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    encrypted_bytes = f.read().strip()
                    encrypted_json = decryptor.update(
                        encrypted_bytes) + decryptor.finalize()
                    JSON = encrypted_json.decode('latin-1')
                    self.auth = json.loads(JSON)
        except json.decoder.JSONDecodeError as e:
            print(e)

    def login(self, nick: string, token: string):
        headers = {
            'X-Bot-Token': os.getenv('API_TOKEN'),
            'Authorization': 'Bearer {}'.format(token),
        }

        response = requests.get("{}/api/auth/token/login".format(os.getenv('API_HOSTNAME')),
                                verify=self.ssl_verify,
                                headers=headers)

        json = {'error': True}

        if response.status_code == 200:
            try:
                json = response.json()
            except:
                return json

            future = datetime.datetime.utcnow() + datetime.timedelta(days=7)

            self.auth[nick] = {'character': json.get('name', ''),
                               'token': json.get('token', ''),
                               'expiration': str(future)}
            self.write_cache()

        return json

    def register(self, username: string, password: string):
        headers = {'X-Bot-Token': os.getenv('API_TOKEN')}

        response = requests.post("{}/api/auth/register".format(os.getenv('API_HOSTNAME')),
                                 data={'name': username,
                                       'password': password,
                                       'password_confirmation': password},
                                 verify=self.ssl_verify,
                                 headers=headers)

        try:
            response.json()  # We execute this to test if the JSON is valid
            if response.status_code == 200:
                return True
            return False
        except json.decoder.JSONDecodeError:
            return False
        except:
            return False

    def check(self, nick):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=8)

        return (True if datetime.datetime.utcnow() - datetime.datetime.fromisoformat(self.auth.get(str(nick), {}).get('expiration', str(past))) < datetime.timedelta(days=7) else False)

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
