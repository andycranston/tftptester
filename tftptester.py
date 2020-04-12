#
# @(!--#) @(#) tftptester.py, version 007, 12-april-2020
#
# a program to test TFTP server implmentations
#

#
# Help from:
# ---------
#
#    http://www.tcpipguide.com/free/t_TrivialFileTransferProtocolTFTP.htm
#

##############################################################################

#
# imports
#

import sys
import os
import argparse
import time
import socket
import select

##############################################################################

#
# globals
#

DEFAULT_BLOCK_SIZE       = 512
DEFAULT_TEST_FILE        = 'tftptester.txt'
COMMENT_CHAR             = '#'
DEFAULT_PORT_NUMBER      = 69
DEFAULT_TIMEOUT          = 5.0
MAX_PACKET_SIZE          = 65536

##############################################################################

def showpacket(bytes, prefix):
    bpr = 10              # bpr is Bytes Per Row
    
    numbytes = len(bytes)

    if numbytes == 0:
        print('{} <empty packet>'.format(prefix))
    else:
        i = 0
        
        while i < numbytes:
            if (i % bpr) == 0:
                print("{} {:04d} :".format(prefix, i), sep='', end='')
                chars = ''
            
            c = bytes[i]
            
            if (c < 32) or (c > 126):
                c = '?'
            else:
                c = chr(c)
            
            chars += c

            print(" {:02X}".format(bytes[i]), sep='', end='')

            if ((i + 1) % bpr) == 0:
                print('    {}'.format(chars))

            i = i + 1

    if (numbytes % bpr) != 0:
        print('{}    {}'.format(' ' * (3 * (bpr - (numbytes % bpr))), chars))

    return

##############################################################################

def buildrequest(opcode, args):
    packetsize = 2
    for arg in args:
        packetsize += len(arg) + 1
    packet = bytearray(packetsize)
    
    packet[0] = (opcode & 0xFF00) >> 8
    packet[1] = (opcode & 0x00FF) >> 0
    
    i = 2
    for arg in args:
        for c in arg:
            packet[i] = ord(c)
            i += 1
        packet[i] = 0
        i += 1
        
    return packet

##############################################################################

def buildrrq(args):
    return buildrequest(1, args)
    
##############################################################################

def buildwrq(args):
    return buildrequest(2, args)
    
##############################################################################

def builddatablock(blocknum, blocksize, datastrings):
    packet = bytearray(2 + 2 + blocksize)
    
    packet[0] = 0
    packet[1] = 3
    packet[2] = (blocknum & 0xFF00) >> 8
    packet[3] = (blocknum & 0x00FF) >> 0
    
    datastring = ''
    for d in datastrings:
        if datastring != '':
            datastring += ' '
        datastring += d
    datastring += '\n'
    
    i = 4
    while i < (4 + blocksize):
        packet[i] = ord(datastring[(i - 4) % len(datastring)])
        i += 1
    
    return packet
    
##############################################################################

def buildack(blocknum):
    packet = bytearray(2 + 2)
    
    packet[0] = 0
    packet[1] = 4
    packet[2] = (blocknum & 0xFF00) >> 8
    packet[3] = (blocknum & 0x00FF) >> 0

    return packet

##############################################################################

def builderror(errorcode, errormsg):
    packet = bytearray(2 + 2 + len(errormsg) + 1)
    
    packet[0] = 0
    packet[1] = 5
    packet[2] = (errorcode & 0xFF00) >> 8
    packet[3] = (errorcode & 0x00FF) >> 0
    
    i = 4
    for c in errormsg:
        packet[i] = ord(c)
        i += 1
    packet[i] = 0
    
    return packet

##############################################################################

def buildraw(args):
    packet = bytearray(len(args))
    
    i = 0
    for arg in args:
        if len(arg) == 1:
            packet[i] = ord(arg)
        elif len(arg) == 2:
            packet[i] = int(arg, base=16)
        else:
            packet[i] = 0
        i += 1
    
    return packet

##############################################################################

def processtestfile(testfile):
    global progname
    
    destport = DEFAULT_PORT_NUMBER
    
    timeout = DEFAULT_TIMEOUT
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    linenum = 0

    for rawline in testfile:
        linenum += 1
        
        line = rawline.strip()
        
        if len(line) == 0:
            continue
        
        if line[0] == COMMENT_CHAR:
            continue
        
        words = line.split()
        
        if len(words) == 0:
            continue
        
        cmd = words[0]
        
        if len(words) == 1:
            argc = 0
            args = []
        else:
            argc = len(words) - 1
            args = words[1:]
        
        if cmd == 'exit':
            break
        elif cmd == 'ip':
            ipaddr = args[0]
        elif cmd == 'port':
            destport = int(args[0])
        elif cmd == 'timeout':
            timeout = float(args[0])
        elif cmd == 'rrq':
            packet = buildrrq(args)
            destport = DEFAULT_PORT_NUMBER
        elif cmd == 'wrq':
            packet = buildwrq(args)
            destport = DEFAULT_PORT_NUMBER
        elif cmd == 'data':
            blocknum = int(args[0])
            blocksize = int(args[1])
            datastrings = args[2:]
            packet = builddatablock(blocknum, blocksize, datastrings)
        elif cmd == 'ack':
            blocknum = int(args[0])
            packet = buildack(blocknum)
        elif cmd == 'error':
            errorcode = int(args[0])
            errormsg = ''
            for arg in args[1:]:
                if errormsg == '':
                    errormsg = arg
                else:
                    errormsg += ' ' + arg
            packet = builderror(errorcode, errormsg)
        elif cmd == 'raw':
            packet = buildraw(args)
        elif cmd == 'show':
            showpacket(packet, '-')
        elif cmd == 'send':
            showpacket(packet, '>')
            sock.sendto(packet, (ipaddr, destport))
        elif cmd == 'receive':
            ready, dummy1, dummy2 = select.select([sock], [], [], timeout)    
            if len(ready) == 0:
                print('{}: timeout on receive packet - waited {} seconds'.format(progname, timeout), file=sys.stderr)
            else:
                inpacket, server = sock.recvfrom(MAX_PACKET_SIZE)
                destport = server[1]
                showpacket(inpacket, '<')            
        elif cmd == 'sleep':
            duration = args[0]
            time.sleep(float(duration))
        else:
            print('{}: unrecognised command "{}" at line {}'.format(progname, cmd, linenum), file=sys.stderr)
    
    return

##############################################################################

def main():
    global progname
    
    parser = argparse.ArgumentParser()
        
    parser.add_argument('--testfile',       help='name of test file (default is "{}")'.format(DEFAULT_TEST_FILE), default=DEFAULT_TEST_FILE)

    args = parser.parse_args()
    
    testfilename = args.testfile
    
    try:
        testfile = open(testfilename, 'r', encoding='utf=8')
    except IOError:
        print('{}: unable to open test file "{}" for reading'.format(progname, testfilename), file=sys.stderr)
        sys.exit(1)
    
    processtestfile(testfile)
    
    testfile.close()
    
    return 0

##############################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
