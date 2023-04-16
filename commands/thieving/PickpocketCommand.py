#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    data = {}
    split = message.split()
    if len(split) == 2 and split[1].isdigit():
        data['target'] = split[1]

    response = await api.post(game, command, target, token, 'thieving/pickpocket', data)
    if response:
        if 'reward' in response:
            return "[{}] 🕵️ Pickpocketing: {} ({}xp) [+{}xp] | {}: {} [+{}] | {} seconds until completion".format(
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
            return "[{}] 🕵️ Error: {} ({} hitpoints remaining)".format(
                character,
                response.get('error', ''),
                response.get('metadata', {}).get('hitpoints', -1)
            )
