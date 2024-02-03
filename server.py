from typing import Tuple

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import deferLater

import asyncio
import re
import string
#from model import Lobby, User

UDP_MESSAGE_SECONDS_BETWEEN_TRIES: float = 0.05
SESSION_CLEANUP_SCHEDULED_SECONDS: float = 60 * 5
PLAYER_CLEANUP_SCHEDULED_SECONDS: float = 8
CONFIRMATION_RETRIES: int = 8
SECONDS_BETWEEN_CONFIRMATION_RETRIES: float = 0.1

PLAYER_NAME_REGEX : string = "[A-Za-z0-9]{1,23}"
MAX_PLAYERS : int = 8

#Delimiters
DEL_HANDLER = '|'
DEL_MESSAGE = ','
DEL_SUB     = ':'

#Performable outside of an active lobby
KEY_HOST_LOBBY = 'H'
KEY_JOIN_LOBBY = 'J'
KEY_PUBLIC_QUERY = 'Q'

#Performable only within an active lobby
KEY_READY = 'R'
KEY_CHAT_MESSAGE = 'C'

#Performable only by Lobby host
KEY_START = "S"
KEY_KICK = 'K'
KEY_BAN = 'B'

#Utility
KEY_PING = "P"
KEY_EXIT = "X"

###################################################################################################


class Server(DatagramProtocol):

    def __init__(self):
        self.debug = False
        self.activeLobbies : Dictionary = {}
        self.dispatchedLobbies : Dictionary = {}
        self.handlers = \
        {
            KEY_HOST_LOBBY :    self.hostLobby,
            KEY_JOIN_LOBBY :    self.joinLobby,
            KEY_PUBLIC_QUERY :  self.publicQuery,
            KEY_READY :         self.playerReady,
            KEY_CHAT_MESSAGE :  self.chatMessage,
            KEY_START :         self.startGame,
            KEY_KICK :          self.kickPlayer,
            KEY_BAN :           self.banPlayer,
            KEY_PING :          self.pingReceived,
            KEY_EXIT :          self.playerExit
        }

    def datagramReceived(self, data, address):
        dataString = data.decode("utf-8")
        if self.debug:
            print("Data received: '" + dataString + "' from " + str(address))
        try:
            handlerKey, message = self.parseDataString(dataString)
            if not handlerKey in self.handlers.keys():
                if self.debug:
                    print("ERROR: unknown handler key ", message)
                raise Exception
            self.handlers[handlerKey](address, message)
        except Exception as e:
            if self.debug:
                print("ERROR: " + str(e))
        
        #self.send_message(address, "Confirming handshake")

    def parseDataString(self, dataString : string) -> Tuple:
        split = dataString.split(DEL_HANDLER, 1)
        if len(split) != 2:
            if self.debug:
                print("ERROR: Invalid data received " + dataString)
            raise Exception
        return split[0], split[1]

###################################################################################################

    def sendMessage(self, address : Tuple, message : string, retries : int = 0):
        if self.debug:
            print("Sending '" + message + "' to " + str(address))
        self.transport.write(bytes(message, "utf-8"), address)
        if retries > 0:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.sendMessageRetries(address, message, retries))

    async def sendMessageRetries(self, address : Tuple, message : string, retries : int):
        try:
            for i in range(retries):
                await asyncio.sleep(1.0)
                self.transport.write(bytes(message, "utf-8"), address)
            
        except Exception as e:
            if self.debug:
                print("Uncontrolled error: " + str(e))

###################################################################################################

    def hostLobby(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to host lobby: " + message)

    def joinLobby(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to join lobby: " + message)

    def publicQuery(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request for public query: " + message)

    def playerReady(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to be set ready: " + message)
    
    def chatMessage(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to send chat message: " + message)

    def startGame(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to start game: " + message)

    def kickPlayer(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to kick player: " + message)

    def banPlayer(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to ban player: " + message)

    def pingReceived(self, address : Tuple, message : string):
        if self.debug:
            print("Receive ping: " + message)

    def playerExit(self, address : Tuple, message : string):
        if self.debug:
            print("Receive request to exit from player: " + message)

###################################################################################################

    

