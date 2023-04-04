#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import common
import string
from box import Box


async def exec(game: FunctionType, command: string, target, author: string, message: string, character: string, token: string):
    split = message.split()

    if len(split) == 1:
        return "[{}] 🗺️ Syntax: !quest list | !quest start [Quest ID] (Step ID) | !quest inspect [Quest ID]".format(character)
    elif len(split) >= 2:
        if split[1] == 'list':
            response = await api.get(game, command, target, token, 'quests')

            print(response)
            if response:
                quests = []
                for index in response:
                    quest = Box(index)
                    quests.append('{}: {}'.format(
                        str(quest.id),
                        quest.name
                    ))
                return "[{}] 🗺️ Quests: {}".format(character, ', '.join(quests))
            return "[{}] 🗺️ Quests: None started".format(character)
        elif split[1] == 'start':
            if len(split) < 3:
                return "[{}] 🗺️ Syntax: !quest start [Quest ID] (Step ID)".format(character)
            path = 'quests/start/{}/{}'.format(
                split[2], '' if len(split) < 4 else split[3])
            quest = await api.get(game, command, target, token, path)

            if quest:
                print(quest)
                if quest['incompleteDependencies'] > 0:
                    incompleteSteps = [str(step['id'])
                                       for step in quest.get('incompleteSteps', [])]
                    plural = 's' if quest['incompleteDependencies'] > 1 else ''
                    return "[{}] 🗺️ Quests: Quest dependencies not met | {} step{}".format(
                        character,
                        str(quest['incompleteDependencies']),
                        plural
                    )
                rewards = {
                    reward: quest[reward]
                    for reward in quest
                    if reward == 'gold' or reward in common.lib.skills
                    and quest[reward] > 0
                }
                quests = '{}: {} | {} {}'.format(
                    str(quest.get('id')),
                    quest.get('name'),
                    quest.get('step', {}).get('output'),
                    '(repeated)' if quest.get(
                        'completeStep', None) != None else ''
                )
                return "[{}] 🗺️ Quests: {}".format(character, quests)
            return "[{}] 🗺️ Quests: something went wrong".format(character)
        elif split[1] == 'inspect':
            if len(split) < 3:
                return "[{}] 🗺️ Syntax: !quest inspect [Quest ID]".format(character)
            path = 'quests/inspect/{}'.format(
                split[2], '' if len(split) < 4 else split[3])
            quest = await api.get(game, command, target, token, path)

            if quest:
                print(quest)
                rewards = {
                    reward: quest[reward]
                    for reward in quest
                    if reward == 'gold' or reward in common.lib.skills
                    and quest[reward] > 0
                }
                quests = []
                quests.append('{}: {} | {} | Completion: {}/{} | Rewards: {}'.format(
                    str(quest.get('id')),
                    quest.get('name'),
                    quest.get('description'),
                    len(quest.get('completeSteps', [])),
                    len(quest.get('incompleteSteps', [])) +
                    len(quest.get('completeSteps', [])),
                    ' ~ '.join(
                        [
                            '{}: {}'.format(reward, rewards[reward])
                            for reward in rewards
                            if rewards[reward]
                        ]
                    )
                ))
                return "[{}] 🗺️ Quests: {}".format(character, ', '.join(quests))
            return "[{}] 🗺️ Quests: something went wrong".format(character)


'''
{
"id": 1,
"name": "Teacher's Pet",
"description": "Use `.quest start 1` to start this quest.",
"gp": "0",
"thieving": 0,
"fishing": 0,
"mining": 0,
"woodcutting": 50,
"firemaking": 0,
"cooking": 0,
"smithing": 0,
"fletching": 0,
"crafting": 0,
"herblore": 0,
"agility": 0,
"farming": 0,
"hunter": 0,
"step": {
"id": 3,
"quest_id": 1,
"output": "You report your progress back to the teacher and... Congratulations! You have completed the first quest. In one (1) tick you will receive your reward.",
"ticks": 1
},
"requested_step_id": 3,
"incompleteDependencies": 1,
"incompleteSteps": [
{
"id": 2,
"quest_id": 1,
"output": "Your teacher has asked you to collect 1 apple. Use `.quest inspect 1` to view progress.",
"ticks": 5
},
{
"id": 3,
"quest_id": 1,
"output": "You report your progress back to the teacher and... Congratulations! You have completed the first quest. In one (1) tick you will receive your reward.",
"ticks": 1
}
],
"dependencies": [
{
"id": 2,
"quest_id": 1,
"quest_step_id": 2,
"quest_step_dependency_id": 2,
"output": "Your teacher has asked you to collect 1 apple. Use `.quest inspect 1` to view progress.",
"ticks": 5
}
],
"completeStep": null,
"completeSteps": [
{
"id": 1,
"user_id": 1,
"quest_id": 1,
"quest_step_id": 1
}
]
}
'''
