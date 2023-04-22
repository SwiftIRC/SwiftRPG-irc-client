#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    data = {}
    split = message.split()
    if len(split) == 2 and split[1].isdigit():
        data['target'] = split[1]

    response = await api.post(game, command, target, token, 'thieving/pickpocket', data)

    if response:
        return await game.process_generic_command(response)
