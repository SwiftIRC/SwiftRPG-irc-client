#!/usr/bin/env python3

import http.server
import os
import ssl


class WebhookServer:
    irc = None
    config = {}

    def __init__(self, configuration, ircd):
        self.config = configuration
        self.irc = ircd

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
                self.config['WEBHOOK_HOST'],
                self.config['WEBHOOK_PORT']
            ),
            lambda *args, **kwargs: CustomRequestHandler(
                *args, ircd=self.irc, configuration=self.config, **kwargs)
        )
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

        # Start the server
        print(
            f"WebhookServer started on https://0.0.0.0:{self.config['WEBHOOK_PORT']}"
        )
        httpd.serve_forever()


class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, ircd, configuration, **kwargs):
        self.irc = ircd
        self.config = configuration

        super().__init__(*args, **kwargs)

    def do_GET(self):
        print("Received a GET request from", self.client_address)
        if self.path == '/':
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
                    self.irc.irc_privmsg(channel, data.decode())
