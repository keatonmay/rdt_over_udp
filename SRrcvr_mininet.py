import socket, optparse
from common import ip_checksum
import pickle

def send(content,destination):
	checksum = ip_checksum
	sock.sendto(checksum + content, destination)

buffer = 1024

#MAIN
parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(options.ip, options.port)

next_seq = 0
dest = (options.ip, options.port)

f = open('test.txt','w')
	
while True:
	data, addr = sock.recvfrom(1024)
	
	checksum = data[:2]
	seq = data[2]
	content = data[3:]
	f.write("%s: %d\n" % (addr, data))

	send("ACK" + seq, dest)
#end