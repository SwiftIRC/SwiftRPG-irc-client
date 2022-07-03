#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    args = message.split()[0][1:]

    if len(args) != 2:
        response = await api.get(game, command, target, token, 'stats')
    else:
        character = args[1]
        response = await api.get(game, command, target, token, 'stats/{}'.format(args[1]))

    return "Stats: {} - Thieving: {} - Woodcutting: {}".format(character, response['thieving'], response['woodcutting'])
