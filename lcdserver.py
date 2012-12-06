# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)

import binascii
import socket
import time
import logging
import random
import time
import threading
import Queue

import protocol
# import fakelcd as lcd
import lcd

LCD_SLEEPTIME = 60 * 5

HOST = '0.0.0.0'
PORT = 7998

command_queue = Queue.Queue()
csock = None

def handle_client(clientsocket):
    global csock
    csock = clientsocket
    try:
        while True:
            message = protocol.read_message(clientsocket)
            if not message:
                logging.debug('Got empty message')
                break
            logging.debug('Got message %s', protocol.hexstring(message[:32]))
            msglen, cmd, payload = protocol.decode_message(message)
            logging.info('Enqueueing command 0x%.2x of length %i', cmd, msglen)
            command_queue.put((cmd, payload))
    finally:
        clientsocket.close()
        logging.info('Client disconnected')
        csock = None

def server_netloop():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.listen(1)
    try:
        while True:
            logging.info('Waiting for client to connect')
            clientsocket, address = serversocket.accept()
            logging.info('Client connected from %s', address)
            handle_client(clientsocket)
    finally:
        serversocket.close()
    logging.info('Exiting network thread mainloop')

sleeptime = None
sleeping = False

def shouldsleep():
    return time.time() > sleeptime

def resetsleep():
    global sleeptime
    sleeptime = time.time() + LCD_SLEEPTIME
    logging.debug('Sleeptime set to %f', sleeptime)

def sleep():
    logging.info('Going to sleep')
    lcd.set_backlight_enabled(False)
    global sleeping
    sleeping = True

def wakeup():
    logging.info('Waking up')
    lcd.set_backlight_enabled(True)
    global sleeping
    sleeping = False

def server_main():
    """Read input and update the display at a fixed frame rate."""
    logger = logging.getLogger('server')
    logger.info('Starting up')
    lcd.init(debug=True)
    lcd.set_backlight_enabled(True)
    keystates = None
    prev_keystates = None
    resetsleep()
    while True:
        if not sleeping and shouldsleep():
            sleep()
        elif sleeping and not shouldsleep():
            wakeup()
            resetsleep()

        while not csock:
            time.sleep(0.25)
        keystates = lcd.readkeys()
        if keystates != prev_keystates:
            resetsleep()
            logging.debug('Sending keystates %s', keystates)
            message = protocol.encode_message(protocol.CMD_KEYSTATE, bytearray(keystates))
            protocol.write_message(csock, message)
        prev_keystates = keystates

        if not command_queue.empty():
            command, payload = command_queue.get()
            logging.info('Handling command 0x%.2x', command)
            if command == protocol.CMD_DRAW:
                newfb = protocol.decode_bitmap(payload)
                logging.debug('Updating framebuffer')
                lcd.update(newfb)

        time.sleep(1.0 / 30.0)
    logging.info('Exiting mainloop.')

network_thread = threading.Thread(target=server_netloop)
network_thread.start()
server_main()
