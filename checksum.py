def addbits(data):
    sum = 0
    for i in range(0,len(data),2):
        if i+1 >= len(data):
            sum += data[i] & 0xFF
        else:
            w = ((data[i] << 8) & 0xFF00) + (data[i+1] & 0xFF)
            sum += w

    while (sum >> 16) > 0:
        sum = (sum & 0xFFFF) + (sum >> 16)

    return sum
