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

from users import Users


class Connection_manager(asyncore.dispatcher):
    all_conn_count = 0 # Class variable. Contains count of all connections from every instance of this class.
    def __init__(self, type, port):
        asyncore.dispatcher.__init__(self)
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        # This allows to reuse the port which we are listening
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.type = type
        self.connections = []

        self.bind(("", port))
        self.listen(5)
        self.dmesg( self.type.__name__, "listening on port", self.port )


    def __str__(self):
        """equivalent to java's toString()"""
        return "%s clients connected to %s. Overall %s connections" % (len(self.connections), self.type.__name__, Connection_manager.all_conn_count)





    def handle_accept(self):
        conn, addr = self.accept()
        Connection_manager.all_conn_count += 1

        self.connections.append( self.type(conn, addr, self) )

        self.dmesg( str(addr[0]) + ":" + str(addr[1]), "connected to", self.type.__name__ )
        self.dmesg( self )



    def remove_conn(self, conn):
        self.connections.remove(conn)
        Connection_manager.all_conn_count -= 1

        self.dmesg( conn.addr[0], "disconnected from", self.type.__name__ )
        self.dmesg( self )





    def dmesg(self, *msgs):
        msg = "%s> %s" %  (self.__class__.__name__, " ".join(str(v) for v in msgs) )
        # light blue
        print("\033[01;34m" + msg +  "\033[00m" )



class Connection_handler(asynchat.async_chat):
    """Abstract class for connection handling.
    Subclass with implementation of the protocol"""

    users = Users()

    def __init__(self, sock, addr, manager):
        asynchat.async_chat.__init__(self, sock)

        # TODO: Make sure this is really the right one
        # btw, is this exactly same with pop3 and smpt?
        #self.set_terminator("\n") # netcat
        self.set_terminator("\r\n")
        self.users = Connection_handler.users

        self.addr = addr
        self.buffer = ""
        self.manager = manager



    def handle_command(self, data):
        raise NotImplementedError, "must be implemented in subclass"

    def found_terminator(self):
        """Fired when full line is recieved"""

        self.handle_command(self.buffer)
        self.buffer = ""

    def handle_close(self):
        """Fired when client closes connection.
        Can be also called by this class."""
        self.close()
        self.manager.remove_conn(self)

    def __del__(self):
        """just testing"""
        self.dmesg( "deleting object", self.addr )

    def pushln(self, data=""):
        """use this method to send data to client"""
        self.push(data + self.get_terminator())

    def collect_incoming_data(self, data):
        """This is fired always when recieving data."""
        self.buffer += str(data)

    def handle_command(self, data):
        raise NotImplementedError, "must be implemented in subclass"

    def found_terminator(self):
        """Fired when full line is recieved"""
        self.handle_command(self.buffer)
        self.buffer = ""

    def handle_close(self):
        """Fired when client closes connection.
        Can be also called by this class."""
        self.close()
        self.manager.remove_conn(self)

    def __del__(self):
        """just testing"""
        self.dmesg( "deleting object", self.addr )

    def dmesg(self, *msgs):
        """http://hacktux.com/bash/colors"""
        msg = "%s> %s" %  (self.__class__.__name__, " ".join(str(v) for v in msgs) )
        # yellow
        print( "\033[01;33m" + msg +  "\033[00m" )







