import socket, optparse

#MESSAGE = "Hello world"

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

buffer = 1024
f = open("./500K.txt","rb")
data = f.read(buffer)

while(data):
    if sock.sendto(bytes(data), (options.ip, options.port)):
        data = f.read(buffer)
