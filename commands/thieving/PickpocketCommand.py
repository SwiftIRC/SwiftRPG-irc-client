import API.api as api


async def exec(game, command, target, author, message, character, token):
    response = await api.post(game, command, target, token, 'thieving/pickpocket')
    if response:
        return "[{}] 🕵️ Thieving: {} ({}xp) - Gold: {}".format(character, await game.level(response.get('thieving', 0)), response.get('thieving', 0), response.get('gold', 0))
