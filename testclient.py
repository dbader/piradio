import binascii
import socket
import sys
import protocol
import logging

logging.basicConfig(level=logging.DEBUG)

HOST, PORT = "localhost", 7998
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    msg = protocol.encode_message(protocol.CMD_BITBLT, bytearray([0] * (128 * 64)))
    protocol.write_message(sock, msg)

    # Receive data from the server and shut down
    while True:
        received = protocol.read_message(sock)
        print protocol.decode_message(received)
finally:
    sock.close()
