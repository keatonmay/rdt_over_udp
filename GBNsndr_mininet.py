import socket, optparse
import pickle

#MESSAGE = "Hello world"

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nextseqnumber = 0
base = 0
windowsize = 10

numTransmits = 0
numRetransmits = 0
numTOevents = 0
numBytes = 0
numCorrupts = 0


buffer = 100
f = open("./500K.txt","rb")
data = f.read(buffer)

while(data):
    if nextseqnumber < base + windowsize:
        packet = []
        packet.append(nextseqnumber)
        packet.append(data)
        if sock.sendto(pickle.dumps(packet), (options.ip, options.port)):
            nextseqnumber = (nextseqnumber+1)%256
            numTransmits += 1
            numBytes += len(packet[1])
            print(len(packet[1]))
            data = f.read(buffer)
    else:
        break
