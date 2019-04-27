import random

def flipbits(data, probability):
    pos = 1
    mask = 1 << 1
    data[0] = (data[0] ^ mask)
    return data

