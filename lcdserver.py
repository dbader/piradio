# -*- coding: utf-8 -*-
import socket
import time
import logging
import fakelcd
import random
import time
import protocol

logging.basicConfig(level=logging.INFO)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 7998))
serversocket.listen(1)

(clientsocket, address) = serversocket.accept()
print clientsocket, address
# print protocol.decode_message(clientsocket.recv(1024))

message = bytearray()
message.extend(clientsocket.recv(1))
remaining = message[0] - 1
while remaining > 0:
    chunk = clientsocket.recv(remaining)
    message.extend(chunk)
    remaining -= len(chunk)

print protocol.decode_message(message)

clientsocket.close()
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
            if keystates[index] and not prev_keystates[index]:
                eventqueue.put({'name':'key.down', 'key': index})
            elif prev_keystates[index] and not keystates[index]:
                eventqueue.put({'name':'key.up', 'key': index})
        prev_keystates = list(keystates)

        # if framebuffer_needs_redraw.value:
        #     logging.info('redrawing display')
        #     framebuffer_lock.acquire()
        #     fakelcd.update(framebuffer)
        #     framebuffer_lock.release()
        #     framebuffer_needs_redraw.value = False

        time.sleep(1.0 / 60.0)
