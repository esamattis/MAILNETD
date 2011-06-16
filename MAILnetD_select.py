#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__="epeli"
__date__ ="$Feb 8, 2009 7:56:59 PM$"
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

import socket
import select
import signal
import sys

# List of socket objects that are currently open
open_sockets = []

# AF_INET means IPv4.
# SOCK_STREAM means a TCP connection.
# SOCK_DGRAM would mean an UDP "connection".
listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



# The parameter is (host, port).
# The host, when empty or when 0.0.0.0, means to accept connections for
# all IP addresses of current machine. Otherwise, the socket will bind
# itself only to one IP.
# The port must greater than 1023 if you plan running this script as a
# normal user. Ports below 1024 require root privileges.
listening_socket.bind( ("", 1234) )

# The parameter defines how many new connections can wait in queue.
# Note that this is NOT the number of open connections (which has no limit).
# Read listen(2) man page for more information.
listening_socket.listen(5)



mail = """
From: "MAILnetD" <#mail@MAILnet.irc>
Reply-to: #mail@MAILnet.irc
To: linkki-fuksi@lists.jyu.fi
Subject: N messages from #mail@MAILnet
Date: Fri, 15 Sep 2006 13:15:37 +0300 (EEST

15:45 <Maakuth> eikun nyt mennään backronyymilinjalla että kuulostaa mahdollisimman tyhmältä
15:45 <Maakuth> siitä pitää vääntää mailnet vaikka väkisin
15:45 <Epeli> haha
15:45 <Maakuth> irc on kai pakko laittaa tohon i:hin
15:46 <Maakuth> meaningless automatic irc lameness network email transport
15:46 <Maakuth> no tossa on jo harvinaisen vähän järkeä
15:47 <Epeli> joo, yhtä paljon kuin sen ideassa :D
15:47 <Maakuth> joo
15:47 <Maakuth> automaticin ja lamenessin tilalle vois keksiä jotain
15:47 <Maakuth> asynchronous!
15:48 <Epeli> joo, se on muotisana"
15:48 <Epeli> !
15:48 <Maakuth> mitähän ällällä alkavaa..
15:48 <Maakuth> tai irc-emaiL
15:49 <Maakuth> Meaningless Asynchronous Irc-emaiL Network E* Transport
15:50 <Epeli> E* ?
15:50 <Maakuth> niin mietin että mitä siihen pistäis
15:50 <Maakuth> kun ei kahdesti emailia viitsis
15:50 <Epeli> hmm, kyllä se oli ehkä parempi omana sananaan
15:51 <Epeli> siis tossa e:n kohdalla
15:51 <Maakuth> no ehkä
15:55 <Epeli> meta automatic irc linked network email transport daemon
15:55 <Maakuth> meta :D
15:55 <Maakuth> toi on kyllä hyvä, pistä isoilla alkukirjaimilla se tonne speksisivulle
15:56 <Maakuth> eikun ehän oli emailnet näemmä
15:56 <Maakuth> *sehän
15:56 <Maakuth> no, oli miten oli
15:57 <Maakuth> vai asynchronous
15:57 <Epeli> eiku niin se unohtu
15:59 <Epeli> Meta Asynchronous Irc Linked Network Email Transport Daemon - EmailNetD
15:59 <Maakuth> vai mailnetd
15:59 <Epeli> joo
16:00 <Maakuth> näin saatiin aikaa kulumaan \o/
.
    """









def handleUser(data, msg):
    return "+OK user accepted"

def handlePass(data, msg):
    return "+OK pass accepted"

def handleStat(data, msg):
    return "+OK 1 5822"

def handleList(data, msg):
    return "+OK scan listing follows\r\n1 %i\r\n." % len(mail)

def handleTop(data, msg):
    return "+OK top of message follows"  + mail

def handleRetr(data, msg):
    return "+OK Message follows" + mail

def handleDele(data, msg):
    return "+OK message 1 deleted"

def handleNoop(data, msg):
    return "+OK"

def handleQuit(data, msg):
    return "+OK POP3 server signing off"

dispatch = dict(
    USER=handleUser,
    PASS=handlePass,
    STAT=handleStat,
    LIST=handleList,
    RETR=handleRetr,
    DELE=handleDele,
    NOOP=handleNoop,
    TOP=handleTop,
    QUIT=handleQuit,
)





def quit(signum, frame):
    print "nice quit"
    for s in [listening_socket] + open_sockets:
        s.close()
    sys.exit(0)



signal.signal(signal.SIGINT, quit)
signal.signal(signal.SIGTERM, quit)


while True:
    # Waits for I/O being available for reading from any socket object.
    rlist, wlist, xlist = select.select( [listening_socket] + open_sockets, [], [] )
    #print [listening_socket] + open_sockets
    for s in rlist:
        if s is listening_socket:
            new_socket, addr = listening_socket.accept()
            open_sockets.append(new_socket)
            new_socket.send("+OK MAILNETD POP3 server ready\n")
            print "S: +OK MAILnetD POP3 server ready"
        else:
            data = s.recv(1024)
            if data == "":
                s.close()
                open_sockets.remove(s)
                print "Connection closed"
            else:
                #print open_sockets.index(s), ": " , repr(data)
                #print len(data)

                print "C: ", data

                msg = data.split(None, 1)
                pop3_cmd = msg[0]
                if len(msg) == 2:
                    arg_cmd = msg[1]
                else:
                    arg_cmd = ""
                
                try:
                    send_me  = dispatch[pop3_cmd](data, arg_cmd)
                    s.send(send_me + "\n")
                    print "S: ", send_me
                except KeyError:
                    s.send("-ERR unknown command\n")
                    print "S: -ERR unknown command"



