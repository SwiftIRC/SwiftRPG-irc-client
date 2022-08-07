#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'firemaking/burn')
    if response:
        prefix = '🔥 Firemaking'
        if response.get('original', response).get('firemaking', 0):
            return "[{}] : {} ({}xp) - Logs: {}".format(character, prefix, await game.level(response.get('original', response).get('firemaking', 0)), response.get('original', response).get('firemaking', 0), response.get('original', response).get('logs', 0))
        elif response.get('error'):
            return "[{}] {}: {}".format(character, prefix, response.get('error', ''))
