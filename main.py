#!/usr/bin/env python3

import asyncio
import json
import os
import signal
import sys
import threading
import urllib3


from auth import *
from ircd import *
from game import *
from webhook import *
from dotenv import load_dotenv

print("Loading SwiftRPG...")

load_dotenv()

config = {
    'NICK': os.getenv('NICK'),
    'PASSWORD': os.getenv('PASSWORD'),
    'IRC_SERVER': os.getenv('IRC_SERVER'),
    'PORT': int(os.getenv('PORT')),
    'CHANNELS': json.loads(os.getenv('CHANNELS')),
    'API_HOSTNAME': os.getenv('API_HOSTNAME'),
    'CERTIFICATE_PATH': os.getenv('CERTIFICATE_PATH'),
    'PRIVATE_KEY_PATH': os.getenv('PRIVATE_KEY_PATH'),
    'WEBHOOK_HOST': os.getenv('WEBHOOK_HOST'),
    'WEBHOOK_PORT': int(os.getenv('WEBHOOK_PORT')),
    'SSL_VERIFY': bool(int(os.getenv('SSL_VERIFY'))),
    'API_TOKEN': os.getenv('API_TOKEN'),
    'CLIENT_ID': os.getenv('CLIENT_ID'),
}

if not config['SSL_VERIFY']:
    urllib3.disable_warnings()


def irc(argv, game, auth):
    print("Connecting to IRC... ({})".format(argv))

    irc_process = IRC(config, game, auth)

    irc_process.run()


def input_thread():
    input_thread = threading.Thread(target=accept_input)
    input_thread.daemon = True
    input_thread.start()

    return input_thread


def accept_input():

    print("Accepting input...")
    while True:
        cmd = input("$ ")

        # TODO: Add commands
        if cmd == "exit":
            exit(0)


def game_thread():
    game = Game(config)
    gaming_thread = threading.Thread(target=game.start)
    gaming_thread.daemon = True
    gaming_thread.start()
    return gaming_thread, game


def irc_thread(config, game, auth):
    irc = IRC(config, game, auth)
    irc_thread = threading.Thread(target=irc.start)
    irc_thread.daemon = True
    irc_thread.start()
    return irc_thread, irc


def main(argv):
    auth = Auth()
    gaming_thread, game = game_thread()

    ircd_thread, irc = irc_thread(config, game, auth)

    webhook_server = WebhookServer(config, game, irc)
    webhook_server.run()


def handler(signum, frame):
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    args = sys.argv[1:]
    print("Launching main() with args: {}".format(args))
    main(args)
