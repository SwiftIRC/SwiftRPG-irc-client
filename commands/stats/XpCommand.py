#!/usr/bin/env python3

async def exec(game, command, target, author, message, character, token):
    split = message.split()

    if len(split) != 2:
        return "Usage: {} <level>".format(split[0])
        return
    xp = await game.xp(int(split[1]))
    return "Level {} is equivalent to {} XP".format(split[1], xp)
