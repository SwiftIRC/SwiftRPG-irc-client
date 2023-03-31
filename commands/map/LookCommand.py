#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import string


async def exec(game: FunctionType, command: string, target, author: string, message: string, character: string, token: string):
    split = message.split()

    if len(split) == 1:
        raw_response = await api.get(game, command, target, token, 'map/user/look')

        if raw_response:
            response = raw_response.get('meta', {}).get('response', None)
            edges = []
            for edge in response['edges']:
                if edge['pivot']['is_road']:
                    edges.append(edge['pivot']['direction'])
            edge_str = ', '.join(edges)
            if len(edges) > 1:
                edge_split = edge_str.split()
                edge_split.insert(-1, 'and')
                edge_str = ' '.join(edge_split)

            return "[{}] 👀 Looking around [{}, {}]. {} Buildings: {} - NPCs: {} - Trees: {} - Roads: {}".format(character, response['x'], response['y'], response['terrain'][0]['description'], len(response['buildings']), len(response['npcs']), response['available_trees'], edge_str)
        return "[{}] 👀 Something went wrong.".format(character)
    elif len(split) >= 2:
        if split[1] in ['person', 'people', 'npcs', 'npc']:
            returned = await api.get(game, command, target, token, 'map/user/look/npcs')

            if returned:
                response = returned.get('meta', {}).get('response', None)
                print(response)

                if len(response):
                    npcs = []
                    for i in range(0, len(response)):
                        npcs.append(str(i + 1) + ': ' + response[i]['name'])
                    if len(split) == 2:
                        return "[{}] 👀 Looking around at people: {}".format(character, ', '.join(npcs))
                    elif len(split) == 3 and split[2].isdigit():
                        if int(split[2]) - 1 <= len(response):
                            npc = response[int(split[2]) - 1]
                            return "[{}] 👀 Looking at Person: {} | {} | {}".format(character, npc['name'], npc['occupation']['name'], npc['occupation']['description'])
                        else:
                            return "[{}] 👀 Looking at Person: Invalid index.".format(character)
            return "[{}] 👀 Looking around at people: None present".format(character)
        elif split[1] == 'buildings' or split[1] == 'building':
            returned = await api.get(game, command, target, token, 'map/user/look/buildings')

            if returned:
                response = returned.get('meta', {}).get('response', None)

                if response:
                    buildings = [str(building['id']) + ': ' + building['name']
                                 for building in response]
                    return "[{}] 👀 Looking around at buildings. {}".format(character, ', '.join(buildings))
            return "[{}] 👀 Looking around at buildings: None present".format(character)
        elif split[1] in ["north", "east", "south", "west"]:
            direction = split[1]

            returned = await api.get(game, command, target, token, 'map/user/look/' + direction)
            if returned:
                response = returned.get('meta', {}).get('response', None)

                if response:
                    if 'x' in response:
                        return "[{}] 👀 Looking {} at [{}, {}]. There appears to be {}".format(character, direction, response['x'], response['y'], response['terrain']['description'].lower())
                    else:
                        return "[{}] 👀 {}".format(character, response.get('error', 'Something went wrong'))
        return "[{}] 👀 Command not found.".format(character)
