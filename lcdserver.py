# -*- coding: utf-8 -*-
import binascii
import socket
import time
import logging
import fakelcd
import random
import time
import protocol
import threading
import Queue


command_queue = Queue.Queue()
csock = None
logging.basicConfig(level=logging.DEBUG)

def handle_client(clientsocket):
    global csock
    csock = clientsocket
    try:
        while True:
            message = protocol.read_message(clientsocket)
            if not message:
                break
            print 'got message', binascii.hexlify(message[:20])
            l, c, p = protocol.decode_message(message)
            command_queue.put((c, p))
    finally:
        clientsocket.close()
        logging.info('Client disconnected')
        csock = None

def server_netloop():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('0.0.0.0', 7998))
    serversocket.listen(1)

    try:
        while True:
            (clientsocket, address) = serversocket.accept()
            logging.info('Client connected from %s', address)
            handle_client(clientsocket)
    finally:
        serversocket.close()

def server_main():
    """
    Read input and render at a fixed frame rate of 60 Hz.
    """
    ALL_KEYS = [fakelcd.KEY_LEFT, fakelcd.KEY_RIGHT, fakelcd.KEY_UP, fakelcd.KEY_DOWN, fakelcd.KEY_CENTER]
    logger = logging.getLogger('server')
    logger.info('starting up')
    fakelcd.init()
    keystates = [0] * len(ALL_KEYS)
    prev_keystates = list(keystates)
    while not fakelcd.should_quit:
        fakelcd.pollkeys()
        for index, key in enumerate(ALL_KEYS):
            keystates[index] = fakelcd.keydown(key)
        if keystates != prev_keystates and csock:
            message = protocol.encode_message(protocol.CMD_KEYSTATE, bytearray(keystates))
            protocol.write_message(csock, message)
        prev_keystates = list(keystates)

        if not command_queue.empty():
            command, payload = command_queue.get()
            print 'got cmd', command
            if command == protocol.CMD_BITBLT:
                fakelcd.update(protocol.decode_bitmap(payload))

        time.sleep(1.0 / 60.0)

network_thread = threading.Thread(target=server_netloop)
network_thread.start()
server_main()
