import socket
import sys
import os
import time
import Queue
import getpass
from thread import *

HOST = 'localhost'
PORT = 5714
PORT_real = 5715
User = []
cur_user = ''
queue = Queue.Queue()

def logOut(s, user_name, rs): # functinoal
	s.sendall('logOut'+'$'+user_name)
	rs.sendall('logOut'+'$'+user_name)
	s.close()
	rs.close()

def realTimeMsg(user_name, rs): # functional
	data = ''
	while 1:
		if data != 'confirm log out':
			data = rs.recv(1024)
			print data
		else:
			break
	rs.close()

def Prompt(): # functional
	os.system('clear')
	global queue	
	while 1:
		print 'LOG IN'
		user_name = raw_input("user name: ")
		pass_word = getpass.getpass()
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			print 'Failed to create socket'
			sys.exit()
		s.connect((HOST,PORT))
		s.sendall(user_name + '$' + pass_word)

		data = s.recv(1024)
		if data[0] == 's':
			try:
				rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			except socket.error:
				print 'Failed to create socket'
				sys.exit()
			rs.connect((HOST,PORT_real)) # 1st msg
			rs.sendall(user_name + '$' + 'real time msg') # 2nd msg
			queue.put(rs)			
			return 1,user_name,s,data[1:]
		else:
			s.close()
			return 0,'','',0

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

def extract(data): # deprecated
	global User
	User_char = []
	for i in data[1:]:
		if i == '$':
			break
		User_char.append(i)
	User.append(''.join(User_char))

def main_menu(user_name,unmsg): # functional
	#os.system('clear')
	print user_name+', ',
	if unmsg:  
		print 'You have ',str(len(unmsg)-1),' unread message(s)'
	else:
		print 'You have 0 unread message'
	print '------MENU------'
	print '1. See Offline Messages'
	print '2. Edit Subscriptions'
	print '3. Post a Message'
	print '4. See Followers'
	print '5. hashtag search'
	print '0. Logout'	
	print '----------------'

	while 1:
		msg = raw_input("option: ")
		if msg:
			if int(msg) > 5 or int(msg) < 0:
				msg = raw_input("Select again: ")
			else:
				return int(msg)
		else:
			pass

def seeOfflineMessage(s, user_name, unmsg): # functional
	#os.system('clear')
	print '1. see all messages\n2. select messages from subscriptions\n3. back'
	sel = raw_input('choose: ')
	while 1:
		if int(sel) == 3:
			return 0
		elif int(sel) == 1 or int(sel) == 2:
			break
		else:
			sel = raw_input('choose again: ')
	if sel == '1':
		for i in unmsg:
			print user_name+': '+i[len(user_name)-2:]
	else:
		s.sendall('See Offline Messages' + '$' + user_name) # this is only where the server calls
		data = s.recv(1024)
		if data == 'you do not have any subscription':
			print data
			#sel = raw_input('press Enter to continue$ ')
			return 0
		else:
			subscriberList = extractDelimiter(data)
			for i in range(len(subscriberList)):
				if subscriberList[i] != '':
					print str(i+1)+': ', subscriberList[i]
			sel = raw_input('choose: ')
			while int(sel) > len(subscriberList):
				sel = raw_input('invalid, re-input: ')
			s.sendall(subscriberList[int(sel)-1])
			data = s.recv(1024)
			if data:
				unmsg = extractDelimiter(data)
				for i in unmsg:
					print subscriberList[int(sel)-1]+': '+i[len(subscriberList[int(sel)-1]):]
			else:
				print 'no record found'
			#sel = raw_input('press Enter to continue$ ')	
			return 0

def add_delete_step1(s, user_name, sel): # functional
	if sel == 1:
		s.sendall('Edit Subscriptions$add$'+user_name)
	else:
		s.sendall('Edit Subscriptions$del$'+user_name)
	data = s.recv(1024)
	name_list = extractDelimiter(data)
	return name_list

def add_delete_step2(s, obj_name): # functional
	s.sendall(obj_name)
	data = s.recv(1024)
	return data

def editSubscriptions(s, user_name): # functionl
	#os.system('clear')
	print '1. users \n2. hashtag \n3. back'
	sel = raw_input('choose: ')
	while 1:
		if int(sel) == 3:
			return 0
		elif int(sel) == 1 or int(sel) == 2:
			break
		else:
			sel = raw_input('Choose again: ')	
	if sel == '1':
		print 'WHAT DO YOU WANT TO DO:'
		print '1. add a subscription \n2. drop a subscription \n3. back'
		sel = raw_input('choose: ')
		while 1:
			if int(sel) == 3:
				return 0
			elif int(sel) == 1 or int(sel) == 2:
				break
			else:
				sel = raw_input('choose again: ')
		name_list = add_delete_step1(s, user_name, int(sel))
		if name_list:
			print 'choose a name:\nq: quit'
			for i in range(len(name_list)-1): # because there is an empty name at last
				print str(i+1) + ': ' + name_list[i]
			sel = raw_input('num of name: ')
			if sel == 'q':
				s.sendall('cancel')
				return 0
			data = add_delete_step2(s, name_list[int(sel)-1])
			if data == 's':
				print name_list[int(sel)-1] + ' has been proceeded'
				#time.sleep(1)
				return 1
			else:
				print 'server error'
				#time.sleep(1)
				return 0	
		else:
			print 'invalid'
			#time.sleep(3)
			return 0
	else:
		print 'WHAT DO YOU WANT TO DO:'
		print '1. add a hashtag subscription \n2. drop a hashtag subscription \n3. back'
		sel = raw_input('choose: ')
		while 1:
			if int(sel) == 3:
				return 0
			elif int(sel) == 1 or int(sel) == 2:
				break
			else:
				sel = raw_input('choose again: ')
		if sel == '1':
			while 1:
				print 'input which hashtag you are interest'
				data = raw_input('hashtag: ')
				if data:
					break
			s.sendall('Edit Subscriptions$add$'+user_name+'$'+data+'$hashtag')
		elif sel == '2':
			s.sendall('Edit Subscriptions$del$'+user_name+'$hashtag')
			data = s.recv(1024)
			hashlist = extractDelimiter(data)
			if hashlist[0] == 'no hashtag found':
				print 'no hashtag subscription found'
				#sel = raw_input('press Enter to continue>>')
				return 0
			else:
				for i in range(len(hashlist)-1):
					print str(i+1)+': '+hashlist[i]
				print 'q: quit'
				sel = raw_input('num of hashtag: ')
				while not sel:
					sel = raw_input('num of hashtag: ')
				if sel == 'q':
					return 0
				else:
					pass
				while int(sel) > len(hashlist)-1:
					sel = raw_input('num of hashtag: ')
				s.sendall(hashlist[int(sel)-1])
				#print 'gonna delete it'
				deletehash = s.recv(1024)
				print 'deleted ' + deletehash
				#sel = raw_input('press Enter to continue>>')
				return 0				
		else:
			pass
		
def postAMessage(s,user_name): # functional
	#os.system('clear')
	while 1:
		print 'type your message(q for quit): '
		msg1 = raw_input('message: ')
		if msg1 == 'q':
			break
		msg2 = raw_input('hashtag(if no, type \'none\'): ')
		if msg2 != 'none':
			msg  = msg1 + '#' +msg2
		elif msg2 == 'none':
			msg = msg1
		#msg = raw_input('message#hashtag: ')
		if msg1 != 'q':
			while 1:
				if len(msg) > 140:
					print 'messages should be less than 140 characters'
					msg1 = raw_input('message: ')
					msg2 = raw_input('hashtag(if no, type \'none\'): ')
					if msg2 != 'none':
						msg  = msg1 + '#' +msg2
					elif msg2 == 'none':
						msg = msg1
				else:
					break
			sel = raw_input('press y to set this to be private(if no, press enter):')
			if not sel:
				s.sendall('Post a Message$' + msg + '$' + user_name)
			elif sel == 'y' or sel == 'Y':
				while 1:
					obj_name = raw_input('sepecified users: ')
					if obj_name:
						break
				s.sendall('Post a Message$' + msg + '$' + user_name + '$' + obj_name + '$' + 'Private Msg')
			else:
				s.sendall('Post a Message$' + msg + '$' + user_name)
		else:
			break
			
def seeSubscribes(s, user_name): # functional
	#os.system('clear')
	'''
	print '1. see followers'
	print '2. see who am I following'
	sel = raw_input('>> ')
	if sel == '2':
		data = 'See Subscribes' + '$' + user_name + '$' + '2'
	else:
	'''
	data = 'See Subscribes' + '$' + user_name + '$' + '1'
	s.sendall(data)
	data = s.recv(1024)
	data = extractDelimiter(data)
	if data[0] != 'none':
		'''
		if sel == '2':
			print 'you are following: '
		else:
		'''
		print 'your followers: '
		for i in data:
			print i
	else:
		print 'none'
	#a = raw_input('press any key to continue >> ')

def hashtagSearch(s, user_name):
	#os.system('clear')
	print '**********hashtag search**********'
	hashkey = raw_input('type a hashtag: ')
	s.sendall('Hashtag Search' + '$' + user_name + '$' + hashkey)
	data = s.recv(1024)
	if data == 'no record found':
		print data
		#sel = raw_input('press Enter to continue >>')
		return 0
	else:
		hashlist = extractDelimiter(data)
		if hashlist:
			for i in hashlist:
				print i
		else:
			print 'Unknown error'
	#sel = raw_input('press Enter to continue >>')		
		
while 1:
	while 1:
		val,user_name,s,unmsg = Prompt()
		if val == 1:
			rs = queue.get()
			break
		else:
			pass
	unmsg = extractDelimiter(unmsg)
	start_new_thread(realTimeMsg, (user_name, rs, ))
	while 1:
		sel = main_menu(user_name,unmsg)
		if sel == 1:
			seeOfflineMessage(s,user_name,unmsg)
		elif sel == 2:
			editSubscriptions(s,user_name)
		elif sel == 3:
			postAMessage(s,user_name)
		elif sel == 0:
			logOut(s, user_name, rs)
			break
		elif sel == 4:
			seeSubscribes(s, user_name)
		elif sel == 5:
			hashtagSearch(s, user_name)
		else:
			pass

