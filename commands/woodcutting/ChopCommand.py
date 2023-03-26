#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'woodcutting/chop')
    if response:
        return "[{}] 🪓 Woodcutting: {} ({}xp) - Logs: {}".format(character, await game.level(response.get('original', response).get('experience', 0)), response.get('original', response).get('experience', 0), response.get('original', response).get('reward', 0).get('total', 0))
