#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'thieving/pickpocket')
    if response:
        prefix = '🕵️ Pickpocketing'
        if 'thieving' in response:
            return "[{}] {}: {} ({}xp) - Gold: {}".format(character, prefix, await game.level(response.get('thieving', 0)), response.get('thieving', 0), response.get('gold', 0))
        elif 'error' in response:
            return "[{}] {}: {} ({} hitpoints remaining)".format(character, prefix, response.get('error', ''), response.get('hitpoints', -1))
