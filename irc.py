#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MAILnetD.py
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

import asyncore
import asynchat
import socket

import re


import traceback


class IRC(asynchat.async_chat):
    def __init__(self, user, servername, serverport=None, serverpassword=None):
        asynchat.async_chat.__init__(self)


        self.channels = {}

        self.user = user

        self.set_terminator("\r\n")
        self.buffer = ""
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)


        self.nick = self.user.username 

        self.servername = servername
        self.serverpassword = serverpassword
        if serverport:
            self.serverport = serverport
        else:
            self.serverport = 6667

    
        self.registeted = False

        self.sendQueue = []
        self.ircPattern = re.compile(r"(?::([_@!~a-zA-Z-\.0-9]*)\s+)?([a-zA-Z0-9]+)(?:\s+([^:]*))(?:\s*:(.*))?")
        self.cmds = {
            '001': self.handleWelcome,
            '433': self.handleBadNick,
            'PING': self.handlePing,
            'PRIVMSG': self.handleMsg,
            'JOIN': self.handleJoin,
            'PART': self.handlePart,

        }
        
        self.userCmds = {
            'PART': self.partChannel,
            'JOIN': self.joinChannel,
            'RAW': self.sendRaw,
            'QUIT': self.quitUser,
        }
        

        self.dmesg( "connecting to irc-server", servername, serverport )
        self.connect( ( self.servername,  self.serverport) )
        
        
    def pushln(self, msg):
        match = self.ircPattern.search(msg)
        self.dmesg("own messge matching: " + msg)
        if match:
            prefix, cmd, params, message = match.groups()
            params = self.none2Empty(params)
            message = self.none2Empty(message)
            if prefix == "":
                prefix = "%s!%s@%s" % (self.nick, self.nick, self.servername)
            try:
                self.cmds[cmd](prefix, cmd, params, message)
                self.dmesg("applying " + cmd + " to own message")
            except KeyError:
                pass
        self.push(msg + self.get_terminator())


    def partChannel(self, msg):
        tmp = msg.split(None, 1)
        channel = tmp[0]
        msg = tmp[1]
        try:
            del self.channels[channel]
        except KeyError:
            self.dmesg("not on that channel: " + channel)
            # TODO: add this to status message
            
          
        
      





    def handlePart(self, prefix, cmd, params, message):
        self.dmesg("join prefix: " + prefix)
        
        nick = prefix.split("!")[0]
        channel = params.strip()
    
        try:
            nick_list = self.channels[channel]
        except KeyError:
            return
        nick_list.remove(nick) 
            


    def quitUser(self, msg):
      # TODO: remove this from irc-connections-list
      self.dmesg("quitting from " + self.servername)
      self.pushln("QUIT :" + msg)
      self.registeted = False
    
    
    def sendRaw(self, raw):
        self.dmesg("sending raw message to server: " + raw)
        if self.registeted:
            self.pushln(raw)
        else:
            self.dmesg("Obs! Can't send yet. Adding to raw-command to queue.")
            self.sendQueue.append(raw)

    def found_terminator(self):

        # p.search(":optional_prefix command param1 param2 :the message").groups()
        # ('optional_prefix', 'command', 'param1 param2 ', 'the message')
        match = self.ircPattern.search(self.buffer)

        if match:
            prefix, cmd, params, message = match.groups()
            params = self.none2Empty(params)
            message = self.none2Empty(message)
            prefix = self.none2Empty(prefix)
            
            try:
                 self.cmds[cmd](prefix, cmd, params, message)

            except KeyError:
                pass
                #self.dmesg( "No handler found for '%s' <> %s" % (match.group(2),  self.buffer)  )
        else:
            self.dmesg( "No match for: " + self.buffer )

        self.buffer = ""

    def none2Empty(self, x):
        if x is None:
            return ""
        return x
    
    def handleJoin(self, prefix, cmd, params, message):
        self.dmesg("join prefix: " + str(prefix))
        self.dmesg("join params: " + params)      
        
        if prefix is not None:
            nick = prefix.split("!")[0]
        else:
            nick = self.nick
        
        params = params.strip() 
        message = message.strip()
        if params == "" and message[0] == '#':
            channel = message
        else:
            channel = params
        
        
        
        self.dmesg( nick, "joined channel", channel)
        self.saveMsg(channel, "-!- %s has joined %s" % (nick, channel) )


        try:
            nick_list = self.channels[channel]
        except KeyError:
            self.channels[channel] = []
            nick_list = self.channels[channel]
        self.dmesg("adding " + nick + " to channel's " + channel + 
            "nick listing") 
        nick_list.append(nick)








    def handleMsg(self, prefix, cmd, params, message):
        if prefix is not None:
            nick = prefix.split("!")[0]
        else:
            nick = self.nick
        self.dmesg( nick + "'s message from " + params.strip() + ": " 
            + message )

        self.saveMsg(params.strip(), "<%s> %s" % (nick, message))
        



    def saveMsg(self, sender, message):
        """sender without the server"""
        if sender.strip() == "":
            self.dmesg("HUGE ERROR! Tried to save message without rcpt!")
            traceback.print_stack()
            return

        self.user.messages.addMsg(sender + "@" + self.servername, message)


    def handleBadNick(self, prefix, cmd, params, message):
        self.nick += "-mail"
        self.dmesg( "trying new nick:", self.nick )
        self.pushln("NICK " + self.nick)



    def handlePing(self, prefix, cmd, params, message):
        reply = "PONG " + params + message
        self.dmesg("replying to ping", reply)
        self.pushln(reply)

    def handleWelcome(self, prefix, cmd, params, message):
        self.registeted = True
        self.dmesg( "Registered!" )


        nick = params.split()[0]
        if nick != self.nick:
            self.nick = nick
            # TODO: Is this true?!
            self.dmesg("server gave an another nick: " + self.nick)

        if len(self.sendQueue) != 0:
            for message in self.sendQueue:
                self.dmesg("sending from queue: " + message)
                
                self.pushln(message)
            self.sendQueue = []
        
        


    def joinChannel(self, channel):
        cmd = "JOIN " + channel
        self.channels[channel] = []
        if self.registeted:
            self.dmesg("joining " + channel)
            self.pushln( cmd )
        else:
            self.dmesg("Can't join yet. Adding to queue: " + cmd)
            self.sendQueue.append(cmd)






    def sendMsg(self, target, msg):
        cmd = "PRIVMSG %s :%s" % (target, msg)
        target = target.strip()
        if "#" == target[0] and not self.onChannel(target):
            self.joinChannel(target)
        if self.connected:
            self.dmesg("sending: " + cmd)
            self.pushln(cmd)
        else:
            self.dmesg("adding to queue: " + cmd)
            self.sendQueue.append( cmd )


    def onChannel(self, channel):
        try:
          channel = self.channels[channel]
          return True
        except KeyError:
          return False
        
    def collect_incoming_data(self, data):
        self.buffer += str(data)
    
    def registerConn(self):
        self.dmesg("registering connection")
        if self.serverpassword:
            self.pushln("PASS " + self.serverpassword)
        self.pushln("NICK %s \n" % self.nick )
        self.pushln("USER MAILnetD 0 * :MAILnetD user")



    def handle_connect(self):
        self.registerConn()

    def dmesg(self, *msgs):
        """http://hacktux.com/bash/colors"""
        msg = "%s(%s@%s)> %s" %  (self.__class__.__name__, self.nick, self.servername, " ".join(str(v) for v in msgs) )
        # green
        print("\033[00;32m" + msg +  "\033[00m" )


if __name__ == "__main__":
    

    IRC("Epeli", "irc.jyu.fi", 6667 )
    asyncore.loop()









    
