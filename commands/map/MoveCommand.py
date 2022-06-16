#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import string


async def exec(game: FunctionType, command: string, target, author: string, message: string, character: string, token: string):
    split = message.split()
    if len(split) < 2 or split[1] not in ['north', 'east', 'south', 'west']:
        return "Syntax: {} <north|east|south|west>".format(split[0])
    else:
        response = await api.post(game, command, target, token, 'map/user/move', {'direction': split[1]})
        if response:
            return "[{}] 🏃 Moving [{},{}]".format(character, response['x'], response['y'], response['discovered_by'])
