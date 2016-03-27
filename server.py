import socket
import sys
from thread import *
import Queue
import time


queue = Queue.Queue()

user1 = 'Mike'
user2 = 'Chao'
user3 = 'Wenhao'
pw1 = '0000'
pw2 = '1111'
pw3 = '2222'
registed_user = [user1,user2,user3]
registed_passwd = [pw1,pw2,pw3]
subscriptionMatrix = [[0,0,0],[0,0,0],[0,0,0]]

# msgbox: (mainly used for hashtag things)
# ['user_name(who put this message)', 'msg', '#', 'hashtag', '#']
# ['user_name(who put this message)', 'msg']
# ['user_name(who put this message)', 'msg']
# :
# everymsg should goes to this table
msgbox = []
# msgbox_not: 
# [['from who', 'msg', '#', 'hashtag', '#'], 
#  ['from who', 'msg', 'hashtag'], 
#  ['from who', 'msg', 'hashtag']]
# only 1: subscribed, 2: offline msg should goes to this table, 
msgbox_not = dict([('Mike',[]),('Chao',[]),('Wenhao',[])])
# item:['who' 'subscribe what hashtag']
sub_hashtag = dict([('Mike',[]),('Chao',[]),('Wenhao',[])])
# item:['hashtag', 'who is the subscriber of this hashtag']
lib_hashtag = dict()
conn_list = []
real_conn_list = []

def return_2nd_from_a_list(twoDarray): # functional
	var = []
	for i in twoDarray:
		var.append(i[1])
	return var

def logOut(conn, c, user_name): 
	print 'User ' + user_name[0] +' has log out pool'
	conn.send('confirm log out')
	c.send('confirm log out')
	msgbox_not[user_name[0]] = [] # according to the specification, we must empty this array
	time.sleep(0.3) # wait the client turn it off first
	conn.close()
	c.close()
	for i in range(len(conn_list)):
		if conn_list[i][1] == user_name[0]:
			j = i
	#conn_list.pop(j)
	#real_conn_list.pop(j)
	del conn_list[j]
	del real_conn_list[j]
	while 1:
		time.sleep(1000) # permanetly sleep this thread

def extractName(data): # functional
	name_char = []
	pass_char = []
	delimiter = data.index('$')
	for i in data[:delimiter]:
		name_char.append(i)
	for i in data[(delimiter+1):]:
		pass_char.append(i)
	return ''.join(name_char), ''.join(pass_char)

def extractDelimiter(data): # functional
	if data:
		dollars = [-1]
		dollars = dollars + [i for i,x in enumerate(data) if x == '$']
		dollars = dollars + [len(data)]
		par_str = []
		temp = []
		for i in range(len(dollars)-1):
			for j in data[dollars[i]+1 : dollars[i+1]]:
				temp.append(j)
			par_str.append(''.join(temp))
			temp = []
		#print par_str
		return par_str
	else:
		return []

def isValid(name, pw): # functional
        for i in range(len(registed_user)):
                if registed_user[i] == name:
                        j = i; break
        if 'j' in locals():
                if pw == registed_passwd[j]:
                        return 1
                else:
                        return 0
        else:
                return -1

def addSub(from_whom, to_whom): # functional
        for i in range(len(registed_user)):
                if registed_user[i] == from_whom:
                        j = i
                        break
        for i in range(len(registed_user)):       
                if registed_user[i] == to_whom:
                        k = i
                        break
        if 'j' in locals() and 'k' in locals():
                subscriptionMatrix[j][i] = 1
                return 1
        else:
                return 0

def delSub(from_whom, to_whom): # functional
	for i in range(len(registed_user)):
		if registed_user[i] == from_whom:
			j = i
			break
	for i in range(len(registed_user)):
		if registed_user[i] == to_whom:
			k = i
			break
	if 'j' in locals() and 'k' in locals():
		subscriptionMatrix[j][i] = 0
		return 1
	else:
		return 0

def editSubscriptions(conn, subframe): # functional
	user_name = subframe[1]
	#print 'user name ',user_name
	addORdel = subframe[0]
	#print 'chosen ',addORdel
	hashtag = subframe[-1]
	if hashtag == 'hashtag' and addORdel == 'add':
		hashdata = subframe[-2]
		sub_hashtag[user_name].append(hashdata)
		if hashdata in lib_hashtag.keys():
			lib_hashtag[hashdata].append(user_name)
		else:
			lib_hashtag.update({hashdata:[user_name]})
		#print sub_hashtag[user_name]
	elif hashtag == 'hashtag' and addORdel == 'del':
		#print 'gonna del'
		hashlist = sub_hashtag[user_name]
		if hashlist:
			hashstring = ''
			for i in hashlist:
				hashstring = hashstring + i + '$'
			conn.sendall(hashstring)
			hashname = conn.recv(1024)
			index = sub_hashtag[user_name].index(hashname)
			deletename = sub_hashtag[user_name].pop(index)
			if len(lib_hashtag[deletename]) == 1:
				del lib_hashtag[deletename]
			else:
				for i in lib_hashtag[deletename]:
					if i == user_name:
						index = lib_hashtag[deletename].index(i)
						break
				lib_hashtag[deletename].pop(index)
			conn.sendall(deletename)
		else:
			conn.sendall('no hashtag found')
		
	else:
		reply_list = ''
		for i in registed_user:
			if i != user_name:
				reply_list = reply_list + i + '$'
		conn.sendall(reply_list)
		#print 'reply list',reply_list
		obj_name = conn.recv(1024)
		#print 'src name',user_name
		#print 'object name',obj_name
		if obj_name == 'cancel':
			return 0
		if addORdel == 'add':
			if addSub(user_name, obj_name):
				conn.sendall('s')
			else:
				conn.sendall('server error')
		elif addORdel == 'del':
			if delSub(user_name, obj_name):
				conn.sendall('s')
			else:
				conn.sendall('server error')
		else:
			pass

def parseHash(data): # functional
	msg = []
	hashtag = []
	if '#' in data:
		delimiter = data.index('#')
        	for i in data[:delimiter]:
                	msg.append(i)
        	for i in data[(delimiter+1):]:
                	hashtag.append(i)
        	return 1,''.join(msg), ''.join(hashtag)
	else:
		return 0,data,''

def checkSubscribers(user_name, sel): # functional
	# the subscriptionMatrix is unidirectional
	# raw: from whom
	# col: to whom
	# 
	# param 2: if sel == 1  , then return the follower of user_name
	#		   if sel other , then return who is user_name following
	#print user_name
	#print registed_user
	who_sub = []
	user = registed_user.index(user_name)
	for i in range(len(subscriptionMatrix)):
		if sel == 1:
			if subscriptionMatrix[i][user] == 1:
				who_sub.append(registed_user[i])
		else:
			if subscriptionMatrix[user][i] == 1:
				who_sub.append(registed_user[i])
	return who_sub
	
def postAMessage(conn, c, subframe): # not functional 
	global msgbox, msgbox_not, conn_list, registed_user, subscriptionMatrix, real_conn_list
	msg = subframe[0] 
	user_name = subframe[1]
	hashed,msg,hashtag = parseHash(msg)
	flag = 0
	if subframe[-1] == 'Private Msg':
		obj_name = subframe[2]
		if real_conn_list:
			for i in real_conn_list:
				#print i[1]
				#print obj_name
				if i[1] == obj_name:
					flag = 1
					if hashed:
						i[0].sendall('real time msg: ' + user_name + ': ' + msg + '#' + hashtag)
						msgbox.append([user_name, msg, '#', hashtag, '#'])
					else:
						i[0].sendall('real time msg: ' + user_name + ': ' + msg)
						msgbox.append([user_name, msg])
		else:
			pass				
		if flag == 0:
			if obj_name in registed_user:
				if hashed:
					msgbox_not[obj_name].append([user_name, msg, ' #', hashtag, '#'])
					#print obj_name
					#print msgbox_not[obj_name]
					msgbox.append([user_name, msg, '#', hashtag, '#'])
				else:
					msgbox_not[obj_name].append([user_name, msg, ''])
					#print obj_name
					#print msgbox_not[obj_name]
					msgbox.append([user_name, msg])
			else:
				pass
		else:
			pass
		
	else:
		if hashed:
			msgbox.append([user_name, ':' + msg, '#', hashtag, '#'])
		else:
			msgbox.append([user_name, ':' + msg, ''])		
		# check who is the follower of this posting user
		# and check whether he is online now
		subscriberList = checkSubscribers(user_name, 1) # check who is the follower of user_name
		if subscriberList:
			for j in range(len(subscriberList)):
				for i in range(len(conn_list)):
					if conn_list[i][1] == subscriberList[j]:
						if hashed: #if he/she is in the connection list, then send real time msg
							real_conn_list[i][0].sendall('real time msg: ' + user_name + ': ' + msg + '#' + hashtag) #2nd sign problematic
						else:
							real_conn_list[i][0].sendall('real time msg: ' + user_name + ': ' + msg)
					else:
						pass
			for i in range(len(subscriberList)): #if the follower is not online, put the message in to msgbox_not
				if subscriberList[i] not in return_2nd_from_a_list(conn_list):
					#print subscriberList[i]
					if hashed:
						msgbox_not[subscriberList[i]].append([user_name, msg, ' #', hashtag, '#'])
					else:
						msgbox_not[subscriberList[i]].append([user_name, msg, ''])
				else:
					pass
		else:
			pass
	if hashed: ################### we should post the hashed msg to those hash subscribers
		#print lib_hashtag.keys()
		if hashtag in lib_hashtag.keys():
			#print hashtag
			for i in lib_hashtag[hashtag]: # 1: show to currently connected users
				for k in real_conn_list:
					#print k[1]
					if k[1] == i:
						k[0].sendall(msg)
					else:
						pass
			temp1 = set(registed_user) # 2: store the message to msgbox_not list
			temp2 = set(return_2nd_from_a_list(real_conn_list))
			temp3 = list(temp1-temp2)
			subscriberList = checkSubscribers(user_name, 1)
			for i in temp3:
				if i in subscriberList:
					msgbox_not[i].append([user_name, msg, ' #', hashtag, '#'])
					
		else: # this hashtag has no user to hashed
			pass
	else:
		pass
		

def getUnreadMsg(user_name, obj_name): # functional
	unmsg = ''
	if obj_name == '':
		if msgbox_not[user_name]:
			for i in msgbox_not[user_name]:
				for j in i:
					unmsg = unmsg + j
				unmsg = unmsg + '$'
		return unmsg # a big big string
	else:
		if msgbox_not[user_name]:
			for i in msgbox_not[user_name]:
				if i[0] == obj_name:
					for j in i:
						unmsg = unmsg + j
					unmsg = unmsg + '$'
				else:
					pass
		return unmsg

def seeSubscribes(conn, subframe): # functional
	## user_name would like to see he follows who, according to subscriptionMatrix ...
	user_name = subframe[0]
	sel = subframe[1]
	subList = []
	data = ''
	if sel == '2':
		for i in range(len(registed_user)):
			if registed_user[i] == user_name:
				for j in range(len(subscriptionMatrix[i])):
					if subscriptionMatrix[i][j] == 1:
						subList.append(registed_user[j])
		if subList:
			for i in subList:
				data = data + i + '$'
		else:
			data = 'none'
		conn.sendall(data)
	else:
		for i in range(len(registed_user)):
			if registed_user[i] == user_name:
				for j in range(len(subscriptionMatrix[i])):
					if subscriptionMatrix[j][i] == 1:
						subList.append(registed_user[j])
		if subList:
			for i in subList:
				data = data + i + '$'
		else:
			data = 'none'
		conn.sendall(data)		

def seeOfflineMessages(conn, subframe):
	user_name = subframe[0]
	data = ''
	subscriberList = checkSubscribers(user_name, 2) # see user_name following who
	if subscriberList:
		for i in subscriberList:
			data = data + i + '$'
		conn.sendall(data) # give name list back to user
	else:
		conn.sendall('you do not have any subscription')
		return 0
	obj_name = conn.recv(1024)
	unmsg = getUnreadMsg(user_name, obj_name)
	conn.sendall(unmsg)
	
def hashtagSearch(conn, subframe):
	user_name = subframe[0]
	hashkey = subframe[1]
	hashlist = []
	reply = ''
	num = 0
	#print hashkey
	#print user_name
	if not msgbox:
		conn.sendall('no record found')
		return 0
	else:
		for i in reversed(msgbox):
			#print i
			if i[-1] == '#'and i[-2] == hashkey:
				hashlist.append(i)
				num = num + 1
			if num >= 10:
				break
		if not hashlist:
			conn.sendall('no record found')
			return 0
		else:
			for i in hashlist:
				for j in i:
					reply = reply + j
				reply = reply + '$'
			conn.sendall(reply)
			return 0
		
def clientthread(conn):
	global msgbox, msgbox_not, conn_list, registed_user, subscriptionMatrix, registed_passwd, real_conn_list, queue
	data = conn.recv(1024)
	user_name, passwd = extractName(data)
	if isValid(user_name, passwd):
		print 'valid user logged in'
		conn_list[-1].append(user_name)
		unreadMsg = getUnreadMsg(user_name,'')
		conn.sendall('s' + unreadMsg)
		################################# add real time socket here
		c,a = rs.accept() # 1st msg goes here
		real_conn_list.append([c])
		data = c.recv(1024) # 2nd msg goes here
		#################################
		user_name, m = extractName(data)
		real_conn_list[-1].append(user_name)
		queue.put(c)
	else:
		print 'invalid user'
		conn.sendall('error log in')
		conn.close()
		conn_list.pop()
		while 1:
			time.sleep(1000)
		
	while 1: # wait for any info
		data = conn.recv(1024)
		#############################see mat
		#for i in subscriptionMatrix:
		#	print i
		############################3
		subframe = extractDelimiter(data)
		if subframe[0] == '':
			pass
		elif subframe[0] == 'logOut':
			logOut(conn, c, subframe[1:])
		elif subframe[0] == 'See Offline Messages':
			seeOfflineMessages(conn, subframe[1:])
		elif subframe[0] == 'Edit Subscriptions':
			editSubscriptions(conn, subframe[1:])	
		elif subframe[0] == 'Post a Message':
			postAMessage(conn, c, subframe[1:])
		elif subframe[0] == 'See Subscribes':
			seeSubscribes(conn, subframe[1:])
		elif subframe[0] == 'Hashtag Search':
			hashtagSearch(conn, subframe[1:])
		else:
			pass	
		
def manipulate(): # functional
	while 1:
		msg = raw_input(">>  ")
		if msg == "messagecount":
			print int(len(msgbox))
		elif msg == 'usercount':
			if conn_list:
				for i in conn_list:
					print i[1]
				print 'total number of user: ' + str(len(conn_list))
			else:
				print 'nobody currently logging in'
		elif msg == 'storedcount':
			num = 0
			for i in registed_user:
				for j in msgbox_not[i]:
					#print j
					num = num + 1
			print 'total number of unread msg: ' + str(num)
		elif msg == 'newuser':
			while 1:
				uname = raw_input('new user name: ')
				upass = raw_input('new user passwd: ')
				if uname and upass:
					break
			registed_user.append(uname)
			registed_passwd.append(upass)
			subscriptionMatrix.append([0]*len(subscriptionMatrix))
			for i in subscriptionMatrix:
				i.append(0)
			msgbox_not.update({uname:[]})
			sub_hashtag.update({uname:[]})
		else:
			pass

HOST = ''
PORT = 5714
PORT_realtime = 5715
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.bind((HOST, PORT))
except socket.error, msg:
	print 'Binding error'
	sys.exit()
s.listen(10)

rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
        rs.bind((HOST, PORT_realtime))
except socket.error, msg:
        print 'Binding error'
        sys.exit()
rs.listen(10)
# 1st thread
start_new_thread(manipulate, ())
while True:
	conn,addr = s.accept()
	conn_list.append([conn])
	# 2nd thread
	start_new_thread(clientthread,(conn,))
