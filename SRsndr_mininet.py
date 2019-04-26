import socket, optparse
from common import ip_checksum

buffer = 1024

#MAIN
parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(options.ip, options.port)

buffer = 100
seq = 0
dest = (options.ip, options.port)

f = open("./500K.txt","rb")
data = f.read(buffer)
	
while(data):
	packet = []
	packet.append(seq)
	packet.append(data)
	send_sock.sendto(str(seq), dest)
	message, addr = sock.recvfrom(1024)

	print message