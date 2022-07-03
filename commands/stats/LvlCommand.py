#!/usr/bin/env python3

async def exec(game, command, target, author, message, character, token):
    split = message.split()

    if len(split) != 2:
        await self.process_response(command, target, "Usage: {} <experience>".format(split[0]))
        return
    level = await self.level(int(split[1]))
    await self.process_response(command, target, "XP of {} is equivalent to level {}".format(split[1], level))
