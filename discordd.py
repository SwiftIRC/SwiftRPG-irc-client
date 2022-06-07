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
irc = None


class Discord:
    def __init__(self, conf):
        global config
        global thread_lock
        global channels

        channels = {conf['CHANNELS'][channel]
            : channel for channel in conf['CHANNELS']}

        config = conf

    def set_irc(self, ircd):
        global irc
        irc = ircd

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
    global irc

    # Don't reply to itself
    if message.author == client.user:
        return

    with thread_lock:
        content = message.clean_content
        if len(message.attachments) > 0:
            content += ' ' + message.attachments[0].url

    print('[Discord] [#{}] {}'.format(message.channel, content))

    # if content.startswith('+') or content.startswith('-') or content.startswith('!') or content.startswith('@') or content.startswith('.'):
    #     irc.privmsg(channels[message.channel.id], "%s" % (content))
    # else:
    #     irc.privmsg(channels[message.channel.id], "<%s> %s" %
    #                 (message.author.display_name, content))