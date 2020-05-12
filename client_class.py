import socket
import _thread
import threading
import time
from threading import Thread
import sys, errno

class Client:

    formatCode = '\x1b[s\r\x1b[1A'
    selfMsg = "Me > "
    othersMsg = "{0} > {1}"
    startMsg = "Client server... "
    serverMsg = "Enter chat server IP address and port: "
    clientMsg = "Enter your username: "
    connMsg = "Trying to connect to the server {0}, {1}"
    successMsg = "Connected..."
    def __init__(self):
        self.isQuit = False
        self.lock = threading.Lock()
        self.threads = []
        self.isEcho = True

    def echoServer(self):
        while(not self.isQuit):
            time.sleep(10)
            msg = "This is an echo"
            self.socket.send(bytes("\\. " + msg , "utf-8"))


    def printMsg(self, msg, option = 'n'):
        print(msg, end='\n\x1b[0K')
        if(option == 'n'):
            print('\n' + self.selfMsg, end='')

    def listenForMessages(self):
        while(not self.isQuit):
            try:
                incomingMsg = self.socket.recv(1024)
                incomingMsg = incomingMsg.decode("utf-8")
            except:
                print("Failed to read socket")
                self.isQuit = True
            else:
                try:
                    if(incomingMsg == ""):
                        raise ValueError
                    else:
                        hostName, msg = [str(x) for x in incomingMsg.split(" ", 1)]
                    if(msg[0:2] != "\\."):
                        self.printMsg(self.formatCode + self.othersMsg.format(hostName, msg))
                    else:
                        if(self.isEcho):
                            header, msg = msg.split(" ", 1)
                            self.printMsg(self.formatCode + "Echoed: " + msg)
                except Exception as e:
                    if(type(e).__name__ == "ValueError"):
                        self.socket.close()
                        self.isQuit = True
                        print("Server suddenly closed")
                    else:
                        print("The message received contains a problem")
                else:
                    #print(othersMsg.format(hostName, msg))
                    if(msg == "Has ended the chat server"):
                        self.isQuit = True

    def sendMsg(self):
        while(not self.isQuit):
            outGoing = input('\n' + self.selfMsg)
            if(outGoing == "/quit"):
                self.socket.send(bytes("\\q", "utf-8"))
                self.lock.acquire()
                self.isQuit = True
                self.lock.release()
                break
            elif(outGoing == "/toggleEchoPrint"):
                self.lock.acquire()
                self.isEcho = not self.isEcho
                self.lock.release()
                self.printMsg(self.formatCode + "You have toggled Echo Print to: " + str(self.isEcho), 'r')
            else:
                self.socket.send(bytes(outGoing, "utf-8"))

    def setSocket(self, socket):
        self.socket = socket

    def setIpAddr(self, ip, port):
        self.addr = (ip, int(port))

    def getIpAddr(self):
        return self.addr

    def setUsername(self, username):
        self.username = username

    def setThread(self, thread):
        self.threads.append(thread)

if (__name__ == "__main__"):
    ip = ""
    port = 0

    #socket.SOCK_STREAM specifies a TCP-oriented connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = Client()

    isValid = False
    while(not isValid):
        try:
            ip, port = [str(x) for x in input(client.serverMsg).split()]
            if(ip == "0"):
                ip = "127.0.0.1"
            if(port == "0"):
                port = 8080
            try:
                octet = ip.split(".")
                for i in octet:
                    if(len(i) <= 3):
                        part = int(i)
                        if(part < 0 or part > 255):
                            raise ValueError
                    else:
                        raise ValueError
            except:
                print("Invalid IP")
                raise ValueError
            try:
                port = int(port)
                if(port < 1 or port > 65535):
                    raise ValueError
                isValid = True
            except:
                print("Port is not a valid number!")
                raise ValueError
        except:
            isValid = False
            print("\nInvalid input!! Key in both the IPv4 Address and Port")
    
    username = str(input(client.clientMsg))
    client.setIpAddr(ip, port)
    client.setUsername(username)
    client.setSocket(s)
    addr = client.getIpAddr()
    print(client.connMsg.format(addr[0], addr[1]))

    canConnect = False
    try:
        s.connect(addr)
        canConnect = True
    except:
        print("Connection failed! Server or port may not be open")

    # Run only if connection to socket succeeds
    if(canConnect):
        incomingMsg = s.recv(1024)
        print(incomingMsg.decode("utf-8"))
        s.send(bytes(username, "utf-8"))
        try:
            t = Thread(name="SendMsg", target=client.sendMsg)
            t.setDaemon(True)
            t.start()
            client.setThread(t)
            t = Thread(name="ListenForMessage", target=client.listenForMessages)
            t.setDaemon(True)
            t.start()
            client.setThread(t)
            t = Thread(name="EchoServer", target=client.echoServer)
            t.setDaemon(True)
            t.start()
            client.setThread(s)
        except:
            print("Client thread failed to start!!")

        while (not client.isQuit):
            pass
    s.close()