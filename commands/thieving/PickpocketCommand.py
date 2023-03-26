#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'thieving/pickpocket')
    if response:
        prefix = '🕵️ Pickpocketing'
        if response.get('original', response).get('experience', 0):
            return "[{}] {}: {} ({}xp) - Gold: {}".format(character,
                                                          prefix,
                                                          await game.level(response.get('original', response).get('experience', 0)),
                                                          response.get('original', response).get(
                                                              'experience', 0),
                                                          response.get('original', response).get('reward', 0).get('total', 0))
        elif response.get('error'):
            return "[{}] {}: {} ({} hitpoints remaining)".format(character, prefix, response.get('error', ''), response.get('hitpoints', -1))
