#!/usr/bin/env python3

import time

class Game:
    def __init__(self):
        pass

    def start(self):
        while True:
            time.sleep(1)

    async def command(self, command, target, author, message):
        if message[1:] == 'foo':
            await self.process_response(command, target, "What's up, {}?".format(author))

    async def process_response(self, command, target, response):
        if target != None:
            command(target, response)
        else:
            await command(response)