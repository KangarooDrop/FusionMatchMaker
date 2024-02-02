from typing import Tuple

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import deferLater

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


class Server(DatagramProtocol):

    def __init__(self):
        self.debug = False
        self.activeLobbies : Dictionary = {}
        self.dispatchedLobbies : Dictionary = {}

    def datagramReceived(self, datagram, address):
        datagramString = datagram.decode("utf-8")
        if self.debug:
                print("Datagram received: ", datagramString)


# Helper method to pause execution for n seconds
def sleep(seconds):
    return deferLater(reactor, seconds, lambda: None)
