import socket, optparse
import pickle

parse = optparse.OptionParser()
parse.add_option('-i', dest='ip', default='127.0.0.1')
parse.add_option('-p', dest='port', default=12345)
(options, args) = parse.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((options.ip, options.port))

f = open('test.txt','w')
print("this is printing")

while True:
    data, addr = sock.recvfrom(1024)
    recpack = []
    recpack = pickle.loads(data)
    f.write("%s: %d : %s\n" % (addr, recpack[0], recpack[1]))
    f.flush()
    ack = []
    ack.append(recpack[0])
    ackpack = pickle.dumps(ack)
    if sock.sendto(ackpack, (addr[0], addr[1])):
        print("ack sent")
