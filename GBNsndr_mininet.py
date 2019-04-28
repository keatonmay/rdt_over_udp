import socket, optparse
import pickle
import time
import checksum
import flipbits
import random

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)

nextseqnumber = 0
base = 0
windowsize = 10
timeout = 0.020

seqnumwindow = []

numTransmits = 0
numRetransmits = 0
numTOevents = 0
numBytes = 0
numCorrupts = 0

CORRUPT_PROBA = 5

packetsinwindow = []

begin = time.time()

buffer = 100
f = open("./500K.txt","rb")
data = f.read(buffer)
lastack = time.time()

while(data):
        if nextseqnumber < base+windowsize:
                packet = []
                # add bits and take one's complement to compute checksum
                packchecksum = checksum.addbits(data)
                packchecksum = packchecksum + (packchecksum >> 16)
                packchecksum = ~packchecksum & 0xFFFF
                
                # create packet
                packet.append(nextseqnumber%256)
                packet.append(packchecksum)
                packet.append(data)

                # add packet with correct data to window
                packetsinwindow.append(packet)
                
                if(random.randint(1,101) <= CORRUPT_PROBA):
                        del packetsinwindow[-1]
                        corruptedData = bytearray(data)
                        corruptedData[0] ^= 0b00000001
                        del packet[2]
                        packet.append(corruptedData)
                        numCorrupts += 1
                else:
                        nextseqnumber += 1
                        data = f.read(buffer)
                sock.sendto(pickle.dumps(packet), (options.ip, options.port))
                numTransmits += 1
                numBytes += len(packet[2])
        try:
                recdata, addr = sock.recvfrom(2048)
                ack = []
                ack = pickle.loads(recdata)
                if ack[0] == base%256:
                        del packetsinwindow[0]
                        base += 1
                        lastack = time.time()
        except:
                if(time.time() - lastack > timeout):
                        numTOevents += 1
                        for i in packetsinwindow:
                                sock.sendto(pickle.dumps(i), (options.ip, options.port))
                        lastack = time.time()
end = time.time()
print("total elapsed time: ", end - begin)
print("number of packets transmitted (excluding retransmits): ", numTransmits)
print("number of bytes sent: ", numBytes)
print("number of timeout events: ", numTOevents)
print("number of corrupted packets sent", numCorrupts)
