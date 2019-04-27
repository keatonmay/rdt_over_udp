import socket, optparse
import pickle

parse = optparse.OptionParser()
parse.add_option('-i', dest='ip', default='127.0.0.1')
parse.add_option('-p', dest='port', default=12345)
(options, args) = parse.parse_args()

expectedseqnum = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((options.ip, options.port))

f = open('test.txt','w')
print("this is printing")

while True:
    data, addr = sock.recvfrom(1024)
    recpack = []
    recpack = pickle.loads(data)
    if recpack[0] == expectedseqnum:
        f.write("%s: %d : %s\n" % (addr, recpack[0], recpack[2]))
        f.flush()
        expectedseqnum = (expectedseqnum+1)%256
    ack = []
    ack.append(recpack[0])
    if sock.sendto(pickle.dumps(ack), (addr[0], addr[1])):
        print("ack %d sent" % ack[0])
