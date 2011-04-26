#!/usr/bin/env python
# encoding: utf-8

"""
gameClient.py
TEAM getHead()



"""

from Tkinter import *
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
import tkSimpleDialog

OWN_IP = socket.gethostbyname(socket.gethostname())
GAME_SERVER = '50.19.30.18'
PORT = 7772
#PORT = sys.argv[2]                     TODO
PORT_XML = 7771
PORT_GAME = 7777
PATH = os.getcwd()
fileName = ""



class FileDialog(tkSimpleDialog.Dialog):

    def body(self, master):
        Label(master, text="Enter Name:").grid(row=0)
        self.name = Entry(master)
        self.name.grid(row=0, column=1)

    def apply(self):
        first = self.name.get()
        self.result = first

class PlayerDialog(tkSimpleDialog.Dialog):

    def body(self, master):
        Label(master, text="Enter Number of Players:").grid(row=0)
        self.name = Entry(master)
        self.name.grid(row=0, column=1)

    def apply(self):
        first = self.name.get()
        self.result = first
    
def download_Button():
    global proxy
    pickledList = proxy.downloadablesList()
    gameList = pickle.loads(pickledList)
    
    gameVar = ""
    for game in gameList:
        gameVar = gameVar + game + "\n"
    textVar.set(gameVar + "Enter Name of File to Download in separate window \n")

    gameFile = FileDialog(root)
    fileName = gameFile.result
    if fileName == '0':
        textVar.set(" ")
    else:
        textVar.set( 'Downloading Game \n')
        pickledGame = proxy.downloadGame(OWN_IP,fileName)
        if pickledGame == 0:
            textVar.set("Incorrect game name. Please retry\n")
        else:
            gameFile = pickle.loads(pickledGame)
            writefile = open(fileName+'.zip', 'w')
            writefile.write(gameFile)
            textVar.set( "Game and resources downloaded. The files have been unzipped. \n Make sure that the game file and its resources are in the same \n directory as the getHead() client.\n")
            writefile.close()       
            unzip_file_into_dir(fileName+'.zip',PATH)
        
def running_Button():
    global proxy
    pickledGames, pickledSlots = proxy.openGameList()
    openGames = pickle.loads(pickledGames)
    openSlots = pickle.loads(pickledSlots)

    runVar = ""
    for game in openGames:
        runVar = runVar + "instance of "+openGames[game]+" being run by "+game+" with "+str(openSlots[game])+" slots \n"
    textVar.set(runVar)

def join_Button():
    global proxy
    pickledGames, pickledSlots = proxy.openGameList()
    openGames = pickle.loads(pickledGames)
    openSlots = pickle.loads(pickledSlots)
    
    joinVar = ''
    for game in openGames:
        joinVar = joinVar + "instance of "+openGames[game]+" being run by "+game+" with "+str(openSlots[game])+" slots \n"
    joinVar = JoinVar + "\nTo join a game, type the hostname, or type '0' to skip \n"
    textVar.set(joinVar)
    
    joinName = FileDialog(root)
    fileName = joinName.result
    if fileName == '0':
        pass
    else:
        game,players = joinGameInstance(fileName)
        textVar.set( "Joining instance of of " + game +" on "+fileName+"\n")
        if game == 'Bomberman':
            joinString = 'python main.py '+fileName+' '+str(players)
        elif game == 'ZombieTest':
            joinString = 'python ZombieTest.py '+fileName+' '+str(players)
        elif game == 'SingleZombies':
            joinString = 'python SingleZombies.py '+fileName+' '+str(players)
        p = subprocess.Popen(joinString, shell=True)
        p.wait()
        
def host_Button():
    global proxy
    
    textVar.set('Please enter the name of the game you wish to host in other window: ')
    gameName = FileDialog(root)
    selection = gameName.result
    
    textVar.set('Please enter the number of players (max 4) in other window: ')
    numPlayers = PlayerDialog(root)
    players = numPlayers.result
    
    if selection == 'Bomberman':
        gameString = 'python Host.py '+OWN_IP+' '+players
    elif selection == 'ZombieTest':
        gameString = 'python ZombieHost.py '+OWN_IP+' '+players
    elif selection == 'SingleZombies':
        gameString = 'python SingleZombies.py '+OWN_IP+' '+players
    proxy.registerGameInstance(OWN_IP,selection,players)
    textVar.set( "Starting instance of of '" + selection +"'\n")
    p = subprocess.Popen(gameString, shell=True)
    p.wait()
    proxy.killGameInstance(OWN_IP,selection)
    
def disconnect_Button():
    global proxy
    textVar.set( '\ndisconnecting... \n')
    proxy.disconnect(OWN_IP)
    exit(0)

def unzip_file_into_dir(file, dir):
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        if name.endswith('/'):
            os.mkdir(os.path.join(dir, name))
        else:
            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()
            
root = Tk()
root.title("Vapor Client")

textVar = StringVar()
textBox = Label(root, height=5,textvariable = textVar)
buttonFrame = Frame(root,relief=GROOVE)

downloadButton = Button(buttonFrame, text='Download Game', command = download_Button)
downloadButton.pack(side=LEFT)

runningButton = Button(buttonFrame, text='Running Games', command = running_Button)
runningButton.pack(side=LEFT)

joinButton = Button(buttonFrame, text='Join Game', command = join_Button)
joinButton.pack(side=LEFT)

hostButton = Button(buttonFrame, text='Host a Game', command = host_Button)
hostButton.pack(side=LEFT)

disconnectButton = Button(buttonFrame, text='Disconnect from Game', command = disconnect_Button)
disconnectButton.pack(side=LEFT)

buttonFrame.pack(side=TOP)
textBox.pack()



#FIRST set up the xmlrpc connection
xmlproxy = 'http://'+GAME_SERVER+':'+str(PORT_XML)
print '\nConnecting to ' + xmlproxy
proxy = xmlrpclib.ServerProxy(xmlproxy,allow_none=True)
test = 0
test = proxy.connect(OWN_IP,PORT)
if test != 1: 
    print 'connection failed'
    exit(1)
print '\nYou have connected to the getHead() gaming server!!'
root.update()
root.mainloop()

    
    
