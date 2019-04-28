import socket, optparse
import pickle
import checksum

parse = optparse.OptionParser()
parse.add_option('-i', dest='ip', default='127.0.0.1')
parse.add_option('-p', dest='port', default=12345)
(options, args) = parse.parse_args()

expectedseqnum = 0

numBytes = 0
numErrors = 0
numOutOfSeq = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((options.ip, options.port))
sock.settimeout(0.1)

f = open('test.txt','w')

while True:
    try:
        data, addr = sock.recvfrom(1024)
        #receive packet
        recpack = []
        recpack = pickle.loads(data)
    
        #perform checksum
        packetcheck = checksum.addbits(recpack[2])
        packetcheck += recpack[1]

        #print(expectedseqnum)
        #print(recpack[0])
    
        #if checksum returns 1's
        if(packetcheck == 0xFFFF):
            if recpack[0] == expectedseqnum:
                f.write("%s: %d : %s\n" % (addr, recpack[0], recpack[2]))
                f.flush()
                numBytes += len(recpack[2])
                expectedseqnum = (expectedseqnum+1)%256
            elif recpack[0] > expectedseqnum:
                numOutOfSeq += 1
            ack = []
            ack.append(recpack[0])
            sock.sendto(pickle.dumps(ack), (addr[0], addr[1]))
        else:
            print("checksum error")
            numErrors += 1

    except:
        break

print("number of bytes received: ", numBytes)
print("number of checksum errors: ", numErrors)
print("number of out of order packets received: ", numOutOfSeq)
