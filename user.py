import time

USER_TIMEOUT = 5.0

def getTime() -> float:
    return time.time()

class User:
    def __init__(self, username: str, ip: str, port: int):
        self.username = username
        self.ip = ip
        self.port = port
        self.lastTime = getTime()
        self.ready = False
    
    def setReady(self, val : bool):
        self.ready = val
    
    def isTimedOut(self):
        return getTime() - self.lastTime > USER_TIMEOUT

    def updateTime(self):
        self.lastTime = getTime()

    def __eq__(self, other):
        if other is None:
            return False
        return self.ip == other.ip and self.port == other.port

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "User(username=" + self.username + ", ip=" + str(self.ip) + ", port=" + str(self.port) + ")"
