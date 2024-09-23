# -*- coding: utf-8 -*-

import ctypes
import struct
import re #Regular expressions
import os
from subprocess import check_output
#from distutils import spawn

class Linux_Tools:
    def __init__(self, logger):
        self.logger = logger

    def getIP(self):
        try:
            # Lumicube has an issue with finding the hostname execuable
            # in subprocess
            #my_hostname = spawn.find_executable("hostname")
            #my_hostname = checo_output(["/usr/bin/hostname",""])
            #if(isinstance(my_hostname, str) != True):
            #    raise Exception(os.path.basename(__file__) + " Linux_Tools.getIP() -- did not find \"hostname\" binary")
            my_hostname="/usr/bin/hostname"
            result =  check_output([my_hostname, "--all-ip-addresses"]).decode("utf-8")
            if(isinstance(result, str)):
                return result.strip()
            else:
                raise Exception(os.path.basename(__file__) + " Linux_Tools.getIP() -- check_output() did not return a string")
        except Exception as err1:
            message = os.path.basename(__file__) + " Linux_Tools.getIP() Exception: %s " % err1.args
            if(self.logger is not None):
                self.logger.error(message)
            else:
                print(message)

    def uptime(self):
        libc = ctypes.CDLL('libc.so.6')
        buf = ctypes.create_string_buffer(4096) # generous buffer to hold
                                                # struct sysinfo
        if libc.sysinfo(buf) != 0:
            print('failed')
            return -1

        uptime = struct.unpack_from('@l', buf.raw)[0]
        return uptime

    def systemUname(self):
        uname = ' {{ "Empty": "true" }}'
        try:
            tupleString = str(os.uname()).replace("posix.uname_result(", '{ ').replace(")", ' }')
            #print(f'tuple {tupleString}')
            uname = re.sub("([a-zA-Z]*)=", "\"\\1\": ", tupleString)
            #print(f'uname {uname}')

        except Exception as err1:
            message = os.path.basename(__file__) + " - systemUname() %s " % err1.args
            if(self.logger is not None):
                self.logger.warning(message)
            else:
                print(message)
            raise err1

        return uname

