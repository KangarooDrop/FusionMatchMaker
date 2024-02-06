
import time
import string
from typing import List, Dict, Tuple

from user import User

LOBBY_TIMEOUT = 15 * 60.0

def getTime() -> float:
    return time.time()

class Lobby:

    def __init__(self, name : str, maxUsers : int, host : User):
        self.name: str = name
        self.maxUsers: int = maxUsers
        self.host : User = host
        self.users: List = [host]
        self.lastTime : int = getTime()
        self.public : bool = False
        self.bannedUserAddresses = []
    
    

    def isTimedOut(self) -> bool:
        return (self.host == None) or (getTime() - self.lastTime > LOBBY_TIMEOUT)

    def isFull(self) -> bool:
        return len(self.users) >= self.maxUsers
    
    def isInLobby(self, user : User) -> bool:
        return user in self.users
    
    def isHost(self, user : User) -> bool:
        return self.host == user
    
    def isAllUsersReady(self) -> bool:
        for user in self.users:
            if not user.ready:
                return False
        return True
    
    def isPublic(self) -> bool:
        return self.public
    
    def getUserFromName(self, username : string):
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def getUserFromAddress(self, address : Tuple):
        ip, port = address
        for user in self.users:
            if user.ip == ip and user.port == port:
                return user
        return None
    
    def banUser(self, user : User):
        if user != None:
            self.bannedUserAddresses.append((user.ip, user.port))
    
    def isUsernameTaken(self, username : string) -> bool:
        for user in self.users:
            if user.username == username:
                return True
        return False
    

    def addUser(self, user : User) -> bool:
        if self.isFull():
            return False
        if user in self.users:
            return False
        if (user.ip, user.port) in self.bannedUserAddresses:
            return False
        
        self.users.append(user)
        if self.host == None:
            self.host = user
        return True
    
    def removeUser(self, userToRemove : User):
        rehost = self.isHost(userToRemove)
        self.users.remove(userToRemove)
        if rehost:
            if len(self.users) > 0:
                self.host = self.users[0]
            else:
                self.host = None
    
    
    
    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "Lobby(name=" + self.name + ", maxUsers=" + str(self.maxUsers) + ", host=" + str(self.host) + ", users=" + str(self.users) + ", lastTime=" + str(self.lastTime) + ")"
