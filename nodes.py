import socket, sys, math, re
import random
from subprocess import check_output
import time, thread, threading
from tabulate import tabulate
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from ast import literal_eval
from operator import itemgetter

hash_bit=0
nodes = []
udpserverport=55555

class Peer:   
    state = 1				#online/offline state of the node
    ledger = []				
    bitcoins = 1000
    inlist = []     			#input/output list of transactions
    t_id=0				#transaction id that node will generate
    crecvflag=False
    cwitflag=False
    
    def __init__(self):
    	
        self.state = 1
        self.serverport = 49156
        self.print_ledger()
        self.MyIP=check_output(['hostname', '--all-ip-addresses']) 		#to get the ip address from machine 10.0.0.x
        self.ind=self.MyIP[7:].rstrip() 					#extract x from 10.0.0.x
        self.nodeid = 1000+int(self.ind) 					
        self.dht = {} 								# distibuted hash table
        self.ft = {} 								#finger table
        random_generator= Random.new().read
        self.key=RSA.generate(1024, random_generator) 				#public, private key pair
        
        self.newpk=None
        self.publickey=self.key.publickey()
        self.dht[self.nodeid] = self.publickey
        self.rollbacks=[]
        
        print 'IP address: ', self.MyIP
        print 'NodeID ', self.nodeid
        
        p1=threading.Thread(target=self.tcpservercode) 			#thread for tcp server
       	p1.daemon = True
       	p1.start()
       	time.sleep(0.2)
        
        p2=threading.Thread(target=self.udpservercode) 			#thread for udp server
       	p2.daemon = True
       	p2.start()
        
        p3=threading.Thread(target=self.randomoffon) 			#thread for offline-online
       	p3.daemon = True
       	p3.start()
        
#------------------------------DHT----------------------------------------------------------------->
    
    def print_ft(self):
    	print("Node ID\t  IP addr")
    	print("-------   --------")
    	for i in self.ft:
    	    print("{}\t{}".format(i,self.ft[i]))
    
    def create_ft(self): 						#to create finger table
        self.ft = {}
        j=-1
        
        for i in range(len(nodes)):
            index=nodes[i]
            nid=int(index)+1000
            dist=(nid-self.nodeid)%(2**hash_bit)
            
            if(dist!=0):
                d=math.log(dist, 2)
            
                if(j<d-1):
                    j=int(math.floor(d))
                    self.ft[nid] = '10.0.0.'+str(index)
            
                elif(j==d-1):
                    if((d-math.floor(d)==0 and d<=(2**(hash_bit-1)))):
                        j+=1
                        self.ft[nid] = '10.0.0.'+str(index)
        
        print 'Finger table built for ', self.nodeid, '\n'
        self.print_ft()
 
    def randomoffon(self): 				#to make a node go offline or online with random probability
        global nodes
        time.sleep(30)
        
        while True:
            time.sleep(0.2)
            x=random.randint(1, 100)
            
            if self.state==1 and len(nodes)>2:
                randoff=10
            
                if(randoff==x):
                    print "Going offline", self.nodeid
                    self.state=0
            
                    if int(self.ind) in nodes:
                        nodes.remove(int(self.ind))
            
                    message = str(self.nodeid)+" off"
                    self.udpclientcode(message)
                    time.sleep(35)        
            
            if self.state==0:
                randon=10
            
                if(randon==random.randint(1, 100)):
                    print "Back online", self.nodeid
                    self.state=1
                    nodes=[int(self.ind)]
                    message = str(self.nodeid)+" on"
                    self.udpclientcode(message)
                    time.sleep(35)
    
        
    def node_went_offline(self, t): 			#when other nodes receive a broadcast that a node went offline
        if(self.state==1):
            global nodes
            t=int(t)-1000
            
            if int(t) in nodes:
                nodes.remove(t)
            
            print '\nnode_went_offline', nodes
            
            if int(t)+1000!=self.nodeid:
                self.create_ft()
                    
    
    def node_went_online(self, t): 			#when other nodes receive a broadcast that a node came online
    
        global hash_bit, nodes
    
        if(self.state==1 and int(t)!=self.nodeid):
            t=int(t)-1000
            recvip='10.0.0.'+str(t)
            nodes.append(t)
            
            hash_bit=int(math.ceil(math.log(len(nodes),2)))
            nodes.sort()
            i=nodes.index(int(self.ind))
            nodes=nodes[i:]+nodes[:i]
            print '\nnode_wen_online', nodes
            
            message = str(self.ind) +' '+str(len(nodes))+' udpu'
            self.udpunicastclient(recvip, message)
            self.create_ft()


    def find_pk(self, nid): 				#when a transaction is received, a node begins search for sender IP to get its pk
        b=0
        
        for key in sorted(self.ft, reverse=True):
            
            print 'key searched: ', key
            
            if int(key)==int(nid):
                b=1
                index=int(nid)-1000
                recvip='10.0.0.'+str(index)                
                message = str(self.ind) + ' give_pk'
                self.udpunicastclient(recvip, message)
                break
            
            elif(int(key)<int(nid)):
                b=1
                index=int(key)-1000
                recvip='10.0.0.'+str(index)
                message = str(self.ind)+' '+str(nid) + ' find_ip'
                self.udpunicastclient(recvip, message)
                break
        
        if b==0:
            key=sorted(self.ft)[0]
            index=int(key)-1000
            recvip='10.0.0.'+str(index) 		#recvip means receiver of message and xip means receiver of pk               
            message = str(self.ind)+' '+str(nid) + ' find_ip'
            self.udpunicastclient(recvip, message)

	
    def find_pk_rec(self, xip, nid):			#when a node recursively search for sender IP on other nodes
        b=0
        
        for key in sorted(self.ft, reverse=True):
           
            if int(key)==int(nid):
                b=1
                index=int(nid)-1000
                nip='10.0.0.'+str(index)                
                message = str(nip)+ ' r_ip'
                #print message
                recvip='10.0.0.'+str(xip)
                self.udpunicastclient(recvip, message)
                break
            
            elif(int(key)<int(nid)):
                b=1
                index=int(key)-1000
                recvip='10.0.0.'+str(index) 		#recvip means receiver of message and xip means receiver of pk               
                message = str(xip)+' '+str(nid) + ' find_ip'
                self.udpunicastclient(recvip, message)
                break
        
        if b==0:
            key=sorted(self.ft)[0]
            index=int(key)-1000
            recvip='10.0.0.'+str(index) 		#recvip means receiver of message and xip means receiver of pk               
            message = str(xip)+' '+str(nid) + ' find_ip'
            self.udpunicastclient(recvip, message)
                
    def ret_ip(self, nip):  				#once a node receives sender IP, it sends request to the sender to give its pk
        message = str(self.ind) + ' give_pk'
        self.udpunicastclient(nip, message)
    
	        
    def send_pk(self, temp):				#when sender sends back its pk
        recvip='10.0.0.'+temp              
        message = self.publickey.exportKey() + ' pksent' 
        #print 'send_pk to ', recvip, message
        self.udpunicastclient(recvip, message)

    
        
    def update_ft_ledger(self): 			#when a node becomes offline to online, it has to update both its ledger and ft
        global nodes
        nodes.sort()
        i=nodes.index(int(self.ind))
        nodes=nodes[i:]+nodes[:i]
        
        print nodes
        self.create_ft()
        
        print "num_nodes: ", len(nodes)
        x=random.choice(nodes)
        
        while(int(x)==int(self.ind)):
            x=random.choice(nodes)
            
        reqip='10.0.0.'+str(x)
        message=str(self.ind)+' send_led'
        self.udpunicastclient(reqip, message)
    
#----------------UDP CODES--------------------------------------------------------------------------->

    def select_function(self, temp):
        global nodes, hash_bit
        l=temp.split()
        flag=l[len(l)-1]
        
        if(flag=="off"): 					#broadcast received when a node went offline
            self.node_went_offline(l[0])
        
        elif(flag=="on"): 					#broadcast received when a node came online
            self.node_went_online(l[0])
        
        elif(flag=="udpu"): 					#when a node comes online, other nodes send the no. of online nodes
            nodes.append(int(l[0]))
            if(len(nodes)==int(l[1])):
                hash_bit=int(math.ceil(math.log(len(nodes),2)))
                self.update_ft_ledger()
        elif(flag=="bitc"):     				#when sending bitcoins
		sign=literal_eval(l[4])
		sender=int(l[1])
		hash=SHA256.new(str(sender)).digest()
								#obtain public key of sender from DHT
		if(self.nodeid!=int(l[1])):
		    self.find_pk(int(l[1]))
		
		else:
		    self.newpk=self.publickey    
		
		while(self.newpk is None):
		    continue
		
		if self.newpk.verify(hash,sign)==True:
		    print "verified"
		    self.update_ledger(temp)
		    self.t_id=max(int(l[0]),self.t_id)
		
		else:
		    print "not verified"
	    
		self.newpk=None
        
        elif(flag=="give_pk"): 					#request has come to give my pk to a node
            self.send_pk(l[0])
        
        elif(flag=="pksent"): 					#pk of a node has come
            str1 = temp.rsplit(' ', 1)[0]
            self.newpk= RSA.importKey(str1)
            
        elif(flag=="find_ip"):					#finding ip of the sender node
            if(self.nodeid!=l[1]):
                self.find_pk_rec(l[0],l[1])
            else:
                #print "matched rec"
                message = str(self.MyIP)+ ' r_ip'
                #print message
                recvip='10.0.0.'+str(l[0])
                self.udpunicastclient(recvip, message)
        
        elif(flag=="r_ip"):                     		#ip of the sender node has come from some other node
            self.ret_ip(l[0])
        
        elif(flag=="send_led"):                 		#request has come to send my copy of ledger
            recvip='10.0.0.'+l[0]
            message=str(self.ledger)+' '+str(self.t_id)+' gave_led'
            self.udpunicastclient(recvip, message)
        
        elif(flag=="gave_led"):                 		#ledger received from the node we requested from
            str1 = temp.rsplit(' ', 2)[0]
            self.ledger = literal_eval(str1)
            self.t_id=int(l[len(l)-2])
            self.print_ledger()
        
        elif(flag=="abort"):                    		#to abort the committed transaction
            print 'abort called'
            trans_id = int(l[0])
    	    sender = int(l[1])
    	    receiver = int(l[2])
    	    amount = int(l[3])
            self.rollbacktrans(trans_id, sender, receiver,amount)
        
        elif(flag=="verify"):					#ledger received from the node we requested from
            node = int(l[0])
            sign=literal_eval(l[1])
            hash=SHA256.new(str(self.ledger)).digest()
            
            if((self.nodeid)!=int(node)):
                self.find_pk(int(node))
            
            else:
                self.newpk=self.publickey    
            
            while(self.newpk is None):
                continue
            
            if self.newpk.verify(hash,sign)==True:
                print "Ledger of ",node," is verified"
            
            else:
                print "Ledger of ",node," is not correct"
            
            self.newpk=None
            
            
    def udpserverhandler(self,temp):
        self.select_function(str(temp))
            
    def udpservercode(self):
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        #udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        addr = ('', udpserverport)
        udpsocket.bind(addr)
        
        print 'UDP server created for', self.nodeid, 'at', udpserverport
        
        while True:
            if self.state==1:
                #print 'my stste in server ', self.state, 'bus'
                temp, cliaddr = udpsocket.recvfrom(16384)
        
                if(cliaddr is not None):
                    thread.start_new_thread(self.udpserverhandler, (temp,))
                    cliaddr=None
        
            else:
                temp, cliaddr = udpsocket.recvfrom(1024)
                temp=None
                cliaddr=None
            
		    
    def udpclientcode(self, message):
	    udpcsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	    udpcsocket.bind(('', 0))
	    udpcsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	    udpcsocket.sendto(message, ('10.255.255.255', udpserverport))
	    time.sleep(1)
	    udpcsocket.close()    
	  
    def udpunicastclient(self, recvip, message): 
        udpcsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udpcsocket.bind(('', 0))
        udpcsocket.sendto(message, (recvip,udpserverport))

#----------------TCP CODES--------------------------------------------------------------------------->	    
    
    def tcpserverhandler(self, clientsock, clientip, tup_recvd):

        clientip = clientip[0]
    	clientid = int(clientip[7:(len(clientip)+1)]) + 1000
        
        ver_list=[]
        l=tup_recvd.split()
        amount=int(l[0])
        sign=literal_eval(l[1])
        
        if self.check_ledger(clientid)>=int(amount):
	       myrand = 10
	       
	       #Updation for input list 2
	       for i in range(len(self.ledger)):
		       if (self.ledger[i][2]==clientid) or (self.ledger[i][1]==clientid) :
		          ver_list.append(self.ledger[i])
	       
	       hash=SHA256.new(str(ver_list)).digest()
	       
	       if(self.nodeid!=int(clientid)):
	           self.find_pk(int(clientid))
	       
	       else:
	           self.newpk=self.publickey    
	       
	       while(self.newpk is None):
	           continue
	       
	       if self.newpk.verify(hash,sign)==True:
		   print "SENDER's INPUT LIST VERIFIED"
		   if(myrand != random.randint(1,100)):
		   	clientsock.send('commit')
		   else:
			clientsock.send('transaction aborted')
			print 'transaction aborted'
	       self.newpk=None	    
        
        else:
            print('transaction failed')
        
        clientsock.close()

    def tcpservercode(self):
    	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.MyIP, self.serverport))
        s.listen(5)
        print 'TCP Server started for', self.nodeid
        c=None
        while True:
            c, addr = s.accept()
            tup_recvd=c.recv(1024)
                      
            if c:   
            	thread.start_new_thread(self.tcpserverhandler, (c,addr, tup_recvd))
            	c=None
        s.close()

    def tcpclienthandler(self, msg):
        print 'Client ', self.nodeid, ' wants to send'
        l=str(msg).split()
        serverip=l[0]
        recvid=int(l[4])
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverip, 49156))
        
        s.send(str(l[2])+' '+str(l[5])) 				#sending the amount to receiver/witness
        #time.sleep(2)
        
        x=None
        while(x==None):
            x=s.recv(1024)
        
        amount=int(l[2])
        flag=l[3]
        print flag
        
        if x=='commit':
            if flag=='recv':
                self.crecvflag=True
                
            if flag=='wit':
                self.cwitflag=True
                
        if (self.crecvflag==True and self.cwitflag==True):
                self.t_id += 1 
                hash=SHA256.new(str(self.nodeid)).digest()
                signature=self.key.sign(hash,'')
                message = str(self.t_id)+' '+str(self.nodeid)+' '+str(recvid)+' '+str(amount) + ' ' + str(signature) + ' bitc' 
                self.udpclientcode(message)
                self.crecvflag=False
                self.cwitflag=False		    
        
        if x=='transaction aborted':
            print "transaction aborted by recievr or witness"
         			
        s.close()

    def tcpclientcode(self, msg):
        thread.start_new_thread(self.tcpclienthandler, ((msg,)))
            
#--------------------------------------- LEDGER ---------------------------------------------------------------------->   
    
    def abort_transaction(self, trans_id, sender, receiver, amount):
        container = str(trans_id) + ' '+str(sender)+' '+str(receiver) + ' '+str(amount) + ' abort'
        print 'abort trans called'
        self.udpclientcode(container)
    
    def rollbacktrans(self, trans_id, sender, receiver,amount):
    	print 'rollback'
    	
    	if(len(self.ledger)==0):
        	self.rollbacks.append([trans_id, sender, receiver,amount])
            	print self.rollbacks
    	
    	for i in range(len(self.ledger)):
    	    print '\n',self.ledger[i][0], ' ', trans_id
    	
    	    if (int(self.ledger[i][0])==int(trans_id)):
    	    	print 'match found\n'
        	self.ledger.pop(i)
        
            else:
            	self.rollbacks.append([trans_id, sender, receiver,amount])
            	print self.rollbacks
        
        self.print_ledger()
        
    def update_ledger(self, container):
    	container = container.split()
    	trans_id = int(container[0])
    	sender = int(container[1])
    	receiver = int(container[2])
    	amount = int(container[3])
    	
    	if [trans_id, sender, receiver,amount] in self.rollbacks:
    		print self.rollbacks
    		self.rollbacks.remove([trans_id, sender, receiver,amount])
    		return
    	
    	if(self.nodeid == sender):
    	    amt = self.bitcoins - amount
	
	    if amt<0:
		print 'update ledger'
		self.abort_transaction(trans_id, sender, receiver, amount)
		print 'Updated bitcoins are: ', self.bitcoins
        	self.print_ledger()
		return
	
	    else:
		self.bitcoins = self.bitcoins - amount
    	
    	if(self.nodeid == receiver):
    		self.bitcoins = self.bitcoins + amount
    	
    	self.ledger.append([trans_id, sender, receiver, amount])	
        self.ledger=sorted(self.ledger, key=itemgetter(0))
    	
    	print 'Updated bitcoins are: ', self.bitcoins
        self.print_ledger()
           
    def check_ledger(self,node_id):
	cal = 1000
        
        for i in range(0, len(self.ledger)):
            if self.ledger[i][2]==node_id:
               cal = cal + self.ledger[i][3]
            if self.ledger[i][1]==node_id:
               cal = cal - self.ledger[i][3]
        return cal
   
    def print_ledger(self):
        print tabulate(self.ledger, headers=['Transaction ID', 'Sender', 'Receiver', 'Amount'])
        #print("Trans ID\tSender\t Receiver\t Amount")
    	#print("--------\t------\t --------\t -------")
    	#for i in self.ledger:
    	#   for j in i:
    	#        print j,'\t     ',
    	#    print
      
#----------------------when node wants to send bitcoins-----------------------------#            
    def sender_trans(self,recvip, recvid, amt):		
        sender=self.nodeid
        x=random.choice(nodes)
        
        while(int(x)==int(self.ind) and int(x)==int(int(recvid)-1000)):
            x=random.choice(nodes)
        
        witip='10.0.0.'+str(x)
        witid=1000+x
        amount=int(amt)
        
        if (amount<=self.check_ledger(self.nodeid)):
            myrand = 10
            inlist = []
 
            for i in range(len(self.ledger)):
                if (self.ledger[i][2]==self.nodeid) or (self.ledger[i][1]==self.nodeid) :
                    inlist.append(self.ledger[i])
 
            hash=SHA256.new(str(inlist)).digest()
            DS_inlist=peerobj.key.sign(hash,'')
 
            if(myrand != random.randint(1,10000)):
                msg=str(recvip)+' '+str(recvid)+' '+str(amount)+' '+'recv'+' '+str(recvid)+' '+str(DS_inlist)
                self.tcpclientcode(msg)
                time.sleep(0.2)
                msg=str(witip)+' '+str(witid)+' '+str(amount)+' '+'wit'+' '+str(recvid)+' '+str(DS_inlist)
                self.tcpclientcode(msg)        
 
            else:
                print "Transaction aborted by sender"   
 
        else:
            print 'Not sufficient bitcoins'   	
            
    def trans1(self):
	    if (self.nodeid==1002):
		    recvid = 1004 
		    sendTo = '10.0.0.4'      
		    self.sender_trans(sendTo, recvid, '1000')
    
    def trans2(self):
	    if (self.nodeid==1001):
		    recvid = 1003 			
		    sendTo = '10.0.0.3'      		
		    self.sender_trans(sendTo, recvid, '1000')

if __name__ == '__main__':
   
    num_nodes = int(sys.argv[1])
    peerobj = Peer()
    host_pattern = re.compile("^(h[0-9]+)$")
    amount_pattern = re.compile("([1-9][0-9]*)$")
    
    
    if num_nodes==0:
        nodes=[int(peerobj.ind)]
        message = str(peerobj.nodeid)+" on"
        peerobj.udpclientcode(message)
    else:        
        hash_bit=int(math.ceil(math.log(num_nodes,2)))
        
        for i in range(1,num_nodes+1):
        	nodes.append(i)
        nodes.sort()
        
        i=nodes.index(int(peerobj.ind))
        nodes=nodes[i:]+nodes[:i]
        peerobj.create_ft()
        time.sleep(2)
    
    
    while True:
        opt = raw_input("Please choose:\nPress 1: Send Bitcoins -> \nPress 2: Verify Ledger ->")
        
        if(opt=='1'):
            
            if peerobj.state==1:
                sendTo = raw_input("Whom do you want to send? ")    
		
		while not(host_pattern.match(sendTo)):
			sendTo = raw_input("Please enter a valid host: ")
			
                amount = raw_input("Amount of money to send? ")
                
                while not(amount_pattern.match(amount)):
			amount = raw_input("Please enter a valid amount: ")
			
			
                if int(sendTo[1:]) in nodes:
                    recvid = 1000+int(sendTo[1:])	 #receiver's nodeid
                    
                    sendTo = '10.0.0.'+sendTo[1:]      	 #receiver's ip
                    peerobj.sender_trans(sendTo, recvid, amount)
        
                else:
                    print "Receiver is offline"
                
                time.sleep(0.2)
        
            else:
                print "You are offline!\n"
        
        elif(opt=='2'):
            
            if peerobj.state==1:
		        hash=SHA256.new(str(peerobj.ledger)).digest()
		        DS_ledger=peerobj.key.sign(hash,'')
		        message=str(peerobj.nodeid)+' '+str(DS_ledger)+' verify'
		        peerobj.udpclientcode(message)
"""Debug options:
1. To go offline from main()
	if(opt=='1'):
            if peerobj.state==1 and len(nodes)>2:
                gof=raw_input('want to go offline(Y/N)?')
                if(gof=="y" or gof=="Y"):
                    peerobj.state=0
                    if int(peerobj.ind) in nodes:
                        nodes.remove(int(peerobj.ind))
                    num_nodes-=1
                    message = str(peerobj.nodeid)+" off"
                    peerobj.udpclientcode(message)
		    time.sleep(2)
2. To demonstrate double spent problem
    p5=threading.Thread(target=peerobj.trans1) 
    p6=threading.Thread(target=peerobj.trans2) 
    p5.start()
    p6.start()
    
    time.sleep(2)
    print "Updated bitcoins: ", peerobj.bitcoins

"""
