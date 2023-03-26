#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'thieving/pickpocket')
    if response:
        prefix = '🕵️ Pickpocketing'
        print(response)
        if 'experience' in response:
            return "[{}] {}: {} ({}xp) - Gold: {}".format(
                character,
                prefix,
                await game.level(response.get('experience', 0)),
                response.get(
                    'experience', 0),
                response.get('reward', {}).get(
                    'total', 0)
            )
        elif 'error' in response:
            return "[{}] {}: {} ({} hitpoints remaining)".format(
                character,
                prefix,
                response.get(
                    'error', ''),
                response.get(
                    'hitpoints', -1)
            )
