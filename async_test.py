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

import asyncore
import asynchat
import socket



class Connection_manager(asyncore.dispatcher):

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
        print self.type.__name__, "listening on port", self.port

    def handle_accept(self):
        conn, addr = self.accept()
        self.connections.append( self.type(conn, addr, self) )
        print str(addr[0]) + ":" + str(addr[1]), "connected to", self.type.__name__,  "-", len(self.connections), " clients connected to", self.type.__name__

    def remove_conn(self, conn):
        self.connections.remove(conn)
        print conn.addr[0], "disconnected from", self.type.__name__ , "-", len(self.connections), " clients remains..."








class Connection_handler(asynchat.async_chat):
    """Abstract class for connection handling.
    Subclass with implementation of the protocol"""
    def __init__(self, sock, addr, manager):
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator("\n")

        self.addr = addr
        self.buffer = ""
        self.manager = manager

    def pushln(self, data):
        self.push(data + self.get_terminator())

    def collect_incoming_data(self, data):
        """This is fired always when recieving data.
        Probably with recv-method"""
        self.buffer = self.buffer + data

    def handle_command(self, data):
        raise NotImplementedError, "must be implemented in subclass"

    def found_terminator(self):
        """Fired when full line is recieved"""
        self.handle_command(self.buffer)
        self.buffer = ""

    def handle_close(self):
            self.close()
            self.manager.remove_conn(self)

    def __del__(self):
        """just testing"""
        print "deleting object", self.addr






class SMTP(Connection_handler):
    def handle_command(self, data):
        self.pushln("uf lol, i wanna be a real smtp serv some day...")





class POP3(Connection_handler):
    def __init__(self, *args):
        Connection_handler.__init__(self, *args)
        self.pop3_cmds = {
        'USER': self.pop3_user,
        'PASS': self.pop3_pass,
        'QUIT': self.pop3_quit
        }

    def pop3_user(self, data):
        return "+OK user %s accepted" % data

    def pop3_pass(self, data):
        return "+OK pass accepted"

    def pop3_quit(self, data):
        return "+OK POP3 server signing off"
        


    def handle_command(self, data):
        data = self.buffer.split(None, 1)
        pop3_cmd = data[0].upper()

        if len(data) == 2:
            data = data[1]
        else:
            data = ""

        try:
            self.pushln( self.pop3_cmds[pop3_cmd](data) )
        except KeyError:
            self.pushln("-ERR unknown command")


        if pop3_cmd == "QUIT":
            self.handle_close()



pop3_server = Connection_manager(POP3, 1337)
smtp_server = Connection_manager(SMTP, 1338)

asyncore.loop()

