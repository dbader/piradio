# -*- coding: utf-8 -*-
import binascii
import socket
import time
import logging
import lcd
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
            # print 'got message', binascii.hexlify(message[:2048])
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
    ALL_KEYS = [lcd.KEY_LEFT, lcd.KEY_RIGHT, lcd.KEY_UP, lcd.KEY_DOWN, lcd.KEY_CENTER]
    logger = logging.getLogger('server')
    logger.info('starting up')
    lcd.init()
    keystates = [0] * len(ALL_KEYS)
    prev_keystates = list(keystates)
    while not lcd.should_quit:
        lcd.pollkeys()
        for index, key in enumerate(ALL_KEYS):
            keystates[index] = lcd.keydown(key)
        if keystates != prev_keystates and csock:
            message = protocol.encode_message(protocol.CMD_KEYSTATE, bytearray(keystates))
            protocol.write_message(csock, message)
        prev_keystates = list(keystates)

        if not command_queue.empty():
            command, payload = command_queue.get()
            print 'got cmd', command
            if command == protocol.CMD_BITBLT:
                newfb = protocol.decode_bitmap(payload)
                # print newfb
                lcd.update(newfb)

        time.sleep(1.0 / 60.0)

network_thread = threading.Thread(target=server_netloop)
network_thread.start()
server_main()
