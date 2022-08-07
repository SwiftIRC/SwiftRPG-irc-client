#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'woodcutting/chop')
    if response:
        return "[{}] 🪓 Woodcutting: {} ({}xp) - Logs: {}".format(character, await game.level(response.get('original', response).get('woodcutting', 0)), response.get('original', response).get('woodcutting', 0), response.get('original', response).get('logs', 0))
