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
from connections import *




class IRCserver(Connection_handler):
    """Dummy ircserver class for testing"""
    def handle_command(self, data):
        print "%s:%s says: %s "  % (self.addr[0], self.addr[1], data )


if __name__ == "__main__":
    irc_server = Connection_manager(IRCserver, 6667)
    asyncore.loop()
