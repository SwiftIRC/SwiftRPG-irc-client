#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.get(game, command, target, token, 'map/user/look')
    if response:
        return "[{}] 👀 Looking around [{}, {}]. Trees: {} - NPCs: {}".format(character, response['x'], response['y'], response['available_trees'], len(response['npcs']))
