import logging
import binascii
import struct
import bitarray
import time

# Do nothing.
CMD_NOP = 0x00

# Update the LCD.
CMD_DRAW = 0x01

# A key was pressed or released. Notify client of the new key states.
CMD_KEYSTATE = 0x02

KEY_LEFT = 0
KEY_RIGHT = 1
KEY_UP = 2
KEY_DOWN = 3
KEY_CENTER = 4

# Each network message has a header that encodes the length of the message
# (header + payload) and a command byte.
MessageHeader = struct.Struct('!HB')

def hexstring(buffer):
    return binascii.hexlify(buffer)

def encode_message(command, payload):
    msg = bytearray()
    msg.extend(MessageHeader.pack(MessageHeader.size + len(payload), command))
    msg.extend(payload)
    return msg

def decode_message(message):
    length, command = MessageHeader.unpack_from(str(message), 0)
    payload = message[MessageHeader.size:]
    return length, command, payload

def read_message(sock):
    message = bytearray()
    header = sock.recv(MessageHeader.size)
    if not header:
        return None
    message.extend(header)
    length, command = MessageHeader.unpack(str(message))
    logging.debug('Getting message of length %i (command=0x%.2x)', length, command)
    remaining = length - MessageHeader.size
    while remaining > 0:
        logging.debug('Still need %i remaining bytes', remaining)
        chunk = sock.recv(remaining)
        message.extend(chunk)
        remaining -= len(chunk)
    return message

def write_message(sock, message):
    logging.debug('Sending message %s', hexstring(message[:32]))
    sock.sendall(message)

def encode_bitmap(bitmap):
    """Return a bytearray with the encoded bitmap data."""
    return bitarray.bitarray(bitmap).tobytes()

def decode_bitmap(bitmap):
    """Return an iterable that contains a 0 for every pixel that is off, and a 1 for every pixel that is on."""
    b = bitarray.bitarray()
    b.frombytes(bytes(bitmap))
    return bytearray(b.unpack(one='\x01'))

if __name__ == '__main__':
    p = bytearray()
    p.extend([0xDE, 0xAD, 0xBE, 0xEF])
    msg = encode_message(0x01, p)
    print hexstring(msg)
    a,b,c = decode_message(msg)
    print a, b, hexstring(c)

    inb = [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    outb = decode_bitmap(encode_bitmap(inb))
    print [str(x) for x in inb]
    print [str(x) for x in outb]
    if outb[0]:
        print 'aaa'
    print hexstring(outb)

    s = time.time()
    for i in range(10000):
        # 3.66
        decode_bitmap(encode_bitmap([0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]))
    print 'benchmark:', time.time() - s
