#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    args = message.split()

    character = ""
    if len(args) >= 2:
        character = args[1]

    response = await api.get(game, command, target, token, "stats/{}".format(character))

    if response:
        return "[{}] {}".format(
            response["user"]["name"],
            " | ".join(
                [
                    "{}: {} ({:,}xp)".format(
                        skill["details"]["name"].title(),
                        await game.level(skill["gained"]),
                        skill["gained"],
                    )
                    for skill in response["skills"]
                ]
            ),
        )
