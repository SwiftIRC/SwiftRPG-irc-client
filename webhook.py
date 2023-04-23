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
            server = socket.create_server(
                addr, family=socket.AF_INET6, dualstack_ipv6=True
            )
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
            asyncio.run(self.handle_connection(conn, addr))

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
            print(f"Received data from {addr}: {payload}")
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
                    found = True
            print(headers)

    async def handle_payload(self, line):
        try:
            data = json.loads(line)
            if data["type"] == "command_complete":
                message = "{} has finished {}!".format(
                    data["data"]["user"]["name"],
                    data["data"]["command"]["verb"],
                )
            elif data["type"] == "event_start":
                xp_rewards = [
                    "{}: {}".format(
                        xp["name"].title(),
                        xp["quantity"],
                    )
                    for xp in data["data"]["reward"]["experience"]
                ]
                item_rewards = [
                    "{}: {:,}".format(
                        loot["name"],
                        loot["quantity"],
                    )
                    for loot in data["data"]["reward"]["loot"]
                ]
                message = "{} | Rewards: [ (loot) {} | (xp) {} ]".format(
                    data["data"]["event"]["description"],
                    ", ".join(item_rewards),
                    ", ".join(xp_rewards),
                )

            for channel in self.config["CHANNELS"]:
                self.irc.privmsg(channel, message)
        except Exception as e:
            print("Error handling payload:", e)


# class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
#     def __init__(self, *args, ircd, configuration, **kwargs):
#         self.irc = ircd
#         self.config = configuration

#         super().__init__(*args, **kwargs)

#     def do_GET(self):
#         print("Received a GET request from", self.client_address)
#         if self.path == "/status":
#             self.send_response(200)
#             self.send_header("Content-Type", "application/json; charset=utf-8")
#             self.end_headers()
#             self.wfile.write(b'{"status": "ok"}')

#     def do_POST(self):
#         print("Received a POST request from", self.client_address)
#         if self.path == self.config["WEBHOOK_PATH"]:
#             data = self.rfile.read(int(self.headers["Content-Length"]))
#             token = self.headers["X-Bot-Token"]
#             print("received: ", data.decode())

#             if token == os.getenv("API_TOKEN"):
#                 self.send_response(200)
#                 self.send_header("Content-Type", "application/json; charset=utf-8")
#                 self.end_headers()

#                 message = ""
#                 json_data = json.loads(data.decode())

#                 if json_data["type"] == "command_complete":
#                     message = "{} has finished {}!".format(
#                         json_data["data"]["user"]["name"],
#                         json_data["data"]["command"]["verb"],
#                     )
#                 elif json_data["type"] == "event_start":
#                     xp_rewards = [
#                         "{}: {}".format(
#                             xp["name"].title(),
#                             xp["quantity"],
#                         )
#                         for xp in json_data["data"]["reward"]["experience"]
#                     ]
#                     item_rewards = [
#                         "{}: {:,}".format(
#                             loot["name"],
#                             loot["quantity"],
#                         )
#                         for loot in json_data["data"]["reward"]["loot"]
#                     ]
#                     message = "{} | Rewards: [ (loot) {} | (xp) {} ]".format(
#                         json_data["data"]["event"]["description"],
#                         ", ".join(item_rewards),
#                         ", ".join(xp_rewards),
#                     )

#                 for channel in self.config["CHANNELS"]:
#                     self.irc.privmsg(channel, message)
