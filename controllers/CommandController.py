#!/usr/bin/env python3

import commands.events.EngageCommand as command_engage
import commands.firemaking.BurnCommand as command_burn
import commands.map.ExploreCommand as command_explore
import commands.map.LookCommand as command_look
import commands.quest.QuestCommand as command_quest
import commands.stats.StatsCommand as command_stats
import commands.thieving.PickpocketCommand as command_pickpocket
import commands.woodcutting.ChopCommand as command_chop

import commands.stats.XpCommand as command_xp
import commands.stats.LvlCommand as command_lvl


class CommandController:
    commands = None
    auth = None
    command = None
    target = None
    author = None
    message = None
    character = None
    token = None

    def __init__(self, game):
        self.game = game
        self.commands = {
            "burn": command_burn.exec,
            "chop": command_chop.exec,
            "engage": command_engage.exec,
            "explore": command_explore.exec,
            "look": command_look.exec,
            "lvl": command_lvl.exec,
            "pickpocket": command_pickpocket.exec,
            "quest": command_quest.exec,
            "quests": command_quest.exec,
            "stats": command_stats.exec,
            "xp": command_xp.exec,
        }

    async def run(self, command, target, author, message, character, token):
        split = message.split()
        command_string = split[0][1:]

        try:
            if command_string in self.commands:
                await self.game.process_response(
                    command,
                    target,
                    await self.commands[command_string](
                        self.game, command, target, author, message, character, token
                    ),
                )
            else:
                await self.game.process_response(
                    command, target, "Error: command not found"
                )
        except Exception as e:
            await self.game.process_response(command, target, "Error: {}".format(e))
