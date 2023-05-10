#!/usr/bin/env python3

import asyncio
import json
import os
import socket
import ssl
import time
import threading

import API.api as api


# class HTTPServerV6(HTTPServer):
#     address_family = socket.AF_INET6


class WebhookServer:
    config = {}
    irc = None
    game = None

    def __init__(self, config, game, irc):
        self.config = config
        self.irc = irc
        self.game = game

    def run(self):
        # Set up the SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            certfile=self.config["CERTIFICATE_PATH"],
            keyfile=self.config["PRIVATE_KEY_PATH"],
        )

        addr = (self.config["WEBHOOK_LISTEN"], self.config["WEBHOOK_PORT"])

        # Create the HTTP server with SSL enabled
        if socket.has_dualstack_ipv6():
            try:
                server = socket.create_server(
                    addr, family=socket.AF_INET6, dualstack_ipv6=True
                )
            except:
                server = socket.create_server(addr)
        else:
            server = socket.create_server(addr)

        sock = ssl_context.wrap_socket(server, server_side=True)

        sock.listen()
        print(
            f"WebhookServer started on https://{self.config['WEBHOOK_LISTEN']}:{self.config['WEBHOOK_PORT']}{self.config['WEBHOOK_PATH']}"
        )

        http_thread = self.start_http_thread(sock)

        while True:
            asyncio.run(self.register())
            time.sleep(300)

    def start_http_thread(self, sock):
        http_thread = threading.Thread(target=self.listen, args=(sock,))
        http_thread.daemon = True
        http_thread.start()
        return http_thread

    def listen(self, sock):
        while True:
            conn, addr = sock.accept()
            print(f"Received connection from {addr}")
            try:
                asyncio.run(self.handle_connection(conn, addr))
            except Exception as e:
                print("Error handling connection:", e)

    # Posts to the server to register/update the client
    async def register(self):
        data = {
            "client-id": self.config["CLIENT_ID"],
            "webhook_port": self.config["WEBHOOK_PORT"],
            "webhook_path": self.config["WEBHOOK_PATH"],
        }
        if len(self.config["WEBHOOK_ADDRESS"]) > 0:
            data["webhook_address"] = self.config["WEBHOOK_ADDRESS"]

        if self.config["DEBUG"]:
            print("Registering client with data:", data)

        return await api.post(
            self.game,
            self.irc.privmsg,
            self.config["NICK"],
            self.config["API_TOKEN"],
            "client/register",
            data,
        )

    async def handle_connection(self, conn, addr):
        # This function will be called whenever a new connection is received
        with conn:
            data = conn.recv(1024)
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n\r\n")
            if not data:
                return
            payload = data.decode("latin-1")
            print(f"Received data from {addr}")
            found = False
            authorized = False
            correct_path = False
            headers = []
            for line in payload.split("\r\n"):
                if found and authorized and correct_path:
                    print(f'Payload: "{line}"')
                    await self.handle_payload(line)
                elif len(line) > 0 and not found:
                    split = line.split(": ", 1)
                    headers.append(split)
                    if (
                        split[0] == "X-Bot-Token"
                        and split[1] == self.config["API_TOKEN"]
                    ):
                        authorized = True
                    elif " " in split[0]:
                        split = line.split()
                        if (
                            split[0] == "POST"
                            and split[1] == self.config["WEBHOOK_PATH"]
                        ):
                            correct_path = True
                else:
                    # Finding a blank line here means
                    # we've reached the end of the headers.
                    found = True

    async def handle_payload(self, line):
        try:
            data = json.loads(line)
            message = data["type"]
            if data["type"] == "command_complete":
                message = "{} has finished {}!".format(
                    data["data"]["user"]["name"],
                    data["data"]["command"]["verb"],
                )
            elif data["type"] == "event_start":
                xp_rewards = [
                    "{}: {}".format(
                        xp["details"]["name"].title(),
                        xp["gained"],
                    )
                    for xp in data["data"]["reward"]["experience"]
                ]
                item_rewards = [
                    "{}: {:,}".format(
                        loot["details"]["name"],
                        loot["gained"],
                    )
                    for loot in data["data"]["reward"]["loot"]
                ]
                message = "{} | Rewards: [ (loot) {} | (xp) {} ]".format(
                    data["data"]["event"]["description"],
                    ", ".join(item_rewards),
                    ", ".join(xp_rewards),
                )
            elif data["type"] == "event_ending":
                message = "The `{}` event is ending in {} seconds!".format(
                    data["data"]["event"]["name"],
                    data["data"]["seconds_remaining"],
                )

            for channel in self.config["CHANNELS"]:
                self.irc.privmsg(channel, message)
        except Exception as e:
            print("Error handling payload:", e)
