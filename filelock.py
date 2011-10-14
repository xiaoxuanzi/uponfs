#!/usr/bin/env python2.6
# coding: utf-8


'''
File    : x.py
Author  : drdr.xp
Contact : drdr.xp@gmail.com
Date    : 2011 Oct 14

Description : Cross process lock machenism based on file system lock lock
TODO        : If process is killed with signal 9, lockfile is not cleared.
'''


import os, sys
import time
import signal
import errno

LOCK_DIR = '/var/run/locks'

try:
    import filelockconf
    LOCK_DIR = filelockconf.LOCK_DIR
except Exception, e:
    pass


try:
    os.mkdir( LOCK_DIR )
except OSError, e:
    pass

class FileLockException(Exception):
    pass


def onTerm( signum, stackFrame ):
    sys.exit( 1 )

signal.signal( signal.SIGTERM, onTerm )

class FileLock(object):

    def __init__(self, file_name, timeout=10, delay=.1):

        self.is_locked = False
        self.lockfile  = os.path.join(LOCK_DIR, "%s.lock" % file_name)
        self.fd         = None
        self.file_name = file_name
        self.timeout   = timeout
        self.delay     = delay

    # deprecated
    def has_locked( self ):
        return os.path.isfile( self.lockfile )

    def test( self ):
        return self.has_locked()

    def acquire(self):
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                break;
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self.timeout:
                    raise FileLockException("Timeout occured.")
                time.sleep(self.delay)
        self.is_locked = True


    def release(self):
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            self.is_locked = False


    def __enter__(self):
        if not self.is_locked:
            self.acquire()
        return self


    def __exit__(self, type, value, traceback):
        if self.is_locked:
            self.release()


    def __del__(self):
        self.release()

if __name__ == "__main__":

    with FileLock( "test.txt",  timeout=2) as lock:
        print("Lock acquired.")
        import time
        time.sleep( 10 )

