
from socket import socket
import subprocess

def getFreePort() -> int:
    serverSocket = socket()
    serverSocket.bind(('', 0))
    port = serverSocket.getsockname()[1]
    return port

def dispatch(userData) -> int:
    port = getFreePort()
    path = "exe/FusionServer.console.exe"
    args = ""
    args += " -p " + str(port)
    for ud in userData:
        args += " -c " + ud

    lineArgs = (path + args).split(" ")
    print("Dispatching a server for " + str(userData) + "\n\t" + str(lineArgs))
    
    process = subprocess.Popen(lineArgs)
    return port

