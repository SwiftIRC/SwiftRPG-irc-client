#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'woodcutting/chop')
    if response and 'experience' in response:
        return "[{}] 🪓 Woodcutting: {} ({}xp) | Logs: {} | {} seconds until completion".format(
            character,
            await game.level(response.get('experience')),
            response.get('experience'),
            response.get('reward', {}).get('total', 0),
            response.get('seconds_until_tick', 0)
        )
