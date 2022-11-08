#!/usr/bin/env python3

import asyncio
import json
import os
import signal
import sys
import threading

from auth import *
from ircd import *
from game import *
from dotenv import load_dotenv

print("Loading SwiftRPG...")

load_dotenv()

irc_thread_lock = threading.Lock()
game_thread_lock = threading.Lock()

config = {
    'NICK': os.getenv('NICK'),
    'SERVER': os.getenv('SERVER'),
    'PORT': int(os.getenv('PORT')),
    'CHANNELS': json.loads(os.getenv('CHANNELS')),
    'HOSTNAME': os.getenv('HOSTNAME'),
}


def irc(argv, game, auth):
    print("Connecting to IRC... ({})".format(argv))

    irc_process = IRC(config, game, auth)
    irc_process.set_thread_lock(irc_thread_lock)

    irc_process.run


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


def main(argv):
    auth = Auth()
    game = game_thread()

    irc(argv, game, auth)


def handler(signum, frame):
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    args = sys.argv[1:]
    print("Launching main() with args: {}".format(args))
    main(args)
