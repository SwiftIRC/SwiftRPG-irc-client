#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import os
import string
import time
import controllers.CommandController as CommandController


class Game:
    ssl_verify = True
    irc_privmsg = None
    config = {}

    def __init__(self, config):
        if os.getenv("SSL_VERIFY"):
            self.ssl_verify = bool(int(os.getenv("SSL_VERIFY")))
        self.config = config
        self.game_controller = CommandController.CommandController(self)

    def set_irc_privmsg(self, irc_privmsg):
        self.irc_privmsg = irc_privmsg

    def start(self):
        while True:
            time.sleep(300)

    async def xp(self, level: int):
        return level + 10 * level**3

    async def level(self, xp: int):
        for i in range(0, 101):
            if await self.xp(i) > xp:
                return i - 1
        return 100

    async def process_response(self, command, target, response):
        command(target, response)

    async def process_private_response(self, command, target, response):
        command(target, response)

    async def command(
        self,
        auth,
        command: FunctionType,
        target: string,
        author: string,
        message: string,
    ):
        character = await auth.get_character(str(author))
        token = await auth.get_token(str(author))
        response = await self.game_controller.run(
            command, target, author, message, character, token
        )
        await self.process_response(command, target, response)

    async def process_generic_command(self, response):
        if response == None or len(response) == 0:
            return response
        elif "failure" in response and response["failure"] != None:
            return "[{}] {} Failure: {}".format(
                response.get("user").get("name"),
                response.get("command").get("emoji"),
                response.get("failure", ""),
            )
        elif "reward" in response and response["reward"] != None:
            xp_rewards = [
                "{}: {} ({}xp) [+{}xp]".format(
                    reward.get("details").get("name").title(),
                    await self.level(reward.get("total", 0)),
                    reward.get("total", 0),
                    reward.get("gained", 0),
                )
                for reward in response.get("reward", {}).get("experience", [])
            ]
            item_rewards = [
                "{}: {} [{}{}]".format(
                    loot.get("details").get("name"),
                    loot.get("total", 0),
                    "+" if loot.get("gained", 0) > 0 else "",
                    loot.get("gained", 0),
                )
                for loot in response.get("reward", {}).get("loot", [])
            ]
            rewards = " | ".join(xp_rewards + item_rewards)
            return "[{}] {} {} | {} {} seconds more of {}.".format(
                response.get("user").get("name"),
                response.get("command").get("emoji"),
                response.get("command").get("method").title(),
                "" if len(rewards) == 0 else "{} |".format(rewards),
                response.get("seconds_until_tick", 0),
                response.get("command").get("verb"),
            )

    #     elif message[1:] == 'steal':
    #         response = await api.post(
    #             self, command, target, token, 'thieving/steal')
    #         if response:
    #             await self.process_response(command, target, "[{}] 🕵️ Thieving: {} ({}xp) - Gold: {}".format(character, await self.level(response.get('thieving', 0)), response.get('thieving', 0), response.get('gold', 0)))
    #     elif message[1:] == 'pilfer':
    #         response = await api.post(
    #             self, command, target, token, 'thieving/pilfer')
    #         if response:
    #             await self.process_response(command, target, "[{}] 🕵️ Thieving: {} ({}xp) - Gold: {}".format(character, await self.level(response.get('thieving', 0)), response.get('thieving', 0), response.get('gold', 0)))
    #     elif message[1:] == 'plunder':
    #         response = await api.post(
    #             self, command, target, token, 'thieving/plunder')
    #         if response:
    #             await self.process_response(command, target, "[{}] 🕵️ Thieving: {} ({}xp) - Gold: {}".format(character, await self.level(response.get('thieving', 0)), response.get('thieving', 0), response.get('gold', 0)))
    #         pass
    #     # Fishing
    #     elif message[1:] == "net":
    #         pass
    #     elif message[1:] == "lure":
    #         pass
    #     elif message[1:] == "angle":
    #         pass
    #     # Mining
    #     elif message[1:] == "mine":
    #         pass
    #     # Smithing
    #     elif message[1:] == "smith":
    #         pass
    #     # Crafting
    #     elif message[1:] == "craft":
    #         pass
    #     # Cooking
    #     elif message[1:] == "cook":
    #         pass
