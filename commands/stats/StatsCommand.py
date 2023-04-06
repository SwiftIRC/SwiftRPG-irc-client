#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    args = message.split()[0][1:]

    if len(args) != 2:
        response = await api.get(game, command, target, token, 'stats')
    else:
        character = args[1]
        response = await api.get(game, command, target, token, 'stats/{}'.format(args[1]))

    return "Stats: {} - Thieving: {} ({:,}xp) - Woodcutting: {} ({:,}xp) - Firemaking: {} ({:,}xp)".format(character, await game.level(response.get('thieving')), response.get('thieving'), await game.level(response.get('woodcutting')), response.get('woodcutting'), await game.level(response.get('firemaking')), response.get('firemaking'))
