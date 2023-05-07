#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, "fishing/fish")
    if response:
        return await game.process_generic_command(response)
