#!/usr/bin/env python3

import irc.bot
import re


class IRC(irc.bot.SingleServerIRCBot):
    thread_lock = None
    running = True

    config = None
    connection = None
    discord = None

    def __init__(self, config):
        irc.client.ServerConnection.buffer_class.encoding = "latin-1"
        irc.bot.SingleServerIRCBot.__init__(self, [
            (config["SERVER"],
             config["PORT"])],
            config["NICK"],
            "SwiftRPG")

        self.config = config

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
                print("[IRC] [{}] {}".format(event.target, message))
                # message = "**<{:s}>** {:s}".format(
                #     re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), message)
                # self.discord.privmsg(
                #     self.config['CHANNELS'][event.target], message)

    # def on_action(self, connection, event):
    #     if (event.target in self.config['CHANNELS']):
    #         with self.thread_lock:
    #             message = event.arguments[0].strip()
    #             message = "* {:s} {:s}".format(
    #                 re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), message)
    #             self.discord.privmsg(
    #                 self.config['CHANNELS'][event.target], message)

    def run(self):
        self.start()

        if self.running:
            self.running = False
            ircd = IRC({"irc": self.config})
            ircd.set_discord(self.discord)
            self.discord.set_irc(ircd)
            ircd.set_thread_lock(self.thread_lock)
            ircd.run()