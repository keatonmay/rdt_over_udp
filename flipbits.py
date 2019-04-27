import random

def flipbits(data, probability):
    if(random.randint(1,101) <= probability):
        data[0] ^= (1 << 0)
    return data

