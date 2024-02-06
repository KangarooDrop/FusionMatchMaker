
#TODO:
#  lobby settings
#  adjusting lobby size
#  public lobbies
#  run server as headless
#  server output only when self.debug==True

from typing import Tuple

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import deferLater

import asyncio
import re
import string
from lobby import Lobby
from user import User
import dispatcher

SECONDS_BETWEEN_TRIES: float = 0.05
CLEANUP_SECONDS: float = 8
CONFIRMATION_RETRIES: int = 8
SECONDS_BETWEEN_CONFIRMATION_RETRIES: float = 0.1
PING_SECONDS = 1.0

MAX_PLAYERS : int = 8

###################################################################################################
### Message Handlers sent from Client->Server ###

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
### Message Handlers sent from Server->Client#

CLIENT_TYPE_SUCC = 'succ'
CLIENT_TYPE_ERR = 'err'
CLIENT_TYPE_INFO = 'info'

CLIENT_SUCC_HOST_LOBBY = CLIENT_TYPE_SUCC + DEL_MESSAGE +       'lobby_created'
CLIENT_SUCC_JOIN_LOBBY = CLIENT_TYPE_SUCC + DEL_MESSAGE +       'lobby_joined'
CLIENT_SUCC_START_GAME = CLIENT_TYPE_SUCC + DEL_MESSAGE +       'start_game'

CLIENT_INFO_PLAYERS = CLIENT_TYPE_INFO + DEL_MESSAGE +          'players'
CLIENT_INFO_PUBLIC_LOBBIES = CLIENT_TYPE_INFO + DEL_MESSAGE +   'public_lobbies'
CLIENT_INFO_PING = CLIENT_TYPE_INFO + DEL_MESSAGE +             'ping'
CLIENT_INFO_SET_HOST = CLIENT_TYPE_INFO + DEL_MESSAGE +         'set_host'
CLIENT_INFO_CHAT = CLIENT_TYPE_INFO + DEL_MESSAGE +             'chat'

CLIENT_ERR_USER_IN_LOBBY = CLIENT_TYPE_ERR + DEL_MESSAGE +      'user_in_lobby'
CLIENT_ERR_LOBBY_NAME_TAKEN = CLIENT_TYPE_ERR + DEL_MESSAGE +   'lobby_name_taken'
CLIENT_ERR_LOBBY_TIMEOUT = CLIENT_TYPE_ERR + DEL_MESSAGE +      'lobby_timeout'
CLIENT_ERR_USERNAME_TAKEN = CLIENT_TYPE_ERR + DEL_MESSAGE +     'username_taken'
CLIENT_ERR_LOBBY_BAD_SIZE = CLIENT_TYPE_ERR + DEL_MESSAGE +     'lobby_bad_size'
CLIENT_ERR_NOT_HOST = CLIENT_TYPE_ERR + DEL_MESSAGE +           'not_host'
CLIENT_ERR_NOT_IN_LOBBY = CLIENT_TYPE_ERR + DEL_MESSAGE +       'not_in_lobby'
CLIENT_ERR_USERS_NOT_READY = CLIENT_TYPE_ERR + DEL_MESSAGE +    'users_not_ready'
CLIENT_ERR_NO_LOBBY_FOUND = CLIENT_TYPE_ERR + DEL_MESSAGE +     'lobby_not_found'
CLIENT_ERR_COULD_NOT_JOIN = CLIENT_TYPE_ERR + DEL_MESSAGE +     'could_not_join'
CLIENT_ERR_NO_USER_FOUND = CLIENT_TYPE_ERR + DEL_MESSAGE +      'user_not_found'
CLIENT_ERR_KICKED = CLIENT_TYPE_ERR + DEL_MESSAGE +             'kicked'
CLIENT_ERR_BANNED = CLIENT_TYPE_ERR + DEL_MESSAGE +             'banned'

#UNUSED
CLIENT_ERR_INVALID_REQUEST = CLIENT_TYPE_ERR + DEL_MESSAGE +    'invalid_request'
CLIENT_ERR_BAD_START_GAME = CLIENT_TYPE_ERR + DEL_MESSAGE +     'bad_start_game'
CLIENT_ERR_USERNAME_BAD = CLIENT_TYPE_ERR + DEL_MESSAGE +       'username_bad'
CLIENT_ERR_BAD_CHAT = CLIENT_TYPE_ERR + DEL_MESSAGE +           'bad_chat'

###################################################################################################


class Server(DatagramProtocol):

    def __init__(self):
        self.debug = False
        self.activeLobbies  = []
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
        reactor.callLater(CLEANUP_SECONDS, self.cleanup)
        reactor.callLater(PING_SECONDS, self.pingUsers)

    def datagramReceived(self, data, address):
        dataString = data.decode("utf-8")
        self.log("Data received: '" + dataString + "' from " + str(address))
        try:
            handlerKey, message = self.parseDataString(dataString)
            if not handlerKey in self.handlers.keys():
                self.log("ERROR: unknown handler key " + message)
                raise Exception
            self.handlers[handlerKey](address, message)
        except Exception as e:
            self.log("ERROR: " + str(e))
        
        #self.send_message(address, "Confirming handshake")

    def parseDataString(self, dataString : string) -> Tuple:
        split = dataString.split(DEL_HANDLER, 1)
        if len(split) != 2:
            self.log("ERROR: Invalid data received " + dataString)
            raise Exception
        return split[0], split[1]
    
    def log(self, message : string):
        if self.debug:
            print(message)
    
###################################################################################################
    
    def pingUsers(self):
        for lobby in self.activeLobbies:
            for user in lobby.users:
                self.sendMessage((user.ip, user.port), CLIENT_INFO_PING)
        reactor.callLater(PING_SECONDS, self.pingUsers)
    
    def cleanup(self):
        print("Cleaning up... Active Lobbies: " + str(len(self.activeLobbies)))
        
        for lobby in self.activeLobbies:
            for user in lobby.users:
                if user.isTimedOut():
                    self.removeUserFromLobby(lobby, user)
        
            if lobby.isTimedOut():
                for user in lobby.users:
                    sendMessage((user.ip, user.port), CLIENT_ERR_LOBBY_TIMEOUT, 3)
                self.activeLobbies.remove(lobby)
                self.log("Removing timedout lobby")
                
        
        reactor.callLater(CLEANUP_SECONDS, self.cleanup)
    
    def callAsync(self, funcData):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(funcData)
        
    
    def sendMessage(self, address : Tuple, message : string, retries : int = 0):
        self.log("Sending '" + message + "' to " + str(address))
        self.transport.write(bytes(message, "utf-8"), address)
        if retries > 0:
            self.callAsync(self.sendMessageRetries(address, message, retries))

    async def sendMessageRetries(self, address : Tuple, message : string, retries : int):
        try:
            for i in range(retries):
                await asyncio.sleep(SECONDS_BETWEEN_TRIES)
                self.transport.write(bytes(message, "utf-8"), address)
            
        except Exception as e:
            self.log("Uncontrolled error: " + str(e))
    
    def removeUserFromLobby(self, lobby : Lobby, user : User):
        self.sendChat(lobby, user.username + " has left the lobby.")
        host = lobby.host
        lobby.removeUser(user)
        if not lobby.isHost(host) and lobby.host != None:
            self.sendMessage((lobby.host.ip, lobby.host.port), CLIENT_INFO_SET_HOST)
            self.sendChat(lobby, lobby.host.username + " is the new host.")
        self.updateLobbyInfo(lobby)
    
###################################################################################################

    def hostLobby(self, address : Tuple, message : string):
        self.log("Receive request to host lobby: " + message)
        try:
            ip, port = address
            lobbyName, numPlayers, username = self.parseHostInfo(message)
            
            if numPlayers < 1 or numPlayers > MAX_PLAYERS:
                self.log("ERROR: Bad num players")
                self.sendMessage(address, CLIENT_ERR_LOBBY_BAD_SIZE)
                raise Exception
            
            user = User(username, ip, port)
            if self.getUserLobby(user) != None:
                self.log("ERROR: Duplicate user found")
                self.sendMessage(address, CLIENT_ERR_USER_IN_LOBBY)
                raise Exception
            
            if self.getLobby(lobbyName) != None:
                self.log("ERROR: Duplicate lobby found")
                self.sendMessage(address, CLIENT_ERR_LOBBY_NAME_TAKEN)
                raise Exception
            lobby = Lobby(lobbyName, numPlayers, user)
            
            self.activeLobbies.append(lobby)
            self.log("Created lobby: " + str(lobby))
            
            self.sendMessage(address, CLIENT_SUCC_HOST_LOBBY)
            self.sendChat(lobby, username + " started hosting the lobby.")
            self.updateLobbyInfo(lobby)
            
        except Exception as e:
            raise e

    def joinLobby(self, address : Tuple, message : string):
        self.log("Receive request to join lobby: " + message)
        try:
            ip, port = address
            lobbyName, username = self.parseJoinInfo(message)
            
            lobby = self.getLobby(lobbyName)
            if lobby == None:
                self.log("ERROR:  Join lobby not found")
                self.sendMessage(address, CLIENT_ERR_NO_LOBBY_FOUND)
                raise Exception
            
            if lobby.isUsernameTaken(username):
                self.log("ERROR: Username in use")
                self.sendMessage(address, CLIENT_ERR_USERNAME_TAKEN)
                raise Exception
            
            user = User(username, ip, port)
            if self.getUserLobby(user) != None:
                self.log("ERROR: Duplicate user found")
                self.sendMessage(address, CLIENT_ERR_USER_IN_LOBBY)
                raise Exception
            
            if not lobby.addUser(user):
                self.log("ERROR: User could not join lobby")
                self.sendMessage(address, CLIENT_ERR_COULD_NOT_JOIN)
                raise Exception
            
            self.log(str(user) + " successfully joined " + str(lobby))
            lobby.addUser(user)
            self.sendMessage(address, CLIENT_SUCC_JOIN_LOBBY)
            self.sendChat(lobby, username + " has joined the lobby.")
            self.updateLobbyInfo(lobby)
            
            
        except Exception as e:
            raise e

    def publicQuery(self, address : Tuple, message : string):
        self.log("Receive request for public query: " + message)
        try:
            publicLobbies = []
            for lobby in self.activeLobbies:
                if lobby.isPublic():
                    publicLobbies.append(lobby)
            self.sendMessage(address, CLIENT_INFO_PUBLIC_LOBBIES + DEL_HANDLER + DEL_MESSAGE.join([lobby.name for lobby in publicLobbies]))
            
        except Exception as e:
            raise e

    def playerReady(self, address : Tuple, message : string):
        self.log("Receive request to be set ready: " + message)
        try:
            user, lobby = self.getUserAndLobbyFromAddress(address)
            if user == None:
                self.log("ERROR: User not in a lobby")
                self.sendMessage(address, CLIENT_ERR_NOT_IN_LOBBY)
                raise Exception
            
            isReady = self.parseReadyInfo(message)[0]
            user.setReady(isReady)
            self.updateLobbyInfo(lobby)
            
        except Exception as e:
            raise e
    
    def chatMessage(self, address : Tuple, message : string):
        self.log("Receive request to send chat message: " + message)
        try:
            chatUser, chatLobby = self.getUserAndLobbyFromAddress(address)
            
            if chatUser == None or chatLobby == None:
                self.log("ERROR: User not in a lobby")
                self.sendMessage(address, CLIENT_ERR_NOT_IN_LOBBY)
                raise Exception
            
            self.sendChat(chatLobby, chatUser.username + ": " + message)
            
        except Exception as e:
            raise e
    
    def sendChat(self, chatLobby : Lobby, chatMessage : string):
        for user in chatLobby.users:
            self.sendMessage((user.ip, user.port), CLIENT_INFO_CHAT + DEL_HANDLER + chatMessage)
    
    def startGame(self, address : Tuple, message : string):
        self.log("Receive request to start game: " + message)
        try:
            startUser, startLobby = self.getUserAndLobbyFromAddress(address)
            
            if startUser == None or startLobby == None:
                self.log("ERROR: User not in a lobby")
                self.sendMessage(address, CLIENT_ERR_NOT_IN_LOBBY)
                raise Exception
            
            if not startLobby.isHost(startUser):
                self.log("ERROR: Cannot start, user is not host")
                self.sendMessage(address, CLIENT_ERR_NOT_HOST)
                raise Exception
            
            if not startLobby.isAllUsersReady():
                self.log("ERROR: Cannot start, users not ready")
                self.sendMessage(address, CLIENT_ERR_USERS_NOT_READY)
                raise Exception
            
            userData = [user.ip + ":" + str(user.port) for user in startLobby.users]
            dispatchPort : int = dispatcher.dispatch(userData)
            for user in startLobby.users:
                self.sendMessage((user.ip, user.port), CLIENT_SUCC_START_GAME + DEL_HANDLER + str(dispatchPort))
            self.activeLobbies.remove(startLobby)
            
        except Exception as e:
            raise e
        

    def kickPlayer(self, address : Tuple, message : string):
        self.log("Receive request to kick player: " + message)
        try:
            fromUser, fromLobby = self.getUserAndLobbyFromAddress(address)
            kickUser = fromLobby.getUserFromName(message)
            
            if fromUser == None or fromLobby == None:
                self.log("ERROR: User not in a lobby")
                self.sendMessage(address, CLIENT_ERR_NOT_IN_LOBBY)
                raise Exception
            
            if not fromLobby.isHost(fromUser):
                self.log("ERROR: Cannot kick, user is not host")
                self.sendMessage(address, CLIENT_ERR_NOT_HOST)
                raise Exception
            
            if kickUser == None:
                self.log("ERROR: Cannot kick, no target found")
                self.sendMessage(address, CLIENT_ERR_NO_USER_FOUND)
                raise Exception
            
            self.removeUserFromLobby(fromLobby, kickUser)
            self.sendMessage((kickUser.ip, kickUser.port), CLIENT_ERR_KICKED)
            self.updateLobbyInfo(fromLobby)
            
        except Exception as e:
            raise e

    def banPlayer(self, address : Tuple, message : string):
        self.log("Receive request to ban player: " + message)
        try:
            fromUser, fromLobby = self.getUserAndLobbyFromAddress(address)
            bannedUser = fromLobby.getUserFromName(message)
            
            if fromUser == None or fromLobby == None:
                self.log("ERROR: User not in a lobby")
                self.sendMessage(address, CLIENT_ERR_NOT_IN_LOBBY)
                raise Exception
            
            if not fromLobby.isHost(fromUser):
                self.log("ERROR: Cannot ban, user is not host")
                self.sendMessage(address, CLIENT_ERR_NOT_HOST)
                raise Exception
            
            if bannedUser == None:
                self.log("ERROR: Cannot ban, no target found")
                self.sendMessage(address, CLIENT_ERR_NO_USER_FOUND)
                raise Exception
            
            self.removeUserFromLobby(fromLobby, bannedUser)
            fromLobby.banUser(bannedUser)
            self.sendMessage((bannedUser.ip, bannedUser.port), CLIENT_ERR_BANNED)
            self.updateLobbyInfo(fromLobby)
            
        except Exception as e:
            raise e

    def pingReceived(self, address : Tuple, message : string):
        self.log("Receive ping: " + message)
        user = self.getUserFromAddress(address)
        if user != None:
            user.updateTime()
        else:
            self.sendMessage(address, CLIENT_ERR_LOBBY_TIMEOUT, 3)
        

    def playerExit(self, address : Tuple, message : string):
        self.log("Receive request to exit from player: " + message)
        try:
            user, lobby = self.getUserAndLobbyFromAddress(address)
            if user == None or lobby == None:
                self.log("ERROR: User not in a lobby")
                self.sendMessage(address, CLIENT_ERR_NOT_IN_LOBBY)
                raise Exception
            
            self.removeUserFromLobby(lobby, user)
            self.updateLobbyInfo(lobby)
            
        except Exception as e:
            raise e

###################################################################################################
    
    def updateLobbyInfo(self, lobby : Lobby):
        userString = CLIENT_INFO_PLAYERS + DEL_HANDLER
        for i in range(len(lobby.users)):
            user = lobby.users[i]
            if i != 0:
                userString += DEL_MESSAGE
            userString += (user.username + DEL_SUB + ("1" if user.ready else "0"))
        
        for user in lobby.users:
            self.sendMessage((user.ip, user.port), userString)
    
    def parseHostInfo(self, message : string) -> Tuple:
        split = message.split(DEL_MESSAGE)
        if len(split) != 3:
            self.log("ERROR: Invalid host info received " + message)
            raise Exception
        return split[0], int(split[1]), split[2]

    def parseJoinInfo(self, message : string) -> Tuple:
        split = message.split(DEL_MESSAGE)
        if len(split) != 2:
            self.log("ERROR: Invalid join info received " + message)
            raise Exception
        return split[0], split[1]
    
    def parseReadyInfo(self, message : string) -> Tuple:
        return [message == "1"]
    
###################################################################################################
    
    def getUserAndLobbyFromAddress(self, address : Tuple) -> Tuple:
        rtnUser = None
        rtnLobby = None
        for lobby in self.activeLobbies:
            user = lobby.getUserFromAddress(address)
            if user != None:
                rtnUser = user
                rtnLobby = lobby
        return rtnUser, rtnLobby
    
    def getUserAndLobbyFromName(self, username : string) -> Tuple:
        rtnUser = None
        rtnLobby = None
        for lobby in self.activeLobbies:
            user = lobby.getUserFromName(username)
            if user != None:
                rtnUser = user
                rtnLobby = lobby
        return rtnUser, rtnLobby
    
    def getUserFromName(self, username : string) -> User:
        for lobby in self.activeLobbies:
            user = lobby.getUserFromName(username)
            if user != None:
                return user
        return None
    
    def getUserFromAddress(self, address : Tuple) -> User:
        for lobby in self.activeLobbies:
            user = lobby.getUserFromAddress(address)
            if user != None:
                return user
        return None
    
    def getUserLobby(self, user : User) -> Lobby:
        for lobby in self.activeLobbies:
            if lobby.isInLobby(user):
                return lobby
        return None
    
    def getLobby(self, lobbyName : string) -> Lobby:
        for lobby in self.activeLobbies:
            if lobby.name == lobbyName:
                return lobby
        return None


