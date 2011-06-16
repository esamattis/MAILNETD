#!/usr/bin/env python
# -*- coding: utf-8 -*-
# unittests.py
# http://wiki.python.org/moin/PyUnit
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

_author__="epeli"
__date__ ="$Feb 21, 2009 1:57:16 AM$"


import socket
import unittest
import os, sys
import time


from connections import Connection_manager
from pop3 import POP3
from smtp import SMTP



class Pop3tests(unittest.TestCase):




    def setUp(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 2337))
        self.client.recv(1024) # recv hello crap away

    def tearDown(self):
        self.client.close()


    def testUser(self):
    
        self.client.send("USER esa\n")
        reply = self.client.recv(1024)
        assert "+OK user esa accepted\n" == reply, "User reply is wrong!"


    def testNoop(self):
        self.client.send("NOOP\n")
        reply = self.client.recv(1024)
        assert "+OK\n" == reply, "NOOP FAIL!"







if __name__ == "__main__":
    os.popen("xterm -e python MAILnetD.py test &")
    time.sleep(1)

    unittest.main()







    