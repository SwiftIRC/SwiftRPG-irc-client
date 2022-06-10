#!/usr/bin/env python3

import math
import time

class Game:
    def __init__(self):
        pass

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

    async def command(self, command, target, author, message):
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
            pass
        elif message[1:] == 'steal':
            pass
        elif message[1:] == 'pilfer':
            pass
        elif message[1:] == 'plunder':
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
