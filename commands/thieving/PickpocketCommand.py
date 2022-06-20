#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'thieving/pickpocket')
    if response:
        if 'thieving' in response:
            return "[{}] 🕵️ Pickpocketing: {} ({}xp) - Gold: {}".format(character, await game.level(response.get('thieving', 0)), response.get('thieving', 0), response.get('gold', 0))
        elif 'error' in response:
            return "[{}] 🕵️ Pickpocketing: {} ({} hitpoints remaining)".format(character, response.get('error', ''), response.get('hitpoints', -1))
