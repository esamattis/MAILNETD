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
import sys

from connections import Connection_manager
from pop3 import POP3
from smtp import SMTP

if __name__ == "__main__":


    try:
        smtp_port = int(sys.argv[1])
        pop_port = int(sys.argv[2])
    except:
        pop_port = 1337
        smtp_port = 1338





    if len(sys.argv) > 1 and sys.argv[1] == "test":
        pop3_server = Connection_manager(POP3, 2337)
        smtp_server = Connection_manager(SMTP, 2338)
    else:
        pop3_server = Connection_manager(POP3, pop_port)
        smtp_server = Connection_manager(SMTP, smtp_port)

    asyncore.loop()

