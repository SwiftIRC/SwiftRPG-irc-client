#!/usr/bin/env python3

import math
import os
import requests
import time


class Game:
    ssl_verify = True

    def __init__(self):
        if os.getenv('SSL_VERIFY'):
            self.ssl_verify = bool(int(os.getenv('SSL_VERIFY')))

    def start(self):
        while True:
            time.sleep(1)

    async def xp(self, level):
        return int(level + 10 * level ** 3)

    async def level(self, xp):
        total = 0
        for i in range(0, 101):
            if await self.xp(i) > xp:
                return i-1
        return 100

    async def process_response(self, command, target, response):
        if target != None:
            command(target, response)
        else:
            await command(response)

    async def command(self, auth, command, target, author, message):
        character = await auth.get_character(author)
        token = await auth.get_token(author)
        split = message.split()
        if message[1:] == 'foo':
            await self.process_response(command, target, "What's up, {}?".format(author))
        elif message[1:] == 'bar':
            await self.process_response(command, target, "Hello, {}!".format(author))
        elif split[0][1:] == 'xp':
            if len(split) != 2:
                await self.process_response(command, target, "Usage: {} <level>".format(split[0]))
                return
            xp = await self.xp(int(split[1]))
            await self.process_response(command, target, "Level {} is equivalent to {} XP".format(split[1], xp))
        elif split[0][1:] == 'level' or split[0][1:] == 'lvl':
            if len(split) != 2:
                await self.process_response(command, target, "Usage: {} <experience>".format(split[0]))
                return
            level = await self.level(int(split[1]))
            await self.process_response(command, target, "XP of {} is equivalent to level {}".format(split[1], level))
        # Thieving
        elif message[1:] == 'pickpocket':
            response = await self.http_post(
                command, target, token, 'thieving/pickpocket')
            if response:
                await self.process_response(command, target, "Thieving: {} - Gold: {}".format(response.get('thieving', 0), response.get('gold', 0)))
        elif message[1:] == 'steal':
            response = await self.http_post(
                command, target, token, 'thieving/steal')
            if response:
                await self.process_response(command, target, "Thieving: {} - Gold: {}".format(response.get('thieving', 0), response.get('gold', 0)))
        elif message[1:] == 'pilfer':
            response = await self.http_post(
                command, target, token, 'thieving/pilfer')
            if response:
                await self.process_response(command, target, "Thieving: {} - Gold: {}".format(response.get('thieving', 0), response.get('gold', 0)))
        elif message[1:] == 'plunder':
            response = await self.http_post(
                command, target, token, 'thieving/plunder')
            if response:
                await self.process_response(command, target, "Thieving: {} - Gold: {}".format(response.get('thieving', 0), response.get('gold', 0)))
            pass
        # Fishing
        elif message[1:] == "net":
            pass
        elif message[1:] == "lure":
            pass
        elif message[1:] == "angle":
            pass
        # Woodcutting
        elif message[1:] == "chop":
            pass
        # Mining
        elif message[1:] == "mine":
            pass
        # Smithing
        elif message[1:] == "smith":
            pass
        # Crafting
        elif message[1:] == "craft":
            pass
        # Cooking
        elif message[1:] == "cook":
            pass

    async def http_post(self, command, target, token, endpoint, data={}):
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
            print("ERROR: game.py [104]: ",
                  response.status_code, response.text)
