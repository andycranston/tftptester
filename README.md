# tftptester

A program to test TFTP server implementations.

It is essentially a low-level TFTP client driven by a plain text file.  The file contains
commands which build TFTP packets, sends them to the TFTP server under test and displays
the response from the TFTP server.

It can be used, for example, to observe how a TFTP server responds to packet loss.

## Pre-requisites

You will need the following:

+ Python 3
+ The TFTP TCP/IP port 69 open for inbound and outbound TFTP packets

## Default test file `tftptester.txt`

When the `tftptester.py` is run it will, by default, look for a file called:

```
tftptester.txt
```

and read the commands from that file.

You can specify a different test file by using the `--testfile` command line argument.  For example:

```
python tftptester.py --testfile test2.txt
```

will read commands from the file `test2.txt`.

## Format of the test file

Lines in a test file can be one of:

+ Blank lines
+ Lines beginning with a # character
+ Commands with zero, one of more argumemnts

Lines beginning with a # character are treated as comments and ignored.  Blank lines are also ignored.

Command lines are described below.

### exit

Causes the program to stop - even if there are more commands after the `exit` command.

### ip

Sets the IP address (or hostname) of the TFTP server under test.  For example:

```
ip 10.1.1.100
```

will cause TFTP packets to be sent to IP address `10.1.1.100`.

### port

Sets the TCP/IP port number.  This defaults to 69.  To change it:

```
port 8069
```

would set the port number to `8069`.

### timeout

Sets maximum the number of seconds (as a floating point number) that the program will wait
for a response from the TFTP server.  It defaults to 5.0 (five) seconds.  To change it:

```
timeout 2.5
```

will set the timeout to two and a half seconds.

### rrq

Build a Read ReQuest (RRQ) packet (but do not send it).  Requires a minimum of two arguments.  The first
is the name of the file to be read.  The second is either `netascii` to request an ASCII file transfer or `octet` to request
a binary file transfer.

Additional arguments can be specified which are options.  The TFTP protocol supports the following options:

+ blksize
+ tsize
+ interval

The `blksize` option specifies a different block size from the default of 512 bytes.

The `tsize` option requests the size of the transfer.

The `interval` option specifies how long to wait for a response.

Here is a simple rrq command:

```
rrq file octet
```

This builds a read request asking for a file called `file` and for the transfer to be in binary.

A more complex example:

```
rrq bigfile netascii blksize 2048 tsize 0 interval 20
```

This builds a read request asking for a file called `bigfile` and for the transfer to be
in ASCII.  Additionally block size of 2048 bytes is being request, the size of the
file is also being requested and an interval of 20 seconds.

### wrq

Build a Write ReQuest (WRQ) packet (but do not send it).  The arguments are the same as for the `rrq` command.

### data

Build a data packet (but do not send it).  This requires three arguments.  The first is the block number.  This is a number between 1 and 65535.
The second is the number of bytes of data in this block.  This is a number between 0 and the block size.  Block size is 512 bytes or the number specified
as the `blksize` option on the Write ReQuest (WRA) packet.  The third argument is a string used to generate the data.  This string is simply repeated as many times as necessary
to fill the data portion of the packet.

For example:

```
data 1 512 andy
```

will build a data packet for block number 1 with 512 bytes of data.  The 512 bytes of data will be the string 'andy'
repeated 128 times as follows:

```
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
andyandyandyandyandyandyandyandyandyandyandyandyandyandyandyandy
```

Another example:

```
data 2 10 mary
```

will build a data packet for block number 2 with 10 bytes of data.  The 10 bytes of data will be the string 'mary'
repeated "two and a half times" as follows:

```
marymaryma
```

### ack

Build an ACKnowledge packet (but do not send it).  Requires one argument which is the block number to
acknowledge.  This can be between 0 and 65535 inclusive.

### error

Build an error packet (but do not send it).  Requires a minimum of two arguments.  The first is the error code which can
be between 0 and 8 inclusive.  The second and other arguments make up the error string.  For example:

```
error 0 This is an error
```

### raw

Build a packet of specific bytes.  Requires a minimum of one argument.  Each argument is converted to a byte value
to build up the raw packet.  If an argument is a single character the ASCII value of the character is used.  If the argument
is two characters long it is assumed to be a hexdecimal byte value.  Anything else results in a zero byte value.

For example:

```
raw a 01 A 2 foo
```

produces a raw packet with these byte values (in hex):

```
61 01 41 32 00
```

As the hex ASCII value for 'a' is 61, 01 is 01, the hex ASCII value for 'A' is 61, the hex ASCII value for '2' is 32
and foo falls into the "anything else" category and results in 00.

The `raw` command can be used to build packets from scratch or build invalid packets just to see how
the TFTP server reacts (if it reacts at all).

### show

Show the packet that has been built.

### send

Send the packet that has been built to the TFTP server.

### receive

Receive a packet from the TFTP server.  Wait at most either the default timeout period or the timeout period specified
by the last `timeout` command.

### sleep

Takes single floating point argument and waits that amount of seconds.  For example:

```
sleep 2.0
```

waits for two seconds before processing the next command.

## Example test file

Here is an example test file to use as a template.  It writes a file called `testfile` of 700 bytes of data using binary
transfer mode to a TFTP server running at IP address 10.1.1.8 on the standard well known TCP/IP port number 69:

```
#
# example test file for the tftptester.py Python program
#
# write a file called `testfile` with 700 bytes of data using
# binary transfer mode to a TFTP server at IP address 10.1.18

ip 10.1.1.8

wrq testfile octet
show
send
receive

data 1 512 andy
show
send
receive

data 2 188 cranston
show
send
receive

exit
```

This file is included in the repository and called `example.txt`.  Run as follows:

```
python tftptester.py --testfile example.txt
```

You will almost certainly need to edit the file first and change the line:

```
ip 10.1.1.8
```

to specify an IP address (or hostname) of a TFTP server on your network.

## Simulating packet loss

Conside this series of commands:

```
data 1 512 lisa
show
send
receive

data 3 512 mike
show
send
receive
```

Here data packet for block number 2 is missing.  What do you think a TFTP server should do in this situation?  Why not modify
the example test file and find out.

## Simulating duplicate packets

Simulating a duplicate packet is as easy as you think:

```
data 1 512 jane
show
send
receive

data 1 512 jane
show
send
receive
```

## Simulating out of sequence packets

As TFTP runs over UDP (User Datagram Protocol) packets might not arrive in the order in which they were sent.
You can simulate this:

```
data 2 512 bill
show
send
receive

data 1 512 ruby
show
send
receive
```

## Error handling (or lack of)

The program breaks if you do not specify enough arguments to each command in the test file.  Erro checking can be
added but I wanted to keep the program structure clean.

## References

[The TCP/IP Guide - Trivial File Transfer Protocol](http://www.tcpipguide.com/free/t_TrivialFileTransferProtocolTFTP.htm)

-------------------------

End of README.md

