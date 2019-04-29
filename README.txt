CS 4390.003
Keaton May
Humberto Arana
Ariel Quintanilla

These python scripts implement Go-Back-N and Selective Repeat RDT protocols over an unreliable UDP connection. The scripts were built to run on mininet: http://mininet.org/, which has affected the usability of the scripts a little bit.

For now, to run either protocol, you must alter the file name in rdt_udp_topo.py, where you can also change the delay and loss of the simulated topology. Similarly, parameters must be set in their respective sndr scripts.

Settable parameters include:
CORRUPT_PROBA - probability of single bit corruption
payload_size - size of payload in udp packet
windowsize - size of sliding window in the protocol
timeout - time (in seconds) before a timeout event occurs

When the parameters, protocol and network topology are configured to your liking, simply run:

sudo -E python rdt_udp_topo.py

then wait 2-20 seconds, depending on the configuration, to quit the mininet CLI.

The output for sender and receiver will be written to s.out and r.out respectively and contain the variables required by the assignment. One bug we've run into is that sometimes the receiver will have received but has not accounted for a packet or two in the output. If this is the case, run the program once or twice more and it should provide the proper output.

IMPORTANT NOTE: r.out and s.out will not be written until the scripts have completed. If r.out and s.out have not changed from a previous execution or do not exist, run the command again and wait a bit longer.