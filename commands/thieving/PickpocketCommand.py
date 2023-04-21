#!/usr/bin/env python3

import API.api as api


async def exec(game, command, target, author, message, character, token):
    data = {}
    split = message.split()
    if len(split) == 2 and split[1].isdigit():
        data['target'] = split[1]

    response = await api.post(game, command, target, token, 'thieving/pickpocket', data)
    if response:
        if 'failure' in response and response['failure'] != None:
            return "[{}] 🕵️ Failure: {} {}".format(
                character,
                response.get('failure'),
                ''
                if response.get('metadata') == None
                else '({} hitpoints remaining)'.format(
                    response.get('metadata', {}).get('hitpoints', -1)
                )
            )
        elif 'reward' in response and response['reward'] != None:
            xp_rewards = [
                '{}: {} ({}xp) [+{}xp]'.format(
                    reward.get('skill').get('name').title(),
                    await game.level(reward.get('total', 0)),
                    reward.get('total', 0),
                    reward.get('quantity', 0),
                )
                for reward in response.get('reward', {}).get('experience')
            ]
            item_rewards = [
                '{}: {} [+{}]'.format(
                    loot.get('item').get('name'),
                    loot.get('total', 0),
                    loot.get('quantity', 0),
                )
                for loot in response.get('reward', {}).get('loot')
            ]
            rewards = ' | '.join(xp_rewards + item_rewards)
            return "[{}] {} {} | {} {} seconds more of {}.".format(
                character,
                response.get('command').get('emoji'),
                response.get('command').get('method').title(),
                '' if len(rewards) == 0 else '{} |'.format(rewards),
                response.get('seconds_until_tick', 0),
                response.get('command').get('verb'),
            )
