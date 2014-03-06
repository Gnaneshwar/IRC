"""

Name: IRC server
Purpose: Serves as a common formal platform as a means of communication 
Author: Gnaneshwar Reddy
Created : 17-Nov-2013

"""

import socket, select
from copy import *


"""a dictionary mapping commands with the function pointers of these command handlers"""
list_of_commands = {}

class chatRoom:
    """class that encapsulates all the attributes of chatRoom"""
    
    #if it don't work -> in __init__ initialize the variables
    def __init__(self,admin_chatroom,admin_sock,name_chatRoom,client_list,client_names):
        #intialize the chatroom object given chatroomname, admin name and other required attributes
        
        self.admin = admin_chatroom
        self.admin_sock = admin_sock
        self.name = name_chatRoom
        self.users = deepcopy(client_names) # dict - {host->{port -> name}} - contains all the users
        self.client_socks = copy(client_list) # dict (sock->addr) - conatins all the sockets of users


    def isOnline(self,msg_sender_sock,dest_sock):
        #to check who is online
        if(dest_sock in self.users):
            try:
                msg_sender_sock.send("Yes,destination is active")
            except:
                msg_sender_sock.send("No,destination is inactive")
                self.removeClient(dest_sock)
        else:
            msg_sender_sock.send("there is no user named **** found in this chatRoom")
    

    def privateMsg(self,msg_sender_sock,msg_recvr_sock,message):
        #one -to -one communication
        if(msg_recvr_sock in self.client_socks.keys()):
            try:
                msg_recvr_sock.send(message)
                #msg_sender_sock("sent")
            except:
                msg_recv_sock.close()
                self.removeClient(msg_recv_sock)
                #msg_sender_sock.send("Inactive destination,Sending failed")


    
    def broadcast(self,msg_sender_sock, message): #one -to -many communication
        # broacast message to all clients in chat room
        
       
        
        #for every socket user present in the chatroom
        for socket in self.client_socks.keys():
            #except the mssg sender and the server
            if socket != server_socket and socket != msg_sender_sock : #-> scope of server_socket ?; global var might work
                try :
                    #send the message
                    socket.send(message) 
                except :
                    #if the socket is not active remove it from the list of clients 
                    self.removeClient(socket)#swapped
                    socket.close()
    

    def broadcast1(self,msg_sender_sock, message): #one -to -many communication
        # broacast message to all clients in chat room
        
        # check if the socket exists in the list of clients
        if socket in self.client_socks.keys(): 
            try :
                print "sending:",message
                socket.send(message) 
            except :
                socket.close()
                self.removeClient(socket)#swapped
                
                    

    def add_client(self,client_socket,client_name):
        """it adds the client in the chatroom and updates all the records maintained by the chatroom"""

        #get host and port number to which the socket is connected
        host, port = client_socket.getpeername()
        
        #update glob list
        glob_list[(client_socket.getpeername())][client_name].append(self.name)   
        
        #if host already present
        if host in self.users.keys():
            self.users[host][port] = client_name
        else:
            self.users[host] = {port:client_name}
        print self.users[host]
        #update client sockets
        self.client_socks[client_socket] = (host, port)

    def removeClient(self, sock) : 
        """ remove a client from the chatroom and update the chatroom records """
        host = sock.getpeername()[0]
        port =sock.getpeername()[1]
        
        try:
            # update the chatroom
            del self.users[host][port]
            del self.client_socks[sock]
            del glob_list[(sock.getpeername())]

        except:
            pass    

                

def parse_command(mssg_sender_sock,message):
    """ It parses the command and handles it accordingly"""
    print "in parse command"
    list_of_words = message.split()
    #print list_of_words
    print list_of_commands
    
    # if the user types a command
    if list_of_words[0] in list_of_commands.keys():
        print "True"
        # function pointer of the command is used for calling the function 
        # with the arguments
        if(len(list_of_words) > 1):
            list_of_commands[list_of_words[0]](mssg_sender_sock, list_of_words[1:])
        else:
            list_of_commands[list_of_words[0]](mssg_sender_sock)
        return True
        
    # if a simple message
    else:
        return None

        
def who(mssg_sender_sock, arguments): # arguments-> chatroom_name
    """ Returns a list of users who belong to the particular chatRoom"""
    
    chatRoom_name = arguments[0] #first argument is the chatroom name
    
    # if chatroom name exists 
    if chatRoom_name in chatRoom_list.keys():
        chatRoom_obj = chatRoom_list[arguments[0]]
        user_names = []
        #get all the clients in the given chatroom
        for key in chatRoom_obj.users.keys():
            for key2 in chatRoom_obj.users[key].keys():
                if chatRoom_obj.users[key][key2] not in user_names:
                    user_names.append((chatRoom_obj.users)[key][key2])
        
        user_names.remove('server') # dont send the results to the server
        
        i = len(user_names)
        while i: #sending one username at a time
            temp = user_names[i-1]
            temp = temp+"\n "
            mssg_sender_sock.send(temp) #replying to requested client
            i = i-1

    else:
        reply = "Not a valid chatroom name\n"
        mssg_sender_sock.send(reply)


def whois(mssg_sender_sock,arguments): #arguments -> chatroom,clientName
    """ Returns the information about given client in the given chat """
    if(len(arguments) == 2 ):
        chatRoom_name = arguments[0]
        
        # if the given chatroom name does not exist
        if chatRoom_name in chatRoom_list.keys():
            chatRoom_obj = chatRoom_list[arguments[0]]
            flag =  False
            host ="" 
            port = 9394

            # check if this client exists in the chatroom
            for key in chatRoom_obj.users.keys():
                for key2 in chatRoom_obj.users[key].keys():
                    if chatRoom_obj.users[key][key2] is arguments[1]:
                        flag = True
                        host = key
                        port = key2

            # if client is not present then send mssg to the client that it does not exist
            if flag == False:
                reply = "Client don't exist in this chat room\n"
                mssg_sender_sock.send(reply)
                reply3 = "End of whois\n"
                mssg_sender_sock.send(reply3)

            # otherwise send the IP address and port number of this client
            else:
                reply1 = "IP address: %s\n" %host
                reply2 = "Port %s \n" %port
                mssg_sender_sock.send(reply1)
                mssg_sender_sock.send(reply2)
                reply3 = "End of whois\n"
                mssg_sender_sock.send(reply3)

        # if chatroom does not exist
        else:
            reply = "chatRoom_name doesn't exist"
            mssg_sender_sock.send(reply)
            reply3 = "End of whois\n"
            mssg_sender_sock.send(reply3)       

    # if the number of arguments are not correct
    else:
        reply = "USage:chatRoom_name, client_name\n"
        mssg_sender_sock.send(reply)
        
            

def join(addr, sock,sockfd, name): #arguments: chatroom name
    """ Adding client to the requested chat room"""
    sockfd.send("Enter the chatroom name : (join chatroom_name) \n")
    lst = sockfd.recv(RECV_BUFFER)
    lst = lst.split()
    reply1 = "End of join\n"

    # check if arguments given are proper
    if len(lst) <= 2 :
        chatRoom_name = lst[1]
        #chatRoom_name = chatRoom_name[:-1]
        print chatRoom_name
        glob_list[addr] = {name:[]} #!!!!!!!!!!!!!! max elements in the list is 1 :o
                     
        temp = chatRoom_name

        # update the chatroom as new client joins it
        if str(chatRoom_name) in chatRoom_list.keys():

            chatRoom_list[chatRoom_name].add_client(sockfd,name)

            glob_list[addr][name].append(chatRoom_name)

        else:

            print "object intiated"
            chatRoom_obj = chatRoom(name,sockfd,chatRoom_name,clients,names)
            chatRoom_obj.add_client(sockfd,name)
        
            chatRoom_list[chatRoom_name] = chatRoom_obj
            glob_list[addr][name].append(chatRoom_name) 
        return chatRoom_name # return the chatroom name

    
    else:
        reply = "Usage: join chatRoom_name\n"       
        sockfd.send(reply)
        sockfd.send(reply1)
        return None


def private_msg():
    pass
    
#main function
if __name__ == "__main__":  
    
    w   = who
    ws  = whois
    jn  = join
    pmg = private_msg

    # it maintains the function pointers of all the command handler functions
    list_of_commands = {'who':w, 'whois':ws, 'join':jn, 'PMSG':pmg}
    #print list_of_commands

    CLIENT_LIST = {}
    NAME_LEN = 9
    RECV_BUFFER = 4096 
    PORT = 9395
    host = "localhost" # enter server address
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
    chatRoom_list ={} #{string -> object}

    #server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

    server_socket.bind((host, PORT)) #bind the socket with ip and port
    max_clinets = 10 # maximum number of queued connections 

    server_socket.listen(max_clinets)
    print "server listening...."

    #intialize list and names

    CLIENT_LIST[server_socket] = (host, PORT)
    clients = copy(CLIENT_LIST)
    CLIENT_NAMES = {host:{PORT:"server"}}
    names = deepcopy(CLIENT_NAMES)

    glob_list = {} #{addr ->{client_name(string) -> client_chats(string list)}}

    print "IRC SERVER RUNNING ON " + str(PORT)


    while 1:
        # get readable sockets 
        readable_sockets,writable_sockets,error_sockets = select.select(CLIENT_LIST.keys(),[],[]) # !! works only in unix type systems 
        
       
        # for every readable socket in the list
        for sock in readable_sockets:
                
                # if the socket is server socket add a  new client
                if sock == server_socket:
                    # to add clients
                    sockfd, addr = server_socket.accept()
                    print "accepted a new connection"
                
                    name = sockfd.recv(NAME_LEN)
                    name = name[:-1]
                    CLIENT_LIST[sockfd] = addr
                    chatRoom_name = join(addr, sock,sockfd,name )
                    #chatRoom_name = sockfd.recv(NAME_LEN)
                    #chatRoom_name = chatRoom_name[:-1]

                    #glob_list[addr] = {name:[]} #!!!!!!!!!!!!!! max elements in the list is 1 :o

                    print "Client %s connected  to the "  % name 
                    print "%s" %chatRoom_name
                    
                    if chatRoom_name is not None:                   
                        chatRoom_list[chatRoom_name].broadcast(sockfd,"(%s,%s) entered room\n" %sockfd.getpeername())
                
                # if a client send the message 
                else:
                    #normal client
                    host, port  = sock.getpeername()
                    addr = (host, port)
                    
                    name = glob_list[addr].keys()[0]  #!!!!!!!!!!!!!!!!!!!!!!!
                    #print "user name: ", name

                    print glob_list[addr][name]
                    cr_Name = glob_list[addr][name][0] #string
                    cr_obj = chatRoom_list[cr_Name] #obj
                    print "chatroom : ",cr_Name
                    
                    try:
                        # receive the message from the client
                        msg = sock.recv(RECV_BUFFER)
                        
                        # if the message is not empty
                        if len(msg):
                            print "addr: %s" %addr[0]
                            print "port: %s" %addr[1]

                            if not parse_command(sock, msg):
                                message ='<' + cr_obj.users[addr[0]][addr[1]] + '> ' + msg

                                print "about to broadcast : ",message
                                cr_obj.broadcast(sock, message)
                        
                    except:
                        
                        cr_obj.broadcast(sock, "Client %s is offline"  %name )
                        #print "Client %s is offline" % name 
                        cr_obj.removeClient(sock) # !!!!!!!
                        
                        sock.close()
                        try:
                            del CLIENT_LIST[sock]
                            del glob_list[addr]
                        except:
                            print "error"
                        continue
                       
    server_socket.close()
