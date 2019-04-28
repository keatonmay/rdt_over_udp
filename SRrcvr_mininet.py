import socket
import optparse
import pickle
import hashlib
import time
import checksum

parse = optparse.OptionParser()
parse.add_option('-i', dest='ip', default='127.0.0.1')
parse.add_option('-p', dest='port', default=12345)
(options, args) = parse.parse_args()

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((options.ip,options.port))
sock.settimeout(3)

expectedseqnum=1

f = open('test.txt','w')
f.write('BEGIN FILE\n')
f.flush()

EOF = False #boolean for whether end of file is reached
lastpktreceived = time.time()

while True:

	try:
		recpack =[]
		packet,addr= sock.recvfrom(1024)
		recpack  = pickle.loads(packet)
		c = recpack [-1] #-1 gets the last item in received packets (last index is check value)
		del recpack [-1]
		
		# checksum
		#packetcheck = checksum.addbits(recpack[2])
		#packetcheck += recpack[1]
		
		h = hashlib.md5() #hash calculate checksum
		h.update(pickle.dumps(recpack ))
		
		
		if c == h.digest(): #if c == h.digest, packets received in order
			if(recpack [0]==expectedseqnum): #recieved seq num == expected seq num?
				if recpack [1]:
					#writing address, seq number, data
					f.write("%s: %d : %s\n" % (addr, recpack [0], recpack [1:]))
					f.flush()
				else: #if empty, reached end of file
					EOF = True
				expectedseqnum = expectedseqnum + 1
				sndpkt = [] #send packets back for ACK (expectedseq, checksum)
				sndpkt.append(expectedseqnum) #send back updated expected seq num
				h = hashlib.md5()
				h.update(pickle.dumps(sndpkt))
				sndpkt.append(h.digest())
				sock.sendto(pickle.dumps(sndpkt), (addr[0], addr[1]))
			else:
				print("ERROR expected %s, got %s" % (expectedseqnum, recpack [0]))
		else:
			sndpkt = [] #send packets back for ACK
			sndpkt.append(expectedseqnum) #pkts with NAK (expectedseq, checksum)
			h = hashlib.md5()
			h.update(pickle.dumps(sndpkt))
			sndpkt.append(h.digest())
			sock.sendto(pickle.dumps(sndpkt), (addr[0], addr[1]))
	except:
		if EOF:
			f.write("END OF FILE")
			f.flush()
			if(time.time()-lastpktreceived>3): #timeout is 3
				break
f.close()
