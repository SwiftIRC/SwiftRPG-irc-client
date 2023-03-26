#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'woodcutting/chop')
    if 'experience' in response:
        return "[{}] 🪓 Woodcutting: {} ({}xp) - Logs: {}".format(
            character,
            await game.level(response.get('experience')),
            response.get('experience'),
            response.get('reward', {}).get('total', 0)
        )
