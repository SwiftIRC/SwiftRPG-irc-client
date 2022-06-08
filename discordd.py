import logging
import discord
import asyncio
from asyncio import coroutines
import concurrent.futures
from asyncio import futures

from discord import channel

logging.basicConfig(level=logging.INFO)

thread_lock = None

config = None
client = discord.Client()
server = None
channels = {}
game = None


class Discord:
    def __init__(self, conf, g):
        global config
        global thread_lock
        global channels
        global game

        channels = {conf['CHANNELS'][channel]
            : channel for channel in conf['CHANNELS']}

        config = conf
        game = g

    def set_thread_lock(self, lock):
        global thread_lock
        thread_lock = lock

    def privmsg(self, target, message):
        global client
        asyncio.run_coroutine_threadsafe(
            async_privmsg(target, message), client.loop)

    def run(self):
        global config
        global client

        client.run(config["TOKEN"])

    def close(self):
        global client
        global irc
        irc.set_running(False)
        asyncio.run_coroutine_threadsafe(client.close(), client.loop)


async def async_privmsg(target, message):
    global client

    channel = client.get_channel(target)

    await channel.send(message.strip())


@client.event
async def on_message(message):
    global config
    global client
    global channels
    global thread_lock
    global game

    # Don't reply to itself
    if message.author == client.user:
        return

    with thread_lock:
        content = message.clean_content
        if len(message.attachments) > 0:
            content += ' ' + message.attachments[0].url

    if message.channel.id in channels:
        print('[Discord] [#{}] ({}) {}'.format(message.channel, message.author, content))

        if content.startswith('+') or content.startswith('-') or content.startswith('!') or content.startswith('@') or content.startswith('.'):
            print('[Discord] [#{}] CMD DETECTED: ({}) {}'.format(message.channel, message.author, content))
            channel = client.get_channel(message.channel.id)
            await game.command(channel.send, None, message.author, content)