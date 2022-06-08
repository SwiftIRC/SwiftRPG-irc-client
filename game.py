#!/usr/bin/env python3

import time

class Game:
    def __init__(self):
        pass
    
    def start(self):
        while True:
            time.sleep(1)

    def irc_command(self, command, target, message):
        if message[1:] == 'foo':
            command(target, "bar")

    async def discord_command(self, command, message):
        if message[1:] == 'foo':
            await command("bar")