#!/usr/bin/env python3

import asyncio
import irc.bot
import os
import ssl


class IRC(irc.bot.SingleServerIRCBot):
    running = True

    config = None
    connection = None

    game = None
    auth = None

    def __init__(self, config, game, auth):
        ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)

        irc.client.ServerConnection.buffer_class.encoding = "latin-1"
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(config["IRC_SERVER"], config["PORT"])],
            config["NICK"],
            "SwiftRPG",
            connect_factory=ssl_factory,
        )

        self.config = config
        self.game = game
        self.game.set_irc_privmsg(self.privmsg)
        self.auth = auth

    def close(self):
        self.running = False
        self.connection.quit("Adios!")

    def privmsg(self, target, message):
        if message:
            self.connection.privmsg(target, message.strip())

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        self.connection = connection

        if len(self.config["PASSWORD"]):
            self.connection.privmsg(
                "NickServ", "IDENTIFY {}".format(self.config["PASSWORD"])
            )

        connection.join(",".join([channel for channel in self.config["CHANNELS"]]))

    def on_pubmsg(self, connection, event):
        if event.target in self.config["CHANNELS"]:
            message = event.arguments[0].strip()
            split = message.split()
            print("[IRC] [{}] ({}) {}".format(event.target, event.source.nick, message))
            if (
                message.startswith("+")
                or message.startswith("-")
                or message.startswith("!")
                or message.startswith("@")
                or message.startswith(".")
            ):
                if split[0][1:] == "help":
                    self.privmsg(
                        event.target, "{}/help".format(self.config["API_HOSTNAME"])
                    )
                    return
                elif split[0][1:] == "login":
                    if len(split) != 2:
                        self.privmsg(
                            event.target,
                            "Syntax: {} <token from {}/user>".format(
                                split[0], os.getenv("API_HOSTNAME")
                            ),
                        )
                        return

                    response = self.auth.login(
                        self.game,
                        self.privmsg,
                        event.target,
                        event.source.nick,
                        split[1],
                    )

                    if response and "name" in response:
                        self.privmsg(
                            event.target,
                            "[{}] 🔑 Successfully logged in".format(
                                response.get("name"),
                            ),
                        )
                    else:
                        self.privmsg(
                            event.target,
                            "[{}] 🔑 Error: invalid token".format(event.source.nick),
                        )
                    return
                elif split[0][1:] == "logout":
                    if self.auth.check(event.source.nick):
                        self.auth.logout(event.source.nick)
                        self.privmsg(event.target, "Logout successful!")
                    else:
                        self.privmsg(event.target, "You are not logged in.")
                    return
                elif split[0][1:] == "loggedin":
                    if self.auth.check(event.source.nick):
                        self.privmsg(event.target, "Logged in!")
                    else:
                        self.privmsg(event.target, "Not currently logged in.")
                    return
                elif not self.auth.check(event.source.nick):
                    self.privmsg(event.target, "You are not logged in.")
                    return
                print(
                    "[IRC] [{}] CMD DETECTED: ({}) {}".format(
                        event.target, event.source.nick, message
                    )
                )
                loop = asyncio.new_event_loop()
                try:
                    loop.run_until_complete(
                        self.game.command(
                            self.auth,
                            self.privmsg,
                            event.target,
                            event.source.nick,
                            message,
                        )
                    )
                finally:
                    loop.close()

    def on_privmsg(self, connection, event):
        message = event.arguments[0].strip()
        split = message.split()

        print("[IRC] [{}] ({}) {}".format(event.target, event.source.nick, message))

        if (
            message.startswith("+")
            or message.startswith("-")
            or message.startswith("!")
            or message.startswith("@")
            or message.startswith(".")
        ):
            if split[0][1:] == "login":
                if len(split) != 2:
                    self.privmsg(
                        event.source.nick,
                        "Syntax: {} <token from {}/user>".format(
                            split[0], os.getenv("API_HOSTNAME")
                        ),
                    )
                    return

                response = self.auth.login(event.source.nick, split[1])

                if response and "name" in response:
                    self.privmsg(
                        event.source.nick,
                        "[{}] 🔑 Successfully logged in".format(
                            response.get("name"),
                        ),
                    )
                else:
                    self.privmsg(
                        event.source.nick,
                        "[{}] 🔑 Error: invalid token".format(event.source.nick),
                    )
                return
            elif split[0][1:] == "register":
                self.privmsg(
                    event.source.nick,
                    "Syntax: {} <token from {}/user>".format(
                        split[0], os.getenv("API_HOSTNAME")
                    ),
                )
            elif split[0][1:] == "logout":
                if self.auth.check(event.source.nick):
                    self.auth.logout(event.source.nick)
                    self.privmsg(event.source.nick, "Logout successful!")
                else:
                    self.privmsg(event.source.nick, "You are not logged in.")
            elif split[0][1:] == "loggedin":
                if self.auth.check(event.source.nick):
                    self.privmsg(event.source.nick, "Logged in!")
                else:
                    self.privmsg(event.source.nick, "Not currently logged in.")
            elif split[0][1:] == "help":
                self.privmsg(
                    event.source.nick, "{}/help".format(self.config["API_HOSTNAME"])
                )

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
        if event.target in self.config["CHANNELS"] and self.auth.check(
            event.arguments[0]
        ):
            self.auth.logout(event.arguments[0])

    def run(self):
        self.start()

        if self.running:
            self.running = False
            ircd = IRC({"irc": self.config})
            ircd.run()
