import socket, optparse
import pickle
import checksum

parse = optparse.OptionParser()
parse.add_option('-i', dest='ip', default='127.0.0.1')
parse.add_option('-p', dest='port', default=12345)
(options, args) = parse.parse_args()

expectedseqnum = 0

### STATISTIC VARIABLES ###
numBytes = 0
numErrors = 0
numOutOfSeq = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((options.ip, options.port))
sock.settimeout(1)

limitnumbers = [i for i in range(0,50)]

alreadyreceived = []

f = open('test.txt','w')

while True:
    try:
        data, addr = sock.recvfrom(2048)
        #receive packet
        recpack = []
        recpack = pickle.loads(data)
    
        #perform checksum
        packetcheck = checksum.addbits(recpack[2])
        packetcheck += recpack[1]
    
        #if checksum returns 1's, send to application (write to text) and send ack if it is the correct packet
        if(packetcheck == 0xFFFF):
                ack = []
                if recpack[0] == expectedseqnum:
                        f.write("%s: %d : %s\n" % (addr, recpack[0], recpack[2]))
                        f.flush()
                        expectedseqnum = (expectedseqnum+1)%256
                        numBytes += len(recpack[2])
                        limitnumbers = [(x+1)%256 for x in limitnumbers]
                        #print("wrote: ", recpack[0])
                # if the packet is greater than expected, buffer it for later use
                elif recpack[0] in limitnumbers and not any(recpack[0] in s1 for s1 in alreadyreceived):
                        #print("received out of order packet: ", recpack[0])
                        numOutOfSeq += 1
                        alreadyreceived.append(recpack)
                        numBytes += len(recpack[2])
                        #print(alreadyreceived)

                # send ack for the packet
                ack.append(recpack[0])
                sock.sendto(pickle.dumps(ack), (addr[0], addr[1]))
                #print("ack sent", recpack[0])
        else:
                #print("checksum error!")
                numBytes += len(recpack[2])
                numErrors += 1
    except:
        break
    # check to see if buffered packets can increase expected sequence number
    newlist = []
    for i in alreadyreceived:
            if expectedseqnum == i[0]:
                    #print("processing already received packet: ", i[0])
                    f.write("%s: %d: %s\n" % (addr, i[0], i[2]))
                    f.flush()
                    expectedseqnum = (expectedseqnum+1)%256
                    #print("wrote: ", i[0])
                    limitnumbers = [(x+1)%256 for x in limitnumbers]
            else:
                    newlist.append(i)
    alreadyreceived = newlist

# print statistic variables
print("number of bytes received: ", numBytes)
print("number of checksum errors: ", numErrors)
print("number of out of order packets received: ", numOutOfSeq)
