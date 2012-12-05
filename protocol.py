import logging
import binascii
import struct

# Do nothing.
CMD_NOP = 0x00

# Update the LCD.
CMD_BITBLT = 0x01

# A key was pressed or released. Notify client of the new key states.
CMD_KEYSTATE = 0x02

# Each network message has a header that encodes the length of the message
# (header + payload) and a command byte.
MessageHeader = struct.Struct('!HB')

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
    message.extend(sock.recv(MessageHeader.size))
    length, command = MessageHeader.unpack(str(message))
    logging.debug('Getting message of length %i (command=0x%x)', length, command)
    remaining = length - MessageHeader.size
    while remaining > 0:
        logging.debug('Still need %i remaining bytes', remaining)
        chunk = sock.recv(remaining)
        message.extend(chunk)
        remaining -= len(chunk)
    return message

def write_message(sock, message):
    logging.debug('Sending message %s', binascii.hexlify(message))
    sock.sendall(message)

if __name__ == '__main__':
    p = bytearray()
    p.extend([0xDE, 0xAD, 0xBE, 0xEF])
    msg = encode_message(0x01, p)
    print binascii.hexlify(msg)
    a,b,c = decode_message(msg)
    print a, b, binascii.hexlify(c)
