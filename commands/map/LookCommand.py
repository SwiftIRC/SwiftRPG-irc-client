#!/usr/bin/env python3

from types import FunctionType
import API.api as api
import common
import string


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
        raw_response = await api.get(game, command, target, token, "map/user/look")

        if raw_response:
            if raw_response["failure"] != None:
                return "[{}] 👀 Error: {}".format(character, raw_response["failure"])
            response = raw_response.get("metadata", {})
            edges = []
            water = False
            for edge in response["edges"]:
                if edge["is_road"]:
                    edges.append(edge["direction"])
                if edge["name"] == "Water":
                    water = True
            edge_str = ", ".join(edges)
            if len(edges) > 1:
                edge_split = edge_str.split()
                edge_split.insert(-1, "and")
                edge_str = " ".join(edge_split)

            return "[{}] 👀 Looking around [{}, {}]. {} Buildings: {} | People: {} | Trees: {} | Roads: {} | {} available | {}".format(
                character,
                response["x"],
                response["y"],
                response["terrain"]["description"],
                len(response["buildings"]),
                len(response["npcs"]),
                response["available_trees"],
                edge_str,
                "Water" if water else "No water",
                "Undiscovered."
                if response["discovered_at"] == None
                else "Discovered by {} ({}).".format(
                    response["discovered_by"]["name"], response["discovered_at"]
                )
                if response["discovered_by"]["name"].lower() != character.lower()
                else "You discovered this area ({}).".format(response["discovered_at"]),
            )
    elif len(split) >= 2:
        if split[1] in ["person", "people", "npcs", "npc"]:
            returned = await api.get(game, command, target, token, "map/user/look/npcs")

            if returned:
                response = returned.get("metadata", {})

                if response and len(response):
                    npcs = []
                    for i in range(0, len(response)):
                        npcs.append(
                            "{}: {} {}".format(
                                str(i + 1),
                                response[i]["first_name"],
                                response[i]["last_name"],
                            )
                        )
                    if len(split) == 2:
                        return "[{}] 👀 Looking around at people: {}".format(
                            character, ", ".join(npcs)
                        )
                    elif len(split) == 3 and split[2].isdigit():
                        if int(split[2]) - 1 <= len(response):
                            npc = response[int(split[2]) - 1]
                            await game.process_response(
                                command,
                                target,
                                "[{}] 👀 Looking at Person: {} {} | {} | {} | {} | {}".format(
                                    character,
                                    npc["first_name"],
                                    npc["last_name"],
                                    npc["gender"].title(),
                                    npc["species"].title(),
                                    npc["occupation"]["name"],
                                    npc["occupation"]["description"],
                                ),
                            )

                            stats = [
                                "{} {} ({:,}xp)".format(
                                    skill["name"].title(),
                                    await game.level(skill["quantity"]),
                                    skill["quantity"],
                                )
                                for skill in npc["skills"]
                            ]

                            return "[{}] 👀 {}".format(character, " | ".join(stats))

                        else:
                            return "[{}] 👀 Looking at Person: Invalid index.".format(
                                character
                            )
                return "[{}] 👀 Looking around at people: None present".format(character)
        elif split[1] == "buildings" or split[1] == "building":
            returned = await api.get(
                game, command, target, token, "map/user/look/buildings"
            )

            if returned:
                response = returned.get("metadata", {})

                if len(response):
                    buildings = [
                        str(building["id"]) + ": " + building["name"]
                        for building in response
                    ]
                    return "[{}] 👀 Looking around at buildings. {}".format(
                        character, ", ".join(buildings)
                    )
            return "[{}] 👀 Looking around at buildings: None present".format(character)
        elif split[1] in ["north", "east", "south", "west"]:
            direction = split[1]

            returned = await api.get(
                game, command, target, token, "map/user/look/" + direction
            )
            if returned:
                response = returned.get("metadata", None)

                if response:
                    if "x" in response:
                        return "[{}] 👀 Looking {} at [{}, {}]. There appears to be {} {}".format(
                            character,
                            direction,
                            response["x"],
                            response["y"],
                            response["terrain"]["description"].lower(),
                            "Undiscovered."
                            if response["discovered_at"] == None
                            else "Discovered by {} ({}).".format(
                                response["discovered_by"]["name"],
                                response["discovered_at"],
                            )
                            if response["discovered_by"]["name"].lower()
                            != character.lower()
                            else "You discovered this area ({}).".format(
                                response["discovered_at"]
                            ),
                        )
                    else:
                        return "[{}] 👀 {}".format(
                            character, response.get("error", "Something went wrong")
                        )
                else:
                    return "[{}] 👀 {}".format(
                        character, response.get("error", "Something went wrong")
                    )
        else:
            return "[{}] 👀 Command not found.".format(character)
    else:
        return "[{}] 👀 Command not found.".format(character)
