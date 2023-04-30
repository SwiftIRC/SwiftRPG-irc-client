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
        return "[{0}] 🗺️ Syntax: {1} list | {1} start [Quest ID] (Step ID) | {1} inspect [Quest ID]".format(
            character, split[0]
        )
    elif len(split) >= 2:
        if split[1] == "list":
            response = await api.get(game, command, target, token, "quests")

            if response:
                quests = []
                for index in response:
                    quest = Box(index)
                    quests.append(
                        "{}: {} ({}/{})".format(
                            str(quest.id), quest.name, quest.completed, quest.total
                        )
                    )
                return "[{}] 🗺️ Quests | {}".format(character, ", ".join(quests))
            return "[{}] 🗺️ Quests | None started".format(character)
        elif split[1] == "start":
            if len(split) < 3:
                return "[{}] 🗺️ Syntax: {} start [Quest ID] (Step ID)".format(
                    character, split[0]
                )
            path = "quests/start/{}/{}".format(
                split[2], "" if len(split) < 4 else split[3]
            )
            response = await api.get(game, command, target, token, path)

            if response:
                if response["failure"] != None:
                    return "[{}] 🗺️ Error: {}".format(character, response["failure"])
                quest = response["metadata"]["response"]
                if quest.get("incompleteDependencies", 0) > 0:
                    incompleteSteps = [
                        str(step["id"]) for step in quest.get("incompleteSteps", [])
                    ]
                    plural = "s" if quest["incompleteDependencies"] > 1 else ""
                    return (
                        "[{}] 🗺️ Quests: Quest dependencies not met | {} step{}".format(
                            character, str(quest["incompleteDependencies"]), plural
                        )
                    )
                rewards = {
                    reward: quest[reward]
                    for reward in quest
                    if reward == "gold"
                    or reward in common.lib.skills
                    and quest[reward] > 0
                }
                quests = "{}: {} | {} {}".format(
                    str(quest.get("id")),
                    quest.get("name"),
                    quest.get("step", {}).get("output"),
                    "(repeated)" if quest.get("completeStep", None) != None else "",
                )
                return "[{}] 🗺️ Quests: {}".format(character, quests)
        elif split[1] == "inspect":
            if len(split) < 3:
                return "[{}] 🗺️ Syntax: {} inspect [Quest ID]".format(
                    character, split[0]
                )
            path = "quests/inspect/{}".format(split[2])
            response = await api.get(game, command, target, token, path)

            if response:
                quest = response["metadata"]["response"]

                rewards = {
                    reward: quest[reward]
                    for reward in quest
                    if reward == "gold"
                    or reward in common.lib.skills
                    and quest[reward] > 0
                }
                quests = []
                quests.append(
                    "{}: {} | {} | Completion: {}/{} | Rewards: {}".format(
                        str(quest.get("id")),
                        quest.get("name"),
                        quest.get("description"),
                        len(quest.get("completeSteps", [])),
                        len(quest.get("incompleteSteps", []))
                        + len(quest.get("completeSteps", [])),
                        " ~ ".join(
                            [
                                "{}: {}".format(reward, rewards[reward])
                                for reward in rewards
                                if rewards[reward]
                            ]
                        ),
                    )
                )
                return "[{}] 🗺️ Quests: {}".format(character, ", ".join(quests))
