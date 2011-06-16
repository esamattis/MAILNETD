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

import connections
from users import User
from users import Users
from messages import Message

class POP3(connections.Connection_handler):
    def __init__(self, *args):
        connections.Connection_handler.__init__(self, *args)

        self.dmesg("new pop3 user")
        self.users = connections.Connection_handler.users
        self.user = None
	
        # Function map(=dictionary)
        self.pop3_cmds = {  
        'USER': self.pop3_user,
        'USERS': self.pop3_users,
        'PASS': self.pop3_pass,
        'NOOP': self.pop3_noop,
        'STAT': self.pop3_stat,
        'LIST': self.pop3_list,
        'RETR': self.pop3_retr,
        'DELE': self.pop3_dele,
        'TOP': self.pop3_top,
        'QUIT': self.pop3_quit
        }
        self.pushln("+OK POP3 ready")
        

    def pop3_user(self, data):
	try:
            self.user = self.users.getUser(data)
            self.pushln("+OK user %s accepted" % data)
        except KeyError:
            self.pushln("-ERR user %s not accepted" % data)
            
    def pop3_users(self, data):
        self.dmesg("printing users")
        self.pushln( "%s irc users" % len(self.users)  )

    def pop3_pass(self, data):
        self.pushln("+OK pass accepted")

    def pop3_quit(self, data):
        self.pushln("+OK POP3 server signing off")
        self.handle_close()

    def pop3_noop(self, data):
        self.pushln("+OK")
        
    def pop3_stat(self, data):
        """
      The POP3 server issues a positive response with a line
      containing information for the maildrop.  This line is
      called a "drop listing" for that maildrop.
      Examples:
      C: STAT
      S: +OK 2 320
      """

        msgcount, msglen = self.countmessages()
        self.pushln("+OK " + str(msgcount) + " " + str(msglen))
        

    def pop3_list(self, data):
        msgcount, msglen = self.countmessages()
        self.pushln("+OK " + str(msgcount) + " messages (" + str(msglen) + " octets)")
        for k, v in self.user.messages.messages.items():
            self.pushln(str(v.id) + " " + str(len(v.getIMF())))
        
        self.pushln(".")
    
    def countmessages(self):
        msgcount = len(self.user.messages.messages)
        msglen = 0
        for k, v in self.user.messages.messages.items():
            msglen = msglen + len(v.getIMF())
            
        return msgcount, msglen
    
    def pop3_top(self, data):
        msgnumber, msglines = data.split()
        self.dmesg("pop3_top " + msgnumber + " " + msglines + " data " + data)
        self.pushln("+OK")
        for i in self.user.messages.getMsgByNum(int(msgnumber)).getIMFLines(int(msglines)):
            self.pushln(i)
            
        self.pushln(".")
    
    def pop3_retr(self, data):
        try: 
            self.dmesg("RETR: " + data)
            message = self.user.messages.getMsgByNum(int(data.strip()))
            self.pushln("+OK message follows")
            #for i in message.getIMF():
            #    self.pushln(i)
            self.pushln(message.getIMF())
                
            self.pushln(".")
        except ValueError:
            self.dmesg("RETR: Message " + data.strip() + " not found.")
            self.pushln("-ERR no such message " + data.strip())
        pass
    
    def pop3_dele(self, data):
        try:
            self.user.messages.delMsgByNum(int(data.strip()))
            self.pushln("+OK message " + data.strip() + " deleted")
            self.dmesg("DELE: Message " + data.strip() + " deleted.")
        except ValueError:
            self.dmesg("DELE: Message " + data.strip() + " not found.")
            self.pushln("-ERR no such message " + data.strip())
        pass
        
    def handle_command(self, data):
        line = data
        data = data.split(None, 1)
        pop3_cmd = data[0].upper()

        if len(data) == 2:
            data = data[1]
        else:
            data = ""

        try:
            self.pop3_cmds[pop3_cmd](data) 
        except KeyError:
            self.pushln("-ERR unknown command")
            self.dmesg("unimplemented: " + line)

if __name__ == "__main__":
    print "Hello, this is POP3 class";
