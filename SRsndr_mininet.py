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

seqnumwindow = []

### STATISTIC VARIABLES ###
numTransmits = 0
numRetransmits = 0
numTOevents = 0
numBytes = 0
numCorrupts = 0

### SETTABLE PARAMTERS ###
CORRUPT_PROBA = 0
payload_size = 100
windowsize = 10
timeout = 0.02
##########################

packetsinwindow = []
alreadyacked = []
times = []

windownumbers = [i for i in range(windowsize)]

print("Protocol: SR")
print("Corruption probability: ", CORRUPT_PROBA)
print("Payload size: ", payload_size)
print("Window size: ", windowsize)
print("Timeout after: ", timeout)
print("\n \n \n")

begin = time.time()

buffer = payload_size
f = open("./500K.txt","rb")
data = f.read(buffer)
lastack = time.time()

while(data):
        if nextseqnumber < base+windowsize:
                packet = []
                #print("seq num: ", nextseqnumber%256)
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
                times.append(time.time())

                # corrupt a packet with chance CORRUPT_PROBA
                if(random.randint(1,101) <= CORRUPT_PROBA):
                        del packetsinwindow[-1]
                        del times[-1]
                        corruptedData = bytearray(data)
                        corruptedData[0] ^= 0b00000001
                        del packet[2]
                        packet.append(corruptedData)
                        numCorrupts += 1
                else:
                        nextseqnumber += 1
                        data = f.read(buffer)
                # send the packet
                sock.sendto(pickle.dumps(packet), (options.ip, options.port))
                #print("packet sent", packet[0])
                numTransmits += 1
                numBytes += len(packet[2])
        try:
                # try to receive an ack
                recdata, addr = sock.recvfrom(2048)
                ack = []
                ack = pickle.loads(recdata)
                if ack[0] == base%256:
                        #print("received in order ack: ", ack[0])
                        del packetsinwindow[0]
                        del times[0]
                        base += 1
                        windownumbers = [(x+1)%256 for x in windownumbers]

                # if the ack is greater than the base, buffer it for later use
                elif ack[0] in windownumbers and not any(ack[0] in s1 for s1 in alreadyacked):
                        for i in packetsinwindow:
                                if ack[0] == i[0]:
                                        #print("received out of order ack: ", ack[0])
                                        alreadyacked.append(i)
                                        #print(alreadyacked)

                # see if buffered packets can advance the window, and advance the window
                newlist = []
                for i in alreadyacked:
                        #print("searching for already acked packets")
                        if i[0] == base%256:
                                #print("already acked: ", i[0])
                                del packetsinwindow[0]
                                del times[0]
                                base += 1
                                windownumbers = [(x+1)%256 for x in windownumbers]
                        else:
                                newlist.append(i)
                alreadyacked = newlist
        except:
                # resend packets in the window if timeout
                for i in range(len(times)):
                        if(time.time() - times[i] > timeout):
                                numTOevents += 1
                                sock.sendto(pickle.dumps(packetsinwindow[i]), (options.ip, options.port))
                                numRetransmits += 1
                                #print("resent timeout packet", packetsinwindow[i][0])
                                times[i] = time.time()

# print statistic variables on completion
end = time.time()
print("Job completed!")
print("total elapsed time: ", end - begin)
print("number of packets transmitted (excluding retransmits): ", numTransmits)
print("number of bytes sent: ", numBytes)
print("number of timeout events: ", numTOevents)
print("number of retransmitted packets", numRetransmits)
print("number of corrupted packets sent", numCorrupts)
