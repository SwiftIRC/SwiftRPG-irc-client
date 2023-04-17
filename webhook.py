#!/usr/bin/env python3

import asyncio
import http.server
import os
import requests
import ssl
import time
import threading

import API.api as api


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
            certfile=self.config['CERTIFICATE_PATH'],
            keyfile=self.config['PRIVATE_KEY_PATH']
        )

        # Create the HTTP server with SSL enabled
        httpd = http.server.HTTPServer(
            (
                self.config['WEBHOOK_LISTEN'],
                self.config['WEBHOOK_PORT']
            ),
            lambda *args, **kwargs: CustomRequestHandler(
                *args,
                ircd=self.irc,
                configuration=self.config,
                **kwargs
            )
        )
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

        # Start the server
        print(
            f"WebhookServer started on https://{self.config['WEBHOOK_LISTEN']}:{self.config['WEBHOOK_PORT']}{self.config['WEBHOOK_PATH']}"
        )

        http_thread, httpd = self.start_http_thread(httpd)

        while True:
            asyncio.run(self.register())
            time.sleep(300)

    def start_http_thread(self, httpd):
        http_thread = threading.Thread(target=httpd.serve_forever)
        http_thread.daemon = True
        http_thread.start()
        return http_thread, httpd

    # Posts to the server to register/update the client
    async def register(self):
        data = {
            'client-id': self.config['CLIENT_ID'],
            'webhook_port': self.config['WEBHOOK_PORT'],
            'webhook_path': self.config['WEBHOOK_PATH'],
        }
        if len(self.config['WEBHOOK_ADDRESS']) > 0:
            data['webhook_address'] = self.config['WEBHOOK_ADDRESS']

        return await api.post(
            self.game,
            self.irc.privmsg,
            self.config['NICK'],
            self.config['API_TOKEN'],
            'client/register',
            data
        )


class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, ircd, configuration, **kwargs):
        self.irc = ircd
        self.config = configuration

        super().__init__(*args, **kwargs)

    def do_GET(self):
        print("Received a GET request from", self.client_address)
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')

    def do_POST(self):
        print("Received a POST request from", self.client_address)
        if self.path == '/global':
            data = self.rfile.read(int(self.headers['Content-Length']))
            token = self.headers['X-Bot-Token']
            print("received: ", data.decode())

            if token == os.getenv('API_TOKEN'):
                self.send_response(200)
                self.send_header(
                    'Content-Type', 'application/json; charset=utf-8')
                self.end_headers()

                for channel in self.config['CHANNELS']:
                    self.irc.privmsg(channel, data.decode())
