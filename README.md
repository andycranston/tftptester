# tftptester

A program to test TFTP server implementations.

It is essentially a low-level TFTP client driven by a plain text file.  The file contains
commands which build TFTP packets, sends them to the TFTP server under text and displays
the response from the TFTP server.

It can be used, for example, to simulate packet loss and observe how the TFTP server under test responds
to this condition.

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

Lines in the test file can be one of:

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

Build a Read ReQuest (RRQ) packet (but do not send it).  Requires a minumim of two arguments.  The first
is the name of the file to be read.  The second is either `netascii` to request an ASCII file transfer or `octet` to request
a binary file transfer.

Additional arguments can be specified which are options.  The TFTP protocol supports the following options:

+ blksize
+ tsize
+ interval

The `blksize` option specifies a different block size from the default of 512 bytes.

The `tsize` option specifies the size of the transfer.

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

Build a data packet (but do not send it).


