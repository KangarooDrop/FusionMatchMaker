import sys
from twisted.internet import reactor
from server import Server


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3 or (len(sys.argv) == 3 and sys.argv[2] != "DEBUG"):
        print("Usage: ./main.py <port>")
        print("Run with debug: ./main.py <port> DEBUG")
        sys.exit(1)

    port = int(sys.argv[1])
    server = Server()
    if len(sys.argv == 3) and sys.argv[2] == "DEBUG":
        server.debug = True
    reactor.listenUDP(port, server)
    reactor.run()
