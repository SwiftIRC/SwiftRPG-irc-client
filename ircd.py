#!/usr/bin/env python3

import irc.bot
import re
import asyncio

class IRC(irc.bot.SingleServerIRCBot):
    thread_lock = None
    running = True

    config = None
    connection = None
    discord = None

    game = None

    def __init__(self, config, game):
        irc.client.ServerConnection.buffer_class.encoding = "latin-1"
        irc.bot.SingleServerIRCBot.__init__(self, [
            (config["SERVER"],
             config["PORT"])],
            config["NICK"],
            "SwiftRPG")

        self.config = config
        self.game = game

    def set_discord(self, discordd):
        self.discord = discordd

    def set_thread_lock(self, lock):
        self.thread_lock = lock

    def close(self):
        self.running = False
        self.connection.quit("Adios!")

    def privmsg(self, target, message):
        self.connection.privmsg(target, message.strip())

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        self.connection = connection

        connection.join(
            ','.join([channel for channel in self.config['CHANNELS']]))

    def on_pubmsg(self, connection, event):
        if (event.target in self.config['CHANNELS']):
            with self.thread_lock:
                message = event.arguments[0].strip()
                print("[IRC] [{}] ({}) {}".format(event.target, event.source.nick, message))
                if message.startswith('+') or message.startswith('-') or message.startswith('!') or message.startswith('@') or message.startswith('.'):
                    print('[IRC] [{}] CMD DETECTED: ({}) {}'.format(event.target, event.source.nick, message))

                    loop = asyncio.new_event_loop()
                    try:
                        loop.run_until_complete(self.game.command(self.privmsg, event.target, event.source.nick, message))
                    finally:
                        loop.close()

    def run(self):
        self.start()

        if self.running:
            self.running = False
            ircd = IRC({"irc": self.config})
            ircd.set_discord(self.discord)
            self.discord.set_irc(ircd)
            ircd.set_thread_lock(self.thread_lock)
            ircd.run()