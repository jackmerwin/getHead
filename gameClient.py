#!/usr/bin/env python
# encoding: utf-8

"""
gameClient.py
TEAM getHead()



"""


import sys
import os
import time
import cgi
import threading
import random
import socket
import pickle
import xmlrpclib
import subprocess
import zipfile

OWN_IP = socket.gethostbyname(socket.gethostname())
GAME_SERVER = sys.argv[1]
PORT = 7772
#PORT = sys.argv[2]			TODO
PORT_XML = 7771
PORT_GAME = 7777

PATH = os.getcwd()

def unzip_file_into_dir(file, dir):
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        if name.endswith('/'):
            os.mkdir(os.path.join(dir, name))
        else:
            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

def main():

	# FIRST set up the xmlrpc connection
	xmlproxy = 'http://'+GAME_SERVER+':'+str(PORT_XML)
	print '\nConnecting to ' + xmlproxy
	proxy = xmlrpclib.ServerProxy(xmlproxy,allow_none=True)
	test = 0
	test = proxy.connect(OWN_IP,PORT)
	if test != 1: 
		print 'connection failed'
		exit(1)
		
	print '\nYou have connected to the getHead() gaming server!!'
	while True:
		#MAIN CLIENT SCREEN CODE LOOP
		try:
			print 'Please select an option by choosing a number:'
			print '1: View list of downloadable games'
			print '2: View list of running games'
			print '3: Join a running game'
			print '4: Host a game yourself'
			print '5: Disconnect from getHead()'
			choice = raw_input(':: ')
			
			#DOWNLOAD
			if choice == '1':
				pickledList = proxy.downloadablesList()
				gameList = pickle.loads(pickledList)
				print ' '
				for game in gameList:
					print '  ' + game

				print "\nTo download a game, type its name, or type '0' to skip"
				download = raw_input(':: ')
				if download == '0':
					print ' '
				else:
					print "Downloading " + download + '...\n'
					pickledGame = proxy.downloadGame(OWN_IP,download)
					if pickledGame == 0:
						print "Incorrect game name. Please retry\n"
					else:
						gameFile = pickle.loads(pickledGame)
						writefile = open(download+'.zip', 'w')
						writefile.write(gameFile)
						print "Game and resources downloaded. The files have been unzipped."
						print "Make sure that the game file and its resources are in the same "
						print "directory as the getHead() client.\n"
						writefile.close()
						
						unzip_file_into_dir(download+'.zip',PATH)
						
			#VIEW GAME LIST
			elif choice == '2':
				pickledGames, pickledSlots = proxy.openGameList()
				openGames = pickle.loads(pickledGames)
				openSlots = pickle.loads(pickledSlots)
				print '\n'
				for game in openGames:
					print "instance of "+openGames[game]+" being run by "+game+" with "+str(openSlots[game])+" slots"
				print '\n'
				
			#JOIN GAME
			elif choice == '3':
				pickledGames, pickledSlots = proxy.openGameList()
				openGames = pickle.loads(pickledGames)
				openSlots = pickle.loads(pickledSlots)
				print '\n'
				for game in openGames:
					print "instance of "+openGames[game]+" being run by "+game+" with "+str(openSlots[game])+" slots"
				print '\n'
				print "\nTo join a game, type the hostname, or type '0' to skip"
				join = raw_input(':: ')
				if join == '0':
					pass
				else:
					game,players = proxy.joinGameInstance(join)
					print "Joining instance of of " + game +" on "+join+"\n"
					if game == 'Bomberman':
						joinString = 'python main.py '+join+' '+str(players)
					elif game == 'ZombieTest':
						joinString = 'python ZombieTest.py '+join+' '+str(players)
					elif game == 'SingleZombies':
						joinString = 'python SingleZombies.py '+join+' '+str(players)
					p = subprocess.Popen(joinString, shell=True)
					p.wait()
			
			#HOST GAME
			elif choice == '4':
				selection = raw_input('Please enter the name of the game you wish to host: ')
				players = raw_input('Please enter the number of players (max 4): ')
				if selection == 'Bomberman':
					gameString = 'python Host.py '+OWN_IP+' '+players
				elif selection == 'ZombieTest':
					gameString = 'python ZombieHost.py '+OWN_IP+' '+players
				elif selection == 'SingleZombies':
					gameString = 'python SingleZombies.py '+OWN_IP+' '+players
				proxy.registerGameInstance(OWN_IP,selection,players)
				print "Starting instance of of '" + selection +"'\n"
				p = subprocess.Popen(gameString, shell=True)
				p.wait()
				proxy.killGameInstance(OWN_IP,selection)
			
			#DISCONNECT
			elif choice == '5':
				print '\ndisconnecting...'
				#time.sleep(1) 
				proxy.disconnect(OWN_IP)
				exit(0)
			
			#DEFAULT
			else:
				print 'Invalid input; please choose an option by number\n'
				pass
			
		except (KeyboardInterrupt, SystemExit):
			proxy.disconnect(OWN_IP)
			exit(0)


if __name__ == '__main__':
	main()
	
	