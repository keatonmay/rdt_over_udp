import socket
import optparse
import pickle
import hashlib
import time

parse = optparse.OptionParser()
parse.add_option('-i', dest='ip', default='127.0.0.1')
parse.add_option('-p', dest='port', default=12345)
(options, args) = parse.parse_args()

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((options.ip,options.port))
sock.settimeout(3)

expectedseqnum=1
nak = []

f = open('test.txt','w')
f.write('BEGIN FILE\n')
f.flush()

EOF = False #boolean for whether end of file is reached
lastpktreceived = time.time()

while True:

	try:
		rcvpkt=[]
		packet,addr= sock.recvfrom(1024)
		rcvpkt = pickle.loads(packet)
		c = rcvpkt[-1] #-1 gets the last item in received packets (last index is check value)
		del rcvpkt[-1]
		h = hashlib.md5() #hash calculate checksum
		h.update(pickle.dumps(rcvpkt))
		if c == h.digest(): #if c == h.digest, packets received in order
			if(rcvpkt[0]==expectedseqnum): #recieved seq num == expected seq num?
				if rcvpkt[1]:
					#writing address, seq number, data
					f.write("%s: %d : %s\n" % (addr, rcvpkt[0], rcvpkt[1:]))
					f.flush()
				else: #if empty, reached end of file
					EOF = True
				expectedseqnum = expectedseqnum + 1
				sndpkt = [] #send packets back for ACK (expectedseq,ACK, checksum)
				sndpkt.append(expectedseqnum) #send back updated expected seq num
				sndpkt.append('ACK')
				h = hashlib.md5()
				h.update(pickle.dumps(sndpkt))
				sndpkt.append(h.digest())
				sock.sendto(pickle.dumps(sndpkt), (addr[0], addr[1]))
			else:
				print("ERROR expected %s, got %s" % (expectedseqnum, rcvpkt[0]))
				sndpkt = [] #send packets back for ACK (expectedseq,NAK, checksum)
				sndpkt.append(expectedseqnum) #send back updated expected seq num
				sndpkt.append('NAK')
				h = hashlib.md5()
				h.update(pickle.dumps(sndpkt))
				sndpkt.append(h.digest())
				nak.append(sndpkt)
				sock.sendto(pickle.dumps(sndpkt), (addr[0], addr[1]))
		else:
			print("ERROR") #unreachable
	except:
		if EOF:
			f.write("END OF FILE")
			f.flush()
			if(time.time()-lastpktreceived>3): #timeout is 3
				break
f.close()