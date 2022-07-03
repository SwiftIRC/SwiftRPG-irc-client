#!/usr/bin/env python3

async def exec(game, command, target, author, message, character, token):
    split = message.split()

    if len(split) != 2:
        return "Usage: {} <experience>".format(split[0])

    level = await game.level(int(split[1]))
    return "XP of {} is equivalent to level {}".format(split[1], level)
