#!/usr/bin/env python
# encoding: utf-8

"""
mainServer.py
TEAM getHead()

*****IMPORTANT*****
Do not distribute this code to unauthorized parties.
It contains my AWS ID codes. Please protect them.
*******************

XML server to run as a game system matchmaker.  Runs on Amazon AWS.

XML function descriptions:
	
	connect:  adds gaming user's host name and port to the list of connected users
	
	disconnect: removes user's host/port from list of connected users.  
				client should call this before disconnect to maintain
				up to date lists

	downloadablesList: return a list of games maintained by the server as .zip files
	
	downloadGame:	opens a connection to an s3 bucket on the amazon cloud containing
					the .zip files of games that the server allows users to download
	
	openGameList:  displays a list of current games with 
	
	joinGameInstance: 
	
	registerGameInstance:
	
	killGameInstance:	removes a game from server lists. uses try/except on all lists,
						does not need to know the status of the game being killed

"""


import sys
import os
import time
import threading
import random
import socket
import xmlrpclib
import pickle
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7770
PORT_XML = 7771

connectionDict = { "LOCAL":HOST }
FILLED_GAMES = { "FOO":"bar"}
TOTAL_SLOTS = { "FOO":"bar" }
OPEN_GAMES = { "FOO":"bar"}
OPEN_SLOTS = { "FOO":"bar"}
GAME_LIST = []

#XML server functions
class MatchMaker(object):
	
	#CONNECT
	def connect(self,hostname,port):
		connectionDict["hostname"] = port
		print 'client '+hostname+' has connected with port '+str(connectionDict["hostname"])
		return 1
	
	#DISCONNECT
	def disconnect(self,hostname):
		try:
			del connectionDict["hostname"]
			print 'client '+hostname+' has disconnected'
		except (KeyError):
			pass
	
	#SHOW LIST OF AVALIABLE GAMES
	def downloadablesList(self):
		pickledList = pickle.dumps(GAME_LIST)
		return pickledList
	
	#USER DOWNLOAD FUNCTION
	def downloadGame(self,hostname,gameFile):
		if gameFile not in GAME_LIST:
			print 'attempted access of '+gameFile+' by '+hostname+' not in GAME_LIST'
			return 0
		try:
			s3 = S3Connection('', '')
			b = s3.create_bucket('362.merwin.jack')
			fileKey = Key(b)
			fileKey.key = '362/getHead/'+gameFile+'.zip'
			FILETOSEND = fileKey.get_contents_as_string()
			print 'File '+gameFile+'.zip being downloaded by '+hostname
			pickledFile = pickle.dumps(FILETOSEND)
			return pickledFile
		except:
			print 'attempted download of '+gameFile+' by '+hostname+' failed!'
			return 0
		
	#DISPLAY RUNNING GAMES LIST	
	def openGameList(self):
		pickledGames = pickle.dumps(OPEN_GAMES)
		pickledSlots = pickle.dumps(OPEN_SLOTS)
		return pickledGames, pickledSlots
	
	#USER JOIN GAME / MATCHMAKER
	def joinGameInstance(self,hostname):
		game = OPEN_GAMES[hostname]
		players = TOTAL_SLOTS[hostname]
		FILLED_SLOTS[hostname] = FILLED_SLOTS[hostname]+1
		if OPEN_SLOTS[hostname] == FILLED_SLOTS[hostname]:
			FILLED_GAMES[hostname] = OPEN_GAMES[hostname]
			try:
				del OPEN_SLOTS[hostname]
			except:
				pass
			try:
				del OPEN_GAMES[hostname]
			except:
				pass

		return game,players
	
	#USER CREATE GAME INSTANCE
	def registerGameInstance(self,hostname,gameFile,players):
		OPEN_GAMES[hostname] = gameFile
		OPEN_SLOTS[hostname] = int(players)
		TOTAL_SLOTS[hostname] = int(players)
		FILLED_SLOTS[hostname] = 1
		print 'Game '+gameFile+' started by '+hostname
		return 1
	
	#GAME INSTANCE END/CLEANUP FUNCTION
	def killGameInstance(self,hostname,gameFile):
		try:
			del OPEN_GAMES[hostname]
		except:
			pass
		try:
			del FILLED_GAMES[hostname]
		except:
			pass
		try:	
			del OPEN_SLOTS[hostname]
		except:
			pass
		try:
			del TOTAL_SLOTS[hostname]
		except:
			pass
		print 'Game '+gameFile+' run by '+hostname+' finished'
		return 1
		
	
#XML server setup
class xmlserver(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		''' initialize server and register functions as MatchMaker object '''
		self.server = SimpleXMLRPCServer( (HOST,PORT_XML), logRequests=False, allow_none=True )
		self.server.register_introspection_functions()
		self.server.register_instance( MatchMaker() )
	def run(self):
		''' serve forever until interrupt (or main kill) '''
		try:
			self.server.serve_forever()
		except (KeyboardInterrupt, SystemExit):
			os._exit(0)
	
	
''' Creates game list and starts XML server. All functionality in XML code '''
def main():

	print "Starting getHead() server on AWS internal IP: "+HOST+"..."

	del OPEN_GAMES["FOO"]
	
	''' create list of games server is making available'''
	GAME_LIST.append('SingleZombies')
	GAME_LIST.append('ZombieTest')
	GAME_LIST.append('Bomberman')
	GAME_LIST.append('Pong')

	''' start XML server '''
	xmlserver().start()
	
	''' run exit condition loop '''
	while True:
		try:
			opt = raw_input('- 0 to exit at any time - \n')
			if opt == '0':
				os._exit(0)
		except (KeyboardInterrupt, SystemExit):
			os._exit(0)
			raise


if __name__ == '__main__':
	main()
	
	
	
	