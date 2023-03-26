#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'firemaking/burn')
    if response:
        prefix = '🔥 Firemaking'
        if response.get('experience', 0):
            return "[{}] {}: {} ({}xp) - Logs: {}".format(
                character,
                prefix,
                await game.level(response.get('experience', 0)),
                response.get(
                    'experience', 0),
                response.get('reward', {}).get(
                    'total', 0)
            )
        elif response.get('error'):
            return "[{}] {}: {}".format(
                character,
                prefix,
                response.get('error', '')
            )
