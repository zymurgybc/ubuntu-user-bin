#!/usr/bin/python3.8

# sudo /usr/bin/python3.8 -m pip install sh netifaces
import os
import re                         # regular expressions
import subprocess                 # run a command and read the output
from datetime import datetime
from sh import tail               # file manipulation
import socket                     # .gethostname
import netifaces
from pprint import pformat

class HostsChecker:

    def __init__(self, configDir, logFile):
        if(os.path.exists(logFile)):
           os.File.Delete(logFile)
        self.ISSUES = logFile
        #self.LoadConfigFile(os.path.join(configDir, "myip.cronmail.config"))
        #self.LoadConfigFile(os.path.join(configDir, "dyndns-update.config"))
        self.PrepareLogs()
        # accept 0-199, 200-249, 250-255 followed by a period
        self.IP4_REGEX="((1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.){3}(1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])"
        #self.WriteOutput(self.ISSUES, self.Settings)

    def PrepareLogs(self):
        self.NMAP_DIR="/var/log/nmap"
        self.NMAP="/usr/bin/nmap"

        os.makedirs(self.NMAP_DIR, mode = 0o777, exist_ok = True)
        self.NMAP_LOG=os.path.join(self.NMAP_DIR, "nmap.log")
        self.NMAP_OLD_LOG=os.path.join(self.NMAP_DIR, "nmap_old.log")

        if os.path.isfile(self.NMAP_LOG):
            with open(self.NMAP_OLD_LOG, "a") as myfile:
                myfile.write("==================== Appended " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\r")
                for line in tail("-n 2000", self.NMAP_LOG, _iter=True):
                    myfile.write(line)

    #def LoadConfigFile(self, configFile):
    #    if not hasattr(self, "Settings"):
    #        self.Settings = {}
    #    self.WriteOutput(self.ISSUES, "Loading Config File " + configFile)
    #    with open(configFile, "r") as myfile:
    #         for line in myfile:
    #             if "=" in line:
    #                 #print("      Parsing line " + line)
    #                 key, value = line.split('=')
    #                 value = value.replace('`hostname`', socket.gethostname())
    #                 value = value.replace('`date +%Y%m`', datetime.now().strftime("%Y%m"))
    #
    #                 self.Settings[key.strip()]=value.strip('\n').strip('\"')

    def WriteLog(self, msg):
        print(msg)
        with open(self.NMAP_LOG, "a") as myfile:
            myfile.write(msg)

    def WriteOutput(self, filename, msg):
        with open(filename, "a") as myfile:
            myfile.write(msg)

    def WildcardFor(self, ipStr):
        pos = ipStr.rfind(".")
        return ipStr[: pos + 1] + "*"

    def PerformIPScan(self, ip):
        # replace the last segment with a star to scan the subnet of that address
        wildcard = self.WildcardFor(ip)
        #self.WriteLog("Checking " + wildcard + " for address " + ip)
        if re.search("^10\..*" , ip):
            self.WriteLog( "   *** Skipping subnet " + wildcard)
        else:
            self.WriteLog("Scanning subnet " + wildcard + " on " + ip)
            try:
                cmd = [self.NMAP, "-sP","--host-timeout","5","-oG","-", wildcard]
                    #\
                    #+ " | tee -a " + self.NMAP_LOG #\
                    #+ " | grep -oE " + self.IP4_REGEX.pattern
                #print(" ".join(cmd))
                #self.WriteLog(" ".join(cmd))
                cmdOut = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                for lineBytes in cmdOut.stdout.readlines():
                    aLine = lineBytes.decode('utf-8')
                    self.WriteLog(aLine)
                    addr = re.search(self.IP4_REGEX, aLine)
                    if addr:
                        OUTPUT = os.path.join(self.NMAP_DIR, "nmap_" + addr.group() + "_log")
                        if not os.path.isfile(OUTPUT):
                            self.WriteLog( datetime.now().strftime("%Y-%m-%d %T") + " = new device " + aLine)
                            self.WriteOutput(OUTPUT, datetime.now().strftime("%Y-%m-%d %T") + " = new device " + aLine)
                        self.WriteOutput(OUTPUT, "Seen " + datetime.now().strftime("%Y-%m-%d %T"))
                    else:
                        self.WriteLog("   xxx " + aLine)
            except Exception as oops:
                self.WriteLog("   *** Can't scan " + wildcard == pformat(oops))

    def PerformScan(self):
        for interface in netifaces.interfaces():
            if interface != 'lo':
                try:
                    if netifaces.AF_INET in netifaces.ifaddresses(interface):
                        for ip in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                            #pprint([ interface, type(ip), ip ])
                            if 'addr' in ip:
                                self.PerformIPScan(ip['addr'])
                            else:
                                self.WriteLog("IP "+ ip + " does not have a key 'addr'")
                    else:
                        self.WriteLog("interface "+ interface + " does not have an IP Address")
                except Exception as exc:
                    self.WriteLog("   *** Failed to process interface " + interface + " == " + pformat(exc) + "\n\r")
            else:
               self.WriteLog("Skipping interface " + interface)

if __name__ == "__main__":
    try:
        _dir = os.path.dirname(os.path.realpath(__file__))
        NMAP_TMP="/tmp/nmap_issues"

        checker = HostsChecker(_dir, NMAP_TMP)
        checker.PerformScan()
    except Exception as exc:
        self.WriteLog("   *** Failed to complete HostChecker.PerformScan() == " + pformat(exc) + "\n\r")
