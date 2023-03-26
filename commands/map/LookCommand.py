#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import string


async def exec(game: FunctionType, command: string, target, author: string, message: string, character: string, token: string):
    split = message.split()

    if len(split) == 1:
        response = await api.get(game, command, target, token, 'map/user/look')
        if response:
            edges = []
            for edge in response['edges']:
                if edge['pivot']['is_road']:
                    edges.append(edge['pivot']['direction'])
            edge_str = ', '.join(edges)
            if len(edges) > 1:
                edge_split = edge_str.split()
                edge_split.insert(-1, 'and')
                edge_str = ' '.join(edge_split)

            return "[{}] 👀 Looking around [{}, {}]. Buildings: {} - NPCs: {} - Trees: {} - Roads: {}".format(character, response['x'], response['y'], len(response['buildings']), len(response['npcs']), response['available_trees'], edge_str)
    elif len(split) == 2:
        if split[1] == 'npcs' or split[1] == 'npc':
            response = await api.get(game, command, target, token, 'map/user/look/npcs')
            if len(response):
                npcs = [str(npc['id']) + ': ' + npc['name']
                        for npc in response]
                return "[{}] 👀 Looking around at NPCs: {}".format(character, ', '.join(npcs))
        elif split[1] == 'buildings' or split[1] == 'building':
            response = await api.get(game, command, target, token, 'map/user/look/buildings')
            if response:
                buildings = [str(building['id']) + ': ' + building['name']
                             for building in response]
                return "[{}] 👀 Looking around at buildings. {}".format(character, ', '.join(buildings))
        elif split[1] in ["north", "east", "south", "west"]:
            direction = split[1]

            response = await api.get(game, command, target, token, 'map/user/look/' + direction)
            if response:
                return "[{}] 👀 Looking {} at [{}, {}]. It appears to be {}".format(character, direction, response['x'], response['y'], response['terrain'][0]['description'].lower())
