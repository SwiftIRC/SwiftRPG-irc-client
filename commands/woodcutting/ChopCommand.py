#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'woodcutting/chop')
    if response:
        if 'reward' in response:
            return "[{}] 🪓 Woodcutting: {} ({}xp) [+{}xp] | {}: {} [+{}] | {} seconds until completion".format(
                character,
                await game.level(response.get('reward').get('experience')[0].get('total', 0)),
                response.get('reward', {}).get(
                    'experience')[0].get('total', 0),
                response.get('reward', {}).get('experience')[
                    0].get('pivot').get('value', 0),
                response.get('reward', {}).get('loot')[0].get('name', ''),
                response.get('reward', {}).get('loot')[0].get('total', 0),
                response.get('reward', {}).get('loot')[
                    0].get('pivot').get('value', 0),
                response.get('seconds_until_tick', 0)
            )
        elif 'error' in response:
            return "[{}] 🪓 Error: {}".format(
                character,
                response.get('error', ''),
            )
