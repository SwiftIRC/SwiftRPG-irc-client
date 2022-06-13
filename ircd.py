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
    auth = None

    def __init__(self, config, game, auth):
        irc.client.ServerConnection.buffer_class.encoding = "latin-1"
        irc.bot.SingleServerIRCBot.__init__(self, [
            (config["SERVER"],
             config["PORT"])],
            config["NICK"],
            "SwiftRPG")

        self.config = config
        self.game = game
        self.game.set_irc_privmsg(self.privmsg)
        self.auth = auth

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
                print("[IRC] [{}] ({}) {}".format(
                    event.target, event.source.nick, message))
                if message.startswith('+') or message.startswith('-') or message.startswith('!') or message.startswith('@') or message.startswith('.'):
                    if message[1:] == "help":
                        self.privmsg(event.source.nick,
                                     "{}/help".format(self.config['HOSTNAME']))
                        return
                    elif not self.auth.check(event.source.nick):
                        self.privmsg(event.source.nick,
                                     "You are not logged in.")
                        return
                    print('[IRC] [{}] CMD DETECTED: ({}) {}'.format(
                        event.target, event.source.nick, message))
                    loop = asyncio.new_event_loop()
                    try:
                        loop.run_until_complete(self.game.command(
                            self.auth, self.privmsg, event.target, event.source.nick, message))
                    finally:
                        loop.close()

    def on_privmsg(self, connection, event):
        with self.thread_lock:
            message = event.arguments[0].strip()
            split = message.split()

            print("[IRC] [{}] ({}) {}".format(
                event.target, event.source.nick, message))

            if message.startswith('+') or message.startswith('-') or message.startswith('!') or message.startswith('@') or message.startswith('.'):
                print('[IRC] [{}] PM CMD DETECTED: ({}) {}'.format(
                    event.target, event.source.nick, message))

                if split[0][1:] == "login":
                    if len(split) != 3:
                        self.privmsg(
                            event.source.nick, "Syntax: {} <username> <password>".format(split[0]))
                        return
                    if self.auth.check(event.source.nick):
                        self.privmsg(event.source.nick,
                                     "You are already logged in.")
                    elif self.auth.login(event.source.nick, split[1], split[2]):
                        self.privmsg(event.source.nick, "Login successful!")
                    else:
                        # actual auth pls
                        self.privmsg(event.source.nick, "Login failed!")
                elif split[0][1:] == "logout":
                    if self.auth.check(event.source.nick):
                        self.auth.logout(event.source.nick)
                        self.privmsg(event.source.nick, "Logout successful!")
                    else:
                        self.privmsg(event.source.nick,
                                     "You are not logged in.")
                elif split[0][1:] == "loggedin":
                    if self.auth.check(event.source.nick):
                        self.privmsg(event.source.nick,
                                     "Successfully logged in!")
                    else:
                        self.privmsg(event.source.nick,
                                     "Not currently logged in.")
                elif split[0][1:] == "help":
                    self.privmsg(event.source.nick,
                                 "{}/help".format(self.config['HOSTNAME']))

    def on_nick(self, nick, event):
        old_name = event.source.nick
        new_name = event.target

        if self.auth.check(old_name):
            self.auth.rename(old_name, new_name)

    def on_quit(self, quit, event):
        if self.auth.check(event.source.nick):
            self.auth.logout(event.source.nick)

    def on_kick(self, kick, event):
        print(event.arguments[0])
        if event.target in self.config['CHANNELS'] and self.auth.check(event.arguments[0]):
            self.auth.logout(event.arguments[0])

    def run(self):
        self.start()

        if self.running:
            self.running = False
            ircd = IRC({"irc": self.config})
            ircd.set_discord(self.discord)
            self.discord.set_irc(ircd)
            ircd.set_thread_lock(self.thread_lock)
            ircd.run()
