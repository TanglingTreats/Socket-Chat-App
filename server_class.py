import socket
import _thread
import threading
from threading import Thread
import sys, errno

class Server:
    # specify ip and port that users connect to
    host = ""
    newUser = False

    # String formats
    formatCode = '\x1b[s\r\x1b[1A'
    postFormatCode = '\x1b[u'
    selfMsg = "Me > "
    othersMsg = "{0} > {1}"
    welcomeMsg = "This is Networking Chat server, please enter the listening address and port \n"
    namePrompt = "Enter name: "
    waitPrompt = "Waiting for incoming connections..."
    connectionNotif = "\nReceived connection from {0}"
    successNotif = "Connection Established. Connected From: {0}, {1}"
    connectPrompt = "{0} has joined the chat"
    msgToSend = "{0} {1}"

    def __init__(self):
        self.lock = threading.Lock()
        self.numClients = 10
        # keeps track of the number of users connected to the server
        self.clientSocketList = []
        self.totalThreads = []
        self.isQuit = False
        self.threads = []
        self.startChat = False

    def printMsg(self, msg, option = 'n'):
        print(msg, end='\n\x1b[0K')
        if(option == 'n'):
            #prevMsg = sys.stdin.buffer.read()
            #print(prevMsg)
            #sys.stdout.write('\r')
            print('\n' + self.selfMsg, end='')
            #sys.stdout.write(sys.stdout.buffer)

    def acceptIncomingHosts(self):
        isFirstConnection = True
        while(not self.isQuit):
            clientSocket, address = self.socket.accept()
            print(self.connectionNotif.format(address))
            print("")
            print(self.successNotif.format(self.addr[0], address))
            self.clientSocketList.append(clientSocket)
            clientSocket.send(bytes("Connected...", "utf-8"))
            hostName = clientSocket.recv(1024)
            hostName = hostName.decode("utf-8")
            if(isFirstConnection):
                self.printMsg('\n' + self.connectPrompt.format(hostName), 'r')
                isFirstConnection = False
            else:
                self.printMsg('\n' + self.connectPrompt.format(hostName))
            self.sendNotif(clientSocket, hostName)
            self.startChat = True
            try:
                t = Thread(name="Listen_To_Client", target=self.listenToClient,args=(clientSocket, hostName))
                t.setDaemon(True)
                self.setThreads(t)
                t.start()
                # _thread.start_new_thread(listenToClient, (clientSocket, hostName))
            except:
                print("Failed to start thread after receiving connection!!")

    #   Method: Listen to client that has been accepted. Each thread is responsible for handling its own client
    #   Once the listener receives the quit message, it is removed from the clientSocketList and the loop is broken
    def listenToClient(self, client, hostName):
        hasClient = True
        while(not self.isQuit):
            try:
                msg = client.recv(1024)
            except:
                print("Client has closed connection!")
                self.clientSocketList.remove(client)
                print("Inactive client removed")
                break
            if(not msg):
                break
            msg = msg.decode("utf-8")
            if(msg is not None):
                if(msg[0:2] != "\\."):
                    for x in self.clientSocketList:
                        if(x != client):
                            try:
                                if(msg == "\\q"):
                                    x.send(bytes(self.msgToSend.format(hostName, "Has quit the server"), "utf-8"))
                                else:
                                    x.send(bytes(self.msgToSend.format(hostName, msg), "utf-8"))
                            except:
                                self.printMsg(self.formatCode + "Host is no longer available")
                                self.clientSocketList.remove(x)
                                hasClient = False
                                break
                    if(not hasClient):
                        break
                    

                    if(msg == "\\q"):
                        self.printMsg(self.formatCode + self.othersMsg.format(hostName, "Has quit the server"))
                        client.close()
                        self.clientSocketList.remove(client)
                        break
                    else:
                        self.printMsg(self.formatCode + self.othersMsg.format(hostName, msg))
                else:
                    client.send(bytes(self.msgToSend.format(hostName, msg), "utf-8"))

    def sendNotif(self, client, hostName):
        for x in self.clientSocketList:
            if(client != x):
                try:
                    msg = "Has joined the chat"
                    x.send(bytes(self.msgToSend.format(hostName, msg), "utf-8"))
                except:
                    print("Message failed to send")

    def outGoingMsg(self):
        while(not self.isQuit):
            if(self.startChat):
                msg = input('\n' + self.selfMsg)
                if(msg == "/quit"):
                    for x in self.clientSocketList:
                        quitMsg = "Has ended the chat server"
                        try:
                            x.send(bytes(self.msgToSend.format(self.host, quitMsg), "utf-8"))
                        except IOError as e:
                            if e.errno == errno.EPIPE:
                                print("Epipe")
                                print("ERROR - Message not sent! Client does not exist!")
                                self.lock.acquire()
                                self.clientSocketList.remove(x)
                                self.lock.release()
                    self.lock.acquire()
                    self.isQuit = True
                    self.lock.release()
                    # break
                else:
                    for x in self.clientSocketList:
                        try:
                            x.send(bytes(self.msgToSend.format(self.host, msg), "utf-8"))
                        except:
                            self.printMsg(self.formatCode + "ERROR - Message not sent! Client does not exist!")
                            self.clientSocketList.remove(x)
        

    def setServerHost(self, hostName):
        self.host = hostName

    def setIpAddr(self, ip, port):
        self.addr = (ip, int(port))

    def getIpAddr(self):
        return self.addr

    def setSocket(self, socket):
        self.socket = socket

    def setThreads(self, thread):
        self.threads.append(thread)

# ------------------ Start Program --------------
if(__name__ == "__main__"):

    ip = ""
    port = 0

    #socket.SOCK_STREAM specifies a TCP-oriented connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server = Server()
    server.setSocket(s)
    isValid = False
    while(not isValid):
        try:
            ip, port = [str(x) for x in input(server.welcomeMsg).split()]
            if(ip == "0"):
                ip = "127.0.0.1"
            if(port == "0"):
                port = "8080"

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
        except:
            isValid = False
            print("Invalid input! Key in both IPv4 address and Port!")
    
    host = input(server.namePrompt)
    print(server.waitPrompt)

    server.setServerHost(host)
    server.setIpAddr(ip, port)
    canConnect = False
    try:
        s.bind(server.getIpAddr())
        # prepare socket for listening
        s.listen(server.numClients)
        canConnect = True
    except:
        print("Failed to bind socket or start listening")


    if(canConnect):
        try:
            t = Thread(name="Accept_Hosts", target=server.acceptIncomingHosts)
            t.setDaemon(True)
            t.start()
            server.setThreads(t)
            t = Thread(name="Server_Outgoing", target=server.outGoingMsg)
            t.setDaemon(True)
            t.start()
            server.setThreads(t)
        except:
            print("Unable to start threads!!")

        while (not server.isQuit):
            pass
        try:
            s.close()
        except:
            print("Failed to close")



