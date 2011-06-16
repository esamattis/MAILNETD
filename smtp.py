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
import re
import socket
import base64

from users import Mail2IRC
from users import User

class SMTP(connections.Connection_handler):

    def __init__(self, *args):
        connections.Connection_handler.__init__(self, *args)
        self.dmesg("new smtp user")
        #self.users = connections.Connection_handler.users
        self.dataState = False
        self.mail = Mail2IRC()
        self.mailPattern = re.compile(r"([#a-zA-Z0-9\-_\.]+)@([a-zA-Z0-9\-_\.]+)")

        

        # http://tools.ietf.org/html/rfc0821#page-41
        self.cmds = {
        'EHLO': self.smtp_hello,        
        'HELO': self.smtp_hello,
        'MAIL': self.smtp_mail,
        'RCPT': self.smtp_rcpt,
        'DATA': self.smtp_data,
        'RSET': self.smtp_rset,
        'NOOP': self.smtp_noop,
        'QUIT': self.smtp_quit,
        }

        self.pushln("220 " + str(socket.gethostbyname(self.addr[0])) + " MAILnetD smtp-server")

    def smtp_quit(self, data):
        self.pushln("221 Bye")
        self.handle_close()

    def smtp_mail(self, data):
        """http://tools.ietf.org/html/rfc0821#page-20
        MAIL FROM:<bob@example.org>
        """
        
        self.dmesg("mail ", data)

        match = self.mailPattern.search(data)
        if not match:
            self.push("550 bad from address")
            return

        username = match.group(1)

        try:
            self.mail.user = self.users.getUser( username )
        except KeyError:
            self.dmesg("user " + username + " not found. creating new.")
            user = User(username)
            self.users.users[username] = user
            self.dmesg("There are now %s users" % len(self.users.users) )
            self.mail.user = user

        self.pushln( "250 OK" )

    def smtp_rcpt(self, data):
        """http://tools.ietf.org/html/rfc0821#page-20
        In this gateway
        <channel/nick>@<network>

        if possible at this point, respond 550 if user is not on the channel.
        RCPT TO:<#kanava@verkko>
        """

        match = self.mailPattern.search(data)
        if not match:
            self.pushln("550 bad rcpt address")
            return

        channel, network = match.groups()
        self.mail.rcpts.append ( (channel, network) )
        
        self.pushln("250 OK")




    def smtp_rset(self, data):
        """RFC:
        This command specifies that the current mail transaction is
        to be aborted.  Any stored sender, recipients, and mail data
        must be discarded, and all buffers and state tables cleared.
        The receiver must send an OK reply."""
        #TODO actually reset
        self.pushln("250 Ok")

    def smtp_noop(self, data):
        """RFC:
        This command does not affect any parameters or previously
        entered commands.  It specifies no action other than that
        the receiver send an OK reply.

        This command has no effect on any of the reverse-path
        buffer, the forward-path buffer, or the mail data buffer.
        """
        self.pushln("250 Ok")



            
    def smtp_hello(self, data):
        self.pushln("250 Ok")


    def smtp_data(self, data):
        """http://tools.ietf.org/html/rfc0821#page-21
        RFC: The receiver treats the lines following the command as mail
            data from the sender.  This command causes the mail data
            from this command to be appended to the mail data buffer.
            The mail data may contain any of the 128 ASCII character
            codes.

            The mail data is terminated by a line containing only a
            period, that is the character sequence "<CRLF>.<CRLF>" (see
            Section 4.5.2 on Transparency).  This is the end of mail
            data indication.
        """
        self.pushln('354 Enter mail, end with "." on a line by itself')
        self.dataState = True


    def handleData(self, data):
        if data == ".":
            self.dataState = False
            self.pushln("250 Message accepted for delivery")
            self.mail.sendAll()
            return
        self.mail.addLine(data)



    def handle_command(self, data):
        data = data.strip()

        if self.dataState:
            self.handleData(data)
            return

        cmd = data.split(None, 1)


        if len(cmd) == 2:
            msg = cmd[1]
        else:
            msg = ""
        cmd = cmd[0]


        try:
            self.cmds[cmd.upper()](msg)
        except KeyError:
            self.pushln("500 5.5.1 Command unrecognized: \"%s\"" % cmd)
            self.dmesg("unimplemented: " + data)

