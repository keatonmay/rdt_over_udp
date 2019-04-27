import socket
import optparse
import hashlib
import pickle
import time

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)
(options, args) = parser.parse_args()

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.settimeout(0.001)

#initializes window variables (upper and lower window bounds, position of next seq number)
base=1
nextSeqnum=1
windowSize=7
window = []

numTransmits = 0
numRetransmits = 0
numTOevents = 0
numBytes = 0
numCorrupts = 0

#SENDS DATA
f = open("./500K.txt","rb") 
data = f.read(100)
done = False #boolean to see if file is empty
lastackreceived = time.time()

while not done or window: #windows is not full and data is not empty
	if(nextSeqnum<base+windowSize) and not done:
		sndpkt = [] #seq number, data, checksum (index 0, 1, 2)
		sndpkt.append(nextSeqnum)
		sndpkt.append(data)
		h = hashlib.md5()
		h.update(pickle.dumps(sndpkt))
		sndpkt.append(h.digest())
		sock.sendto(pickle.dumps(sndpkt), (options.ip, options.port))
		nextSeqnum = nextSeqnum + 1 #send and update next seq
		if(not data):
			done = True #no more data to end
		window.append(sndpkt) #add packet to window
		data = f.read(100)
	try:
		packet,addr = sock.recvfrom(1024)
		rcvpkt = [] #receive acks
		rcvpkt = pickle.loads(packet)
		c = rcvpkt[-1] #check value
		del rcvpkt[-1]
		h = hashlib.md5() #checksum calculated
		h.update(pickle.dumps(rcvpkt))
		if c == h.digest(): #if true, then received in order
			#ACKS RECEIVED
			while rcvpkt[0]>base and window:
				lastackreceived = time.time()
				del window[0]
				base = base + 1
		else:
			print("ERROR")
	except:
		if(time.time() - lastackreceived > 0.01): #timout is 0.01
			for i in window:
				sock.sendto(pickle.dumps(i), (options.ip, options.port))

f.close()    
sock.close()
