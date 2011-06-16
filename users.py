#!/usr/bin/env python
# -*- coding: utf-8 -*-
# users.py
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



from irc import IRC

from messages import Mail2IRC
from messages import Messages


class User:

    def __init__(self, username):
        
        self.username = username
        self.ircConns = {}
        self.messages = Messages()


    def getIrcConn(self, ircServer, ircPort=6667):
        ircServer = ircServer.strip().lower()
        try:
            irc = self.ircConns[ircServer]
        except KeyError:
            irc = IRC(self, ircServer, ircPort )
            self.ircConns[ircServer] = irc
            self.dmesg("My irc connections: " + str(self.ircConns))



        return irc

    def dmesg(self, *msgs):
        """http://hacktux.com/bash/colors"""
        msg = "%s(%s)> %s" %  (self.__class__.__name__, self.username, " ".join(str(v) for v in msgs) )
        # Light Red
        print( "\033[01;31m" + msg +  "\033[00m" )


class Users:
    def __init__(self):
        self.users = {  }


    def getUser(self, username):
        username = username.strip()
	user = None
        user = self.users[username]
            
        return user

    def dmesg(self, *msgs):
        """http://hacktux.com/bash/colors"""
        msg = "%s> %s" %  (self.__class__.__name__, " ".join(str(v) for v in msgs) )
        # Cyan
        print( "\033[01;36m" + msg +  "\033[00m" )





