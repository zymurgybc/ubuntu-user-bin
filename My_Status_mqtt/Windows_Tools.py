# -*- coding: utf-8 -*-

import re #Regular expressions
import os

class tools:
    def __init__(self, logger):
        self.logger = logger

    def getIP(self):
        # in subprocess
        #return check_output(["hostname", "--all-ip-addresses"]).decode("utf-8")
        return "127.0.0.1 localhost"

    def uptime(self):
        #libc = ctypes.CDLL('libc.so.6')
        #buf = ctypes.create_string_buffer(4096) # generous buffer to hold
        #                                        # struct sysinfo
        #if libc.sysinfo(buf) != 0:
        #    print('failed')
        #    return -1
        #
        #uptime = struct.unpack_from('@l', buf.raw)[0]
        #return uptime
        return 0

    def systemUname(self):
        uname = ' {{ "OS": "Windows" }}'
        #try:
        #   tupleString = str(os.uname()).replace("posix.uname_result(", '{ ').replace(")", ' }')
            #print(f'tuple {tupleString}')
        #   uname = re.sub("([a-zA-Z]*)=", "\"\\1\": ", tupleString)
            #print(f'uname {uname}')

        #except Exception as err1:
        #     self.logger.warning(os.path.basename(__file__) + " - systemUname() %s " % err1.args)
        #     raise err1

        return uname

