from __future__ import absolute_import
from __future__ import print_function

import logging
import multiprocessing
import os
import random
import socket
import sys
import threading
import time
import traceback

try:
    import reprlib
except ImportError:
    import repr as reprlib

if __name__ == "__main__" and __package__ is None:
    # Allow relative imports when executing within package directory, for
    # running tests directly
    sys.path.insert( 0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cpppo
from   cpppo.server import ( enip, network )

logging.basicConfig( **cpppo.log_cfg )
log				= logging.getLogger( "enip.tst" )

def test_octets():
    """Scans raw octets"""
    data			= cpppo.dotdict()
    source			= cpppo.chainable( b'abc123' )
    name			= "five"
    with enip.octets( name, repeat=5, context=name ) as machine:
        for i,(m,s) in enumerate( machine.run( source=source, path='octets', data=data )):
            log.info( "%s #%3d -> %10.10s; next byte %3d: %-10.10r: %r", m.name_centered(),
                      i, s, source.sent, source.peek(), data )
        assert i == 4
    assert source.peek() == b'3'[0]

    assert data.octets.five.input.tostring() == b'abc12'


def test_octets_struct():
    """Parses a specified struct format from scanned octets"""

    data			= cpppo.dotdict()
    source			= cpppo.chainable( b'abc123' )
    name			= 'ushort'
    format			= '<H'
    with enip.octets_struct( name, format=format, context=name ) as machine:
        for i,(m,s) in enumerate( machine.run( source=source, path='octets_struct', data=data )):
            log.info( "%s #%3d -> %10.10s; next byte %3d: %-10.10r: %r", m.name_centered(),
                      i, s, source.sent, source.peek(), data )
        assert i == 1
    assert source.peek() == b'c'[0]

    assert data.octets_struct.ushort == 25185

# pkt4
# "4","0.000863000","192.168.222.128","10.220.104.180","ENIP","82","Register Session (Req)"
rss_004_request 		= bytes(bytearray([
    # Register Session
                                        0x65, 0x00, #/* 9.....e. */
    0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, #/* ........ */
    0x00, 0x00                                      #/* .. */
]))
# pkt6
# "6","0.152924000","10.220.104.180","192.168.222.128","ENIP","82","Register Session (Rsp)"
rss_004_reply 		= bytes(bytearray([
                                        0x65, 0x00, #/* ......e. */
    0x04, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, #/* ........ */
    0x00, 0x00                                      #/* .. */
]))
# pkt8
# "8","0.153249000","192.168.222.128","10.220.104.180","CIP","100","Get Attribute All"
gaa_008_request 		= bytes(bytearray([
                                        0x6f, 0x00, #/* 9.w...o. */
    0x16, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x06, 0x00, 0x01, 0x02, #/* ........ */
    0x20, 0x66, 0x24, 0x01                          #/*  f$. */
]))
# pkt10
# "10","0.247332000","10.220.104.180","192.168.222.128","CIP","116","Success"
gaa_008_reply 		= bytes(bytearray([
                                        0x6f, 0x00, #/* ..T...o. */
    0x26, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* &....... */
    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x16, 0x00, 0x81, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x2d, 0x00, 0x01, 0x00, 0x01, 0x01, 0xb1, 0x2a, #/* -......* */
    0x1b, 0x00, 0x0a, 0x00                          #/* .... */
]))
# pkt11
# "11","0.247477000","192.168.222.128","10.220.104.180","CIP CM","114","Unconnected Send: Get Attribute All"
gaa_011_request	 		= bytes(bytearray([
                                        0x6f, 0x00, #/* 9.....o. */
    0x24, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* $....... */
    0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x14, 0x00, 0x52, 0x02, #/* ......R. */
    0x20, 0x06, 0x24, 0x01, 0x01, 0xfa, 0x06, 0x00, #/*  .$..... */
    0x01, 0x02, 0x20, 0x01, 0x24, 0x01, 0x01, 0x00, #/* .. .$... */
    0x01, 0x00                                      #/* .. */
]))
# pkt13
# "13","0.336669000","10.220.104.180","192.168.222.128","CIP","133","Success"
gaa_011_reply	 		= bytes(bytearray([
                                        0x6f, 0x00, #/* ..dD..o. */
    0x37, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* 7....... */
    0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x27, 0x00, 0x81, 0x00, #/* ....'... */
    0x00, 0x00, 0x01, 0x00, 0x0e, 0x00, 0x36, 0x00, #/* ......6. */
    0x14, 0x0b, 0x60, 0x31, 0x1a, 0x06, 0x6c, 0x00, #/* ..`1..l. */
    0x14, 0x31, 0x37, 0x35, 0x36, 0x2d, 0x4c, 0x36, #/* .1756-L6 */
    0x31, 0x2f, 0x42, 0x20, 0x4c, 0x4f, 0x47, 0x49, #/* 1/B LOGI */
    0x58, 0x35, 0x35, 0x36, 0x31                    #/* X5561 */
    ]))
# pkt14
# "14","0.337357000","192.168.222.128","10.220.104.180","CIP CM","124","Unconnected Send: Unknown Service (0x52)"
unk_014_request 		= bytes(bytearray([
                                        0x6f, 0x00, #/* 9.#...o. */
    0x2e, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x1e, 0x00, 0x52, 0x02, #/* ......R. */
    0x20, 0x06, 0x24, 0x01, 0x05, 0x9d, 0x10, 0x00, #/*  .$..... */
    0x52, 0x04, 0x91, 0x05, 0x53, 0x43, 0x41, 0x44, #/* R...SCAD */
    0x41, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, #/* A....... */
    0x01, 0x00, 0x01, 0x00                          #/* .... */  
]))
# pkt16
# "16","0.423402000","10.220.104.180","192.168.222.128","CIP","102","Success"
unk_014_reply 		= bytes(bytearray([
                                        0x6f, 0x00, #/* ..7...o. */
    0x18, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x08, 0x00, 0xd2, 0x00, #/* ........ */
    0x00, 0x00, 0xc3, 0x00, 0x27, 0x80              #/* ....'. */
]))
# pkt17
# "17","0.423597000","192.168.222.128","10.220.104.180","CIP CM","124","Unconnected Send: Unknown Service (0x52)"
unk_017_request 		= bytes(bytearray([
                                        0x6f, 0x00, #/* 9.....o. */
    0x2e, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x1e, 0x00, 0x52, 0x02, #/* ......R. */
    0x20, 0x06, 0x24, 0x01, 0x05, 0x9d, 0x10, 0x00, #/*  .$..... */
    0x52, 0x04, 0x91, 0x05, 0x53, 0x43, 0x41, 0x44, #/* R...SCAD */
    0x41, 0x00, 0x14, 0x00, 0x02, 0x00, 0x00, 0x00, #/* A....... */
    0x01, 0x00, 0x01, 0x00                          #/* .... */
]))
# pkt19
#"19","0.515458000","10.220.104.180","192.168.222.128","CIP","138","Success"
unk_017_reply		= bytes(bytearray([
                                        0x6f, 0x00, #/* ..jz..o. */
    0x3c, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* <....... */
    0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x2c, 0x00, 0xd2, 0x00, #/* ....,... */
    0x00, 0x00, 0xc3, 0x00, 0x4c, 0x10, 0x08, 0x00, #/* ....L... */
    0x03, 0x00, 0x02, 0x00, 0x02, 0x00, 0x02, 0x00, #/* ........ */
    0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe6, 0x42, #/* .......B */
    0x07, 0x00, 0xc8, 0x40, 0xc8, 0x40, 0x00, 0x00, #/* ...@.@.. */
    0xe4, 0x00, 0x00, 0x00, 0x64, 0x00, 0xb2, 0x02, #/* ....d... */
    0xc8, 0x40                                      #/* .@ */
]))
# pkt20
# "20","0.515830000","192.168.222.128","10.220.104.180","CIP CM","130","Unconnected Send: Unknown Service (0x53)"
unk_020_request 		= bytes(bytearray([
                                        0x6f, 0x00, #/* 9.X...o. */
    0x34, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* 4....... */
    0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x24, 0x00, 0x52, 0x02, #/* ....$.R. */
    0x20, 0x06, 0x24, 0x01, 0x05, 0x9d, 0x16, 0x00, #/*  .$..... */
    0x53, 0x05, 0x91, 0x05, 0x53, 0x43, 0x41, 0x44, #/* S...SCAD */
    0x41, 0x00, 0x28, 0x0c, 0xc3, 0x00, 0x01, 0x00, #/* A.(..... */
    0x00, 0x00, 0x00, 0x00, 0xc9, 0x40, 0x01, 0x00, #/* .....@.. */
    0x01, 0x00                                      #/* .. */
]))
# pkt22
# "22","0.602090000","10.220.104.180","192.168.222.128","CIP","98","Success"
unk_020_reply 		= bytes(bytearray([
                                        0x6f, 0x00, #/* ..&...o. */
    0x14, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x04, 0x00, 0xd3, 0x00, #/* ........ */
    0x00, 0x00                                      #/* .. */
]))
# pkt23
# "23","0.602331000","192.168.222.128","10.220.104.180","CIP CM","126","Unconnected Send: Unknown Service (0x52)"
unk_023_request 		= bytes(bytearray([
                                        0x6f, 0x00, #/* 9..x..o. */
    0x30, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* 0....... */
    0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x20, 0x00, 0x52, 0x02, #/* .... .R. */
    0x20, 0x06, 0x24, 0x01, 0x05, 0x9d, 0x12, 0x00, #/*  .$..... */
    0x52, 0x05, 0x91, 0x05, 0x53, 0x43, 0x41, 0x44, #/* R...SCAD */
    0x41, 0x00, 0x28, 0x0c, 0x01, 0x00, 0x00, 0x00, #/* A.(..... */
    0x00, 0x00, 0x01, 0x00, 0x01, 0x00              #/* ...... */
]))
# pkt 25
# "25","0.687210000","10.220.104.180","192.168.222.128","CIP","102","Success"
unk_023_reply 		= bytes(bytearray([
                                        0x6f, 0x00, #/* ...c..o. */
    0x18, 0x00, 0x01, 0x1e, 0x02, 0x11, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, #/* ........ */
    0x00, 0x00, 0xb2, 0x00, 0x08, 0x00, 0xd2, 0x00, #/* ........ */
    0x00, 0x00, 0xc3, 0x00, 0xc8, 0x40              #/* .....@ */
]))
   
def test_enip():
    for pkt,tst in [
            ( rss_004_request,	{ 'enip.header.command': 0x0065 }),
            ( rss_004_reply,	{} ),
            ( gaa_008_request,	{} ),
            ( gaa_008_reply,	{} ),
            ( gaa_011_request,	{} ),
            ( gaa_011_reply,	{} ),
            ( unk_014_request,	{} ),
            ( unk_014_reply,	{} ),
            ( unk_017_request,	{} ),
            ( unk_017_reply,	{} ),
            ( unk_020_request,	{} ),
            ( unk_020_reply,	{} ),
            ( unk_023_request,	{} ),
            ( unk_023_reply,	{} ), ]:

        # Parse just the headers
        data			= cpppo.dotdict()
        source			= cpppo.chainable( pkt )
        name			= 'header'
        with enip.enip_header( name, context=name ) as machine:
            for i,(m,s) in enumerate( machine.run( source=source, path='enip', data=data )):
                log.info( "%s #%3d -> %10.10s; next byte %3d: %-10.10r: %r", m.name_centered(),
                          i, s, source.sent, source.peek(), data )
            assert i == 30
        log.warning( "Data: %r", data )
        assert source.peek() is not None
   
        for k,v in tst.items():
            assert data[k] == v


        # Parse the headers and encapsulated command data
        data			= cpppo.dotdict()
        source			= cpppo.chainable( pkt )
        with enip.enip_machine() as machine:
            for i,(m,s) in enumerate( machine.run( source=source, data=data )):
                log.info( "%s #%3d -> %10.10s; next byte %3d: %-10.10r: %r", m.name_centered(),
                          i, s, source.sent, source.peek(), data )

        log.warning( "Data: %r", data )
        assert source.peek() is None
   
        for k,v in tst.items():
            assert data[k] == v

        # Ensure we can reproduce the original packet from the parsed data
        assert enip.enip_encode( data ) == pkt


# Run the bench-test.  Sends some request from a bunch of clients to a server, testing responses

def enip_process_canned( addr, request ):
    log.debug( "Request: %s", enip.parser.enip_format( request ))
    if request.enip.header.command == 0x0065:
        data			= cpppo.dotdict()
        source			= cpppo.chainable( rss_004_reply )
        with enip.enip_machine() as machine: # default data context is 'enip'
            for m,s in machine.run( source=source, data=data ):
                pass
            if s:
                log.debug( "Response: %s", enip.parser.enip_format( data ))
                return data
    raise Exception( "Unrecognized request" )

client_count			= 1 #5
charrange, chardelay		= (2,10), .01	# split/delay outgoing msgs
draindelay			= 5.   		# long in case server slow, but immediately upon EOF

enip_cli_kwds			= {
	'tests':	[
            ( rss_004_request, {
                'response.enip.header.command': 	0x0065,
                'response.enip.header.session_handle':	285351425,
            }),
        ]
}

enip_svr_kwds 			= { 
    'enip_process': 	enip_process_canned,
}


def enip_cli( number, tests=None ):
    """Sends a series of test messages, testing response for ) """
    log.info( "%3d client connecting... PID [%5d]", number, os.getpid() )
    conn			= socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    conn.connect( enip.address )
    log.info( "%3d client connected", number )
        
    successes			= 0
    try:
        for req,tst in tests:
            # Parse request
            data		= cpppo.dotdict()
            sta			= None
            with enip.enip_machine() as machine:
                for mch,sta in machine.run( source=cpppo.peekable( req ), path='request', data=data ):
                    pass
            log.info( "%3d test %32s ==> %s", number, reprlib.repr( req ), enip.parser.enip_format( data ))
            assert sta and sta.terminal, "%3d client failed to decode EtherNet/IP request: %r" % req

            # Await response, sending request in chunks using inter-block chardelay if output
            # remains, otherwise await response using draindelay.  Fail if EOF from server.
            rpy			= b''
            while req:
                out		= min( len( req ), random.randrange( *charrange ))
                conn.send( req[:out] )
                req		= req[out:]

                rcvd		= network.recv( conn, timeout=chardelay if req else draindelay )
                if rcvd is not None:
                    log.info( "%3d recv: %5d: %s", number, len( rcvd ), reprlib.repr( rcvd ) if rcvd else "EOF" )
                    if not rcvd:
                        raise Exception( "Server closed connection" )
                    rpy        += rcvd

            # Parse response
            sta			= None
            with enip.enip_machine() as machine:
                for mch,sta in machine.run( source=cpppo.peekable( rpy ), path='response', data=data ):
                    pass
            log.info( "%3d test %32s <== %s", number, reprlib.repr( rpy ), enip.parser.enip_format( data ))
            assert sta and sta.terminal, "%3d client failed to decode EtherNet/IP response: %r\ndata: %s" % (
                rpy, enip.parser.enip_format( data ))

            # Successfully sent request and parsed response; can continue; test req/rpy parsed data payload.
            errors		= 0
            for k,v in tst.items():
                if data[k] != v:
                    log.warning( "%3d test failed: %s != %s; %s", number, data[k], v, enip.parser.enip_format( data ))
                    errors     += 1
            if not errors:
                successes      += 1

    except KeyboardInterrupt as exc:
        log.warning( "%3d client terminated: %r", number, exc )
    except Exception as exc:
        log.warning( "%3d client failed: %r\n%s", number, exc, traceback.format_exc() )
    finally:
        pass

    failed			= successes != len( tests )
    if failed:
        log.warning( "%3d client failed: %d/%d tests succeeded", number, successes, len( tests ))
    
    log.info( "%3d client exited", number )
    return failed

def test_enip_bench():
    failed			= cpppo.server.network.bench( server_func=enip.main,
                                                              server_kwds=enip_svr_kwds,
                                                              client_func=enip_cli,
                                                              client_kwds=enip_cli_kwds,
                                                              client_count=client_count )
    if failed:
        log.warning( "Failure" )
    else:
        log.info( "Succeeded" )

    return failed


if __name__ == "__main__":
    test_enip_bench()

