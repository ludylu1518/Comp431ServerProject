import sys
import os
import socket
from socket import *

#global variables to check for errors at each line
commandError = 0
syntaxError = 0
orderError = 0

#global variable to check for the current expected command
# 0 = HELO  1 = MAIL FROM  2 = RCPT TO   3 = DATA   4 = body
currentCommand = 0

#global variable to store the current rcpt email address
emailRCPT = ""

#global variable to store current email info
emailInfo = ""

#client Address
clientIp = ""

# check for commands MAIL, RCPT, DATA, HELO
def parseCommand(c):

    command = c[:4]

    if command == "MAIL":

        parseMail(c[4:])

        return 0

    elif command == "RCPT":

        parseRCPT(c[4:])

        return 0

    elif command == "DATA":

        if currentCommand != 3:
            global orderError
            orderError += 1

        else:
            parseData(c[4:])

        return 0
    
    elif command == "HELO":

        if currentCommand != 0:
            orderError += 1

        else:
            parseHELO(c[4:])
       
        return 0

    else:
        global commandError
        commandError += 1
    
    return 0


#HELO parser
def parseHELO(c):

    index = parseWhiteSpace(c)

    if index < 1:
        global commandError
        commandError += 1
    
    else:
        rest = c[index:]

        parseDomain2(rest)

    return 0


#domain parser for helo
def parseDomain2(c):

    global clientIp

    if not isLetter(c[0]):
         global syntaxError 
         syntaxError += 1 

    else:

        index = 0

        while isDigit(c[index]) or isLetter(c[index]) or c[index] == "-":
            clientIp += c[index]
            index += 1

        if c[index] == ".":
            parseDomain2(c[index + 1:])
        
        else:
            index1 = parseWhiteSpace(c[index])
            parserCRLF(c[index1 + index:])

    return 0


# Mail parser
def parseMail(c):  
   
    index = parseWhiteSpace(c)
    
    if index < 1:
        global commandError
        commandError += 1
    
    else:  
        rest = c[index:]

        if rest[:5] == "FROM:":

            if currentCommand != 1:
                global orderError 
                orderError += 1

            else:
                parsePath(rest[5:])   

        else:
           commandError += 1

    return 0


#RCPT parser
def parseRCPT(c):

    index = parseWhiteSpace(c)
    
    if index < 1:
        global commandError
        commandError += 1
    
    else:  
        rest = c[index:]

        if rest[:3] == "TO:":

            if currentCommand != 2:
                global orderError
                orderError += 1

            else:
                parsePath(rest[3:])   

        else:
           commandError += 1


    return 0
    

#whiteSpace/nullspace parser
def parseWhiteSpace(c):
    index = 0

    while c[index] == " " or c[index] == "\t":        
        index += 1

    return index


#DATA parser
def parseData(c):
    
    global commandError

    if c[0] != " " and c[0] != "\t" and c != "\n":
        commandError += 1
    
    else:
        index = parseWhiteSpace(c)
        parserCRLF(c[index:])

    return 0


#path parser
def parsePath(c):
    global emailRCPT
    global syntaxError

    index = parseWhiteSpace(c)

    rest = c[index:]

    if rest[0] == "<":
        parseMailBox(rest[1:])

        if currentCommand == 2 and syntaxError < 1:
            
            count = 1

            emailRCPT = ""

            while rest[count] != "@":
                count += 1

            count += 1

            while rest[count] != ">":
                emailRCPT += rest[count]
                count += 1
            
    else:
        syntaxError += 1

    return 0

#CRLF parser
def parserCRLF(c):
    
    if c != "\n":
        global syntaxError
        syntaxError += 1


#MailBox parser
def parseMailBox(c):

    index = parseString(c)

    if index < 1:
        global syntaxError 
        syntaxError += 1
    
    else:    
        rest = c[index:]

        if rest[0] == "@":
            parseDomain(rest[1:])

        else:
            syntaxError += 1 

    return 0


#domain parser
def parseDomain(c):

    if not isLetter(c[0]):
         global syntaxError 
         syntaxError += 1 

    else:
        rest = c[1:]
        index = 0

        while isDigit(rest[index]) or isLetter(rest[index]) or rest[index] == "-":
            index += 1

        if rest[index] == ".":
            parseDomain(rest[index + 1:])

        elif rest[index] == ">":
        
            total = parseWhiteSpace(rest[index + 1:])
            parserCRLF(rest[index + total + 1:])

        else:
            syntaxError += 1


    return 0


#String parser
def parseString(c):
    
    index = 0

    while not isSpecialChar(c[index]) and c[index] != " " and c[index] != "\t":
        index += 1

    return index


#check if is a number
def isDigit(c):

    if c == "0" or c == "1" or c == "2" or c == "3" or c == "4" or c == "5" or c == "6" or c == "7" or c == "8" or c == "9":
        return True
    
    else:
        return False
    

#check if is A-Z/a-z
def isLetter(c):

    if c.lower() == "a" or c.lower() == "b" or c.lower() == "c" or c.lower() == "d" or c.lower() == "e" or c.lower() == "f" or c.lower() == "g" or c.lower() == "h" or c.lower() == "i" or c.lower() == "j" or c.lower() == "k" or c.lower() == "l" or c.lower() == "m" or c.lower() == "n" or c.lower() == "o" or c.lower() == "p" or c.lower() == "q" or c.lower() == "r" or c.lower() == "s" or c.lower() == "t" or c.lower() == "u" or c.lower() == "v" or c.lower() == "w" or c.lower() == "x" or c.lower() == "y" or c.lower() == "z":
        return True
    
    else:
        return False


#check if is special character
def isSpecialChar(c):

    if c == ">" or c == "<" or c == "(" or c == ")" or c == "[" or c == "]" or c == "\\" or c == "." or c == "," or c == ";" or c == ":" or c == "@" or c == "\"":
        return True
    
    else:
        return False



#body text parser
def parseBody(c):
    global emailRCPT
    global emailInfo


    if c == ".":  
        
        #reset command back to HELO    
        global currentCommand
        currentCommand = 0

        global connectionSocket

        m = "250 OK"
        sys.stdout.write(m)
        connectionSocket.sendall(m.encode("utf-8"))
        
        #write info into file
        with open(f'forward/' +  emailRCPT , 'a') as f:
            f.write(emailInfo)


        #Reset emailInfo
        emailInfo = ""

    return 0


#setting up socket
serverPort = int(sys.argv[1])

serverSocket = socket(AF_INET, SOCK_STREAM)
host = gethostname()
#host = "localhost"
serverSocket.bind((host, serverPort))
serverSocket.listen(1)

#listening for messages
while True:

    #setting up connection
    try:
        connectionSocket, addr = serverSocket.accept()
    except Exception as e:
        sys.stdout.write("connection error when trying to connect to client")
        connectionSocket.close()


    #sending the greeting message
    greeting = "220 " + host
    sys.stdout.write(greeting + "\n")
    connectionSocket.sendall(greeting.encode("utf-8"))


    #receiving greeting message from client
    try:
        line = connectionSocket.recv(1024).decode()
    except Exception as e:
        sys.stdout.write("cannot receive message from client error")
        exit()


    currentCommand = 0

    while line != "QUIT\n":

        commandError = 0
        orderError = 0
        syntaxError = 0

        sys.stdout.write(line)     

        if currentCommand == 4:
            emailInfo += line
            lineList = line.split("\n")

            for i in range(len(lineList)):           
                parseBody(lineList[i])


        else: 
            parseCommand(line)


            if commandError > 0:
                commandMessage = "500 Syntax error: command unrecognized"
                #sys.stdout.write("500 Syntax error: command unrecognized\n") 
                
                connectionSocket.sendall(commandMessage.encode("utf-8"))

            
            elif orderError > 0:
                orderMessage = "503 Bad sequence of commands"
                #sys.stdout.write("503 Bad sequence of commands\n")
                            
                connectionSocket.sendall(orderMessage.encode("utf-8"))


            elif syntaxError > 0:
                syntaxMessage = "501 Syntax error in parameters or arguments"
                #sys.stdout.write("501 Syntax error in parameters or arguments\n")
                  
                connectionSocket.sendall(syntaxMessage.encode("utf-8"))


            else:      

                #DATA prompt
                if currentCommand == 3:
                    dataMessage = "354 Start mail input; end with . on a line by itself"
                    sys.stdout.write(dataMessage + "\n")

                    connectionSocket.sendall(dataMessage.encode("utf-8"))
                
            

                #HELO prompt
                elif currentCommand == 0:
                    secondGreeting = "250 Hello " + clientIp + " pleased to meet you"
                    sys.stdout.write(secondGreeting + "\n")
                    
                    connectionSocket.sendall(secondGreeting.encode("utf-8"))

                    #reset clientIp
                    clientIp = ""


                #MAIL FROM, RCPT TO prompt
                else:
                    correctMessage = "250 OK"
                    sys.stdout.write(correctMessage + "\n")

                    connectionSocket.sendall(correctMessage.encode("utf-8"))


                #increment command counter
                currentCommand += 1

        try:
            line = connectionSocket.recv(1024).decode()
        except Exception as e:
            sys.stdout.write("cannot receive message from client error\n")
            connectionSocket.close()

            #reset to initial state
            currentCommand = 0
            clientIp = ""


    #quit command
    closing = "221 " + host + " closing connection"
    sys.stdout.write(closing + "\n")
    connectionSocket.sendall(closing.encode("utf-8"))
    connectionSocket.close()
                