#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    split = message.split()
    if len(split) < 2:
        return "Syntax: {} <north|east|south|west>".format(split[0])
    else:
        response = await api.post(game, command, target, token, 'map/user/move', {'direction': split[1]})
        if response:
            return "[{}] 🏃 Moving: {}".format(character, response)
