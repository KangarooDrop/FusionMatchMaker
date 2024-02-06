
from socket import socket
import subprocess

def getFreePort() -> int:
    serverSocket = socket()
    serverSocket.bind(('', 0))
    port = serverSocket.getsockname()[1]
    return port

def dispatch(userData, debug = False) -> int:
    port = getFreePort()
    path = "exe/FusionServer.exe"
    args = " --headless"
    args += " -p " + str(port)
    for ud in userData:
        args += " -c " + ud

    lineArgs = (path + args).split(" ")
    print("Dispatching a server for " + str(userData) + "\n\t" + str(lineArgs))
    
    if debug:
        process = subprocess.Popen(lineArgs)
    else:
        process = subprocess.Popen(lineArgs, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return port

