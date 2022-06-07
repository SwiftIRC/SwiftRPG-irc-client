#!/usr/bin/env python3

import asyncio
import json
import os
import signal
import sys
import threading

from ircd import *
from discordd import *
from dotenv import load_dotenv

print("Loading SwiftRPG...")

load_dotenv()

irc_thread_lock = threading.Lock()
discord_thread_lock = threading.Lock()

config = {
    'TOKEN': os.getenv('TOKEN'),
    'NICK': os.getenv('NICK'),
    'SERVER': os.getenv('SERVER'),
    'PORT': int(os.getenv('PORT')),
    'CHANNELS': json.loads(os.getenv('CHANNELS'))
}

def discord(argv):
    print("Connecting to Discord... ({})".format(argv))

    discord_process = Discord(config)
    discord_process.set_thread_lock(discord_thread_lock)
    
    discord_process.run()

def irc(argv):
    print("Connecting to IRC... ({})".format(argv))

    irc_process = IRC(config)
    irc_process.set_thread_lock(irc_thread_lock)

    thread = threading.Thread(target=irc_process.run)
    thread.daemon = True
    thread.start()

    return thread, irc_process

def accept_input():

    print("Accepting input...")
    while True:
        cmd = input("$ ")

        ## TODO: Add commands
        if cmd == "exit":
            exit(0)




def main(argv):
    irc_thread, irc_process = irc(argv)

    input_thread = threading.Thread(target=accept_input)
    input_thread.daemon = True
    input_thread.start()
    
    discord(argv) # This keeps the main thread alive
    irc_process.close() # If we reach here, then close the IRC connection


def handler(signum, frame):
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    args = sys.argv[1:]
    print("Launching main() with args: {}".format(args))
    main(args)