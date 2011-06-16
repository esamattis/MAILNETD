#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This file is part of MAILNETd.

#MAILNETd is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#MAILNETd is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with MAILNETd.  If not, see <http://www.gnu.org/licenses/>.

import re
import base64 
import quopri
import time 

class Mail2IRC:
    """
    Internet Message Format to IRC converter
    """
    def __init__(self):
        self.headerState = True
        self.user = None
        self.rcpts = [] # [ ( channel, network), ( channel, another_network) ]
        #self.message = ""
        self.encoding = ""
        self.decodedmessage = ""
        self.commands = []

    def addLine(self, line):
        line = line.strip()
        if line == "":
            self.headerState = False
            
        if self.headerState:
            encpattern = re.compile(r"Content-Transfer-Encoding: (.+)")
            enctmp = encpattern.search(line)
            if enctmp:
                self.encoding = enctmp.group(1).strip()
            

        if not self.headerState:
            if self.encoding == "base64":
                self.decodedmessage += base64.b64decode(line)
            if self.encoding == "quoted-printable": 
                self.decodedmessage += quopri.decodestring(line) + "\n"
            else:
                self.decodedmessage += line + "\n"

    def parseMessage(self, decodedmessage):
        message = ""
        for line in decodedmessage.split("\n"):
            if line.strip() == "": continue
            if line[0].strip() == '>':
                continue
            if line[0].strip() == '/':
                tmp = line.split(None, 1)
                cmd = tmp[0][1:].upper()
                params = tmp[1]
                self.commands.append( (cmd, params) )
                continue
            
            message += line + " "
        
        return message
        
    
    def sendAll(self):
        message = self.parseMessage(self.decodedmessage)
        
        if self.user is None:
            self.dmesg("Sending failed. User was not selected!")
            return False
        for channel, network in self.rcpts:
            irc = self.user.getIrcConn(network)
            for line in message.split("\n"):
                irc.sendMsg(channel, line.strip())
            
            for cmd, params in self.commands:
                try:
                    irc.userCmds[cmd](params)
                except KeyError:
                    self.dmesg("Unknown key " + cmd)

        return True


    def dmesg(self, *msgs):
        """http://hacktux.com/bash/colors"""
        msg = "%s> %s" %  (self.__class__.__name__, " ".join(str(v) for v in msgs) )
        # purple
        print( "\033[01;35m" + msg +  "\033[00m" )









class Message:
    def __init__(self, id, origin,  message):
        self.id = id
        self.origin = origin 
        self.term = "\r\n"
        
        self.header = "From: <%s>" %  self.origin + self.term
        self.header = self.header + "User-Agent: MAILNETd 0.01" + self.term
        self.header = self.header + "Content-Type: text/plain; charset=UTF-8; format=flowed" + self.term
        self.header = self.header + "Content-Transfer-Encoding: quoted-printable" + self.term
        self.header = self.header + "MIME-Version: 1.0" + self.term
        self.header = self.header + "To: you@mailnet:" + self.term
        self.header += "Subject: Messages from  %s" %  self.origin
        self.body = ""
        self.addLine(message)



    def addLine(self, line):
        self.body += time.strftime("%a, %d %b %Y %H:%M:%S ", time.gmtime()) + str(line + self.term)

    def getIMF(self):
        newbody = quopri.encodestring(self.body)
        
        return self.header.strip() + self.term + self.term + newbody

    def getIMFLines(self, count):
        return self.body.split(self.term)[:int(count)]



class Messages:
    def __init__(self):
        self.messages = { "status@MAILnetD": Message(1, "status@MAILnetD",
        "Welcome to MAILNET (Meta Asynchronous Irc Linked Network Email Transport)!\r\n") }
        self.nextId = 2
        
    

        
    def addMsg(self, origin, line):
        try:
            msg = self.messages[origin]
            msg.addLine(line)
        except KeyError:
            msg = Message(self.nextId, origin, line)
            self.messages[origin]  = msg
        self.nextId += 1



    def getMsgByNum(self, id):
        id = int(id)
        for origin, msg in self.messages.items():
            if msg.id == id:
                self.dmesg("returning %s's message: %s" % (msg.origin, msg.body))
                return msg
        return None

    def delMsgByNum(self, id):
        for origin, msg in self.messages.items():
            if msg.id == id: 
                del self.messages[origin]
                return True
        return False

    def dmesg(self, *msgs):
        """http://hacktux.com/bash/colors"""
        msg = "%s> %s" %  (self.__class__.__name__, " ".join(str(v) for v in msgs) )
        print( "\033[01;31m" + msg +  "\033[00m" )




if __name__ == "__main__":
    msgs = Messages()

    msgs.addMsg("#testeri@murrikka", "viesti")
    msgs.addMsg("#testeri@murrikka", "toinen viesti")


    msg = msgs.getMsgByNum(2)

    

    print msg.body







