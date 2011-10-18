#!/usr/bin/env python2.6
# coding: utf-8

import socket
import time

PORT = 65500
WAIT_INTERVAL = 1

class PortLockError( Exception ): pass

class PortLock( object ):
    def __init__( self, n, timeout = WAIT_INTERVAL ):
        self.port = n
        self.is_locked = False
        self.so = None
        self.timeout = timeout

    def try_lock( self ):
        try:
            self.acquire( 0 )
            return True
        except PortLockError, e:
            return False

    def test( self ):
        return self.is_locked

    def acquire( self ):

        if self.is_locked:
            return

        for ii in range( 0, self.timeout, WAIT_INTERVAL ):
            print ii
            try:
                self._lock()
                return
            except PortLockError, e:
                time.sleep( WAIT_INTERVAL )
        else:
            raise PortLockError( self.port )

    def release( self ):
        if not self.is_locked:
            return

        try:
            self.so.close()
        except Exception, e:
            pass

    def _lock( self ):
        try:
            self.so = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.so.bind( ( '127.0.0.1', PORT + self.port ) )
            self.is_locked = True
        except socket.error, e:
            if e.errno == 98:
                raise PortLockError( self.port )
            else:
                raise

    def __enter__(self):
        self.acquire()
        return self


    def __exit__(self, type, value, traceback):
        self.release()


    def __del__(self):
        self.release()


l = PortLock( 2 )
l.acquire()

print 'acc'

time.sleep( 3 )
l.release()
print 'rel'
time.sleep( 3 )
