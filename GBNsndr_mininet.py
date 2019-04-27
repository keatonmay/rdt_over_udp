import socket, optparse
import pickle
import time
import checksum
import flipbits

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

packetsinwindow = []

buffer = 100
f = open("./500K.txt","rb")
data = f.read(buffer)
lastack = time.time()

while(data):
        if nextseqnumber <= (base + windowsize):
                packet = []
                #print(len(packetsinwindow))
                # add bits and take one's complement to compute checksum
                data = bytearray(data)
                packchecksum = checksum.addbits(data)
                packchecksum = packchecksum + (packchecksum >> 16)
                packchecksum = ~packchecksum & 0xFFFF
                #flipbits.flipbits(data, 3)
                packet.append(nextseqnumber)
                packet.append(packchecksum)
                packet.append(data)
                #print ("%s : %s : %s" % (bin(packet[0]), bin(packet[1]), type(packet[2])))
                #print(bin(packchecksum))
                if sock.sendto(pickle.dumps(packet), (options.ip, options.port)):
                        nextseqnumber = (nextseqnumber+1)%256
                        numTransmits += 1
                        packetsinwindow.append(packet)
                        numBytes += len(packet[2])
                        data = f.read(buffer)
        try:
                recdata, addr = sock.recvfrom(2048)
                ack = []
                ack = pickle.loads(recdata)
                if ack[0] == base:
                        #print("ack arrived in order: %s" % ack[0])
                        del packetsinwindow[0]
                        base = (base+1)%256
                        lastack = time.time()
        except:
                if(time.time() - lastack > timeout):
                        print("packet timeout, resending window: %d" % nextseqnumber)
                        numTOevents += 1
                        for i in packetsinwindow:
                                sock.sendto(pickle.dumps(i), (options.ip, options.port))
                        lastack = time.time()
