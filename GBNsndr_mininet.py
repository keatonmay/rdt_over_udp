import socket, optparse
import pickle
import time
import checksum
import flipbits
import random

#MESSAGE = "Hello world"

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.001)

nextseqnumber = 0
base = 0
windowsize = 10
timeout = 0.022

numTransmits = 0
numRetransmits = 0
numTOevents = 0
numBytes = 0
numCorrupts = 0

CORRUPT_PROBA = 0

packetsinwindow = []

begin = time.time()

buffer = 100
f = open("./500K.txt","rb")
data = f.read(buffer)
lastack = time.time()

while(data):
        if nextseqnumber <= (base + windowsize):
                packet = []
                # add bits and take one's complement to compute checksum
                packchecksum = checksum.addbits(data)
                packchecksum = packchecksum + (packchecksum >> 16)
                packchecksum = ~packchecksum & 0xFFFF
                packet.append(nextseqnumber)
                packet.append(packchecksum)
                packet.append(data)
                packetsinwindow.append(packet)
                print(numTransmits)
                if (random.randint(1,101) <= CORRUPT_PROBA):
                        corruptedData = bytearray(data)
                        corruptedData = flipbits.flipbits(corruptedData)
                        del packet[2]
                        packet.append(corruptedData)
                        numCorrupts += 1
                
                sock.sendto(pickle.dumps(packet), (options.ip, options.port))
                nextseqnumber = (nextseqnumber+1)%256
                numTransmits += 1
                numBytes += len(packet[2])
                data = f.read(buffer)
        try:
                recdata, addr = sock.recvfrom(2048)
                ack = []
                ack = pickle.loads(recdata)
                if ack[0] == base:
                        del packetsinwindow[0]
                        base = (base+1)%256
                        lastack = time.time()
        except:
                if(time.time() - lastack > timeout):
                        numTOevents += 1
                        for i in packetsinwindow:
                                sock.sendto(pickle.dumps(i), (options.ip, options.port))
                        lastack = time.time()
