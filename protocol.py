import ctypes

CMD_NOP = 0x00
CMD_BITBLT = 0x01
CMD_KEYSTATE = 0x02

class MessageHeader(ctypes.Structure):
    _pack_ = True
    _fields_ = [("message_length", ctypes.c_uint16),
                ("command", ctypes.c_uint8)]

def encode_message(command, payload):
    header = MessageHeader()
    header.message_length = ctypes.sizeof(header) + ctypes.sizeof(payload)
    header.command = command
    return buffer(header) + buffer(payload)

def decode_message(message):
    header = MessageHeader.from_buffer(message)
    # ctypes.memmove(ctypes.addressof(header), message, ctypes.sizeof(header))
    payload = (ctypes.c_uint8 * (header.message_length - ctypes.sizeof(header))).from_buffer(message[ctypes.sizeof(header):])
    # ctypes.memmove(ctypes.addressof(payload), message[ctypes.sizeof(header):], ctypes.sizeof(payload))
    return header.message_length, header.command, payload

def encode_bitmap(bitmap):
    buf = (ctypes.c_uint8 * len(bitmap))()
    for i, v in enumerate(bitmap):
        buf[i] = ctypes.c_uint8(bitmap[i])
    print buf
    return buf

if __name__ == '__main__':
    import binascii
    p = (ctypes.c_uint8 * 4)()
    p[0] = 0xDE
    p[1] = 0xAD
    p[2] = 0xBE
    p[3] = 0xEF
    msg = encode_message(ctypes.c_uint8(0x01), p)
    print binascii.hexlify(msg)

    print binascii.hexlify(bytearray(msg))
    a,b,c = decode_message(bytearray(msg))
    print a, b
    for v in range(ctypes.sizeof(c)):
        print c[v]
