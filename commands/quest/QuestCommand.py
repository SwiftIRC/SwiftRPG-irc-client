#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import common
import string
from box import Box


async def exec(
    game: FunctionType,
    command: string,
    target,
    author: string,
    message: string,
    character: string,
    token: string,
):
    split = message.split()

    if len(split) == 1:
        return "[{0}] 📜 Syntax: {1} list | {1} start [Quest ID] (Step ID) | {1} inspect [Quest ID]".format(
            character, split[0]
        )
    elif len(split) >= 2:
        if split[1] == "list":
            response = await api.get(game, command, target, token, "quests")

            if response and len(response):
                quests = []
                for index in response:
                    quest = Box(index)
                    quests.append(
                        "{}: {} ({}/{})".format(
                            str(quest.id), quest.name, quest.completed, quest.total
                        )
                    )
                return "[{}] {} {} | {}".format(
                    character,
                    "📜",
                    "Questing",
                    ", ".join(quests),
                )
            return "[{}] 📜 Questing | None started".format(character)
        elif split[1] == "start":
            if len(split) < 3:
                return "[{}] 📜 Syntax: {} start [Quest ID] (Step ID)".format(
                    character, split[0]
                )
            path = "quests/start/{}/{}".format(
                split[2], "" if len(split) < 4 else split[3]
            )
            response = await api.get(game, command, target, token, path)
            r = Box(response)

            if response:
                if response["failure"] != None:
                    return "[{}] 📜 Error: {}".format(character, response["failure"])
                quest = Box(response["metadata"])
                if quest.incomplete_dependencies > 0:
                    incomplete_steps = [
                        str(step["id"]) for step in quest.incomplete_steps
                    ]
                    plural = "s" if quest.incomplete_dependencies > 1 else ""
                    return "[{}] {} {}: Quest dependencies not met | {} step{}".format(
                        r.user.name,
                        r.command.emoji,
                        r.command.name.title(),
                        str(quest.incomplete_dependencies),
                        plural,
                    )
                rewards = {
                    reward: quest[reward]
                    for reward in quest
                    if reward == "gold"
                    or reward in common.lib.skills
                    and quest[reward] > 0
                }
                quests = "{}: {} | {}".format(
                    str(quest.details.id),
                    quest.details.name,
                    quest.step_details.output,
                )
                return "[{}] {} {}: {}".format(
                    r.user.name, r.command.emoji, r.command.name, quests
                )
        elif split[1] == "inspect":
            if len(split) < 3:
                return "[{}] 📜 Syntax: {} inspect [Quest ID]".format(
                    character, split[0]
                )
            path = "quests/inspect/{}".format(split[2])
            response = await api.get(game, command, target, token, path)

            if response:
                quest = response["metadata"]

                rewards = {
                    reward["details"]["name"].title(): reward["gained"]
                    for reward_type in response["reward"]
                    for reward in response["reward"][reward_type]
                }
                quests = []
                quests.append(
                    "{}: {} | {} | Completion: {}/{} | Rewards: {}".format(
                        str(quest["details"]["id"]),
                        quest["details"]["name"],
                        quest["details"]["description"],
                        len(quest.get("complete_steps", [])),
                        len(quest.get("incomplete_steps", []))
                        + len(quest.get("complete_steps", [])),
                        ", ".join(
                            [
                                "{}: {}".format(reward, rewards[reward])
                                for reward in rewards
                                if rewards[reward]
                            ]
                        ),
                    )
                )
                return "[{}] 📜 Quests: {}".format(character, ", ".join(quests))
