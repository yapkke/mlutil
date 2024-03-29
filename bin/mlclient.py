#!/usr/bin/env python
import getopt
import sys
import simplejson

import yapc.core as core
import yapc.interface as yapc
import yapc.comm.json as jsoncomm
import yapc.log.output as output

import mlutil.cache as mlcache

class mlclient(yapc.component):
    """mlab client

    @author ykk
    @date Jun 2011
    """
    def __init__(self):
        self.sock = None
        self.__jclient = None
        self.commands = {}
        self.commands["refresh-gs"] = """refresh-gs [name]
\tRefresh google storage's manifest
        """

        self.commands["stop-refresh-gs"] = """stop-refresh-gs [name]
\tStop refresh of google storage's manifest
        """

        self.commands["list-gs-manifests"] = """list-gs-manifests
\tList all manifests in Google storage
        """

    def __del__(self):
        if (self.__jclient != None):
            self.__jclient.__del__()

    def get_sock(self):
        """Get socket to send command to

        @return json unix domain socket
        """
        if (self.sock == None):
            self.__config = mlcache.config()
            self.sock = self.__config.get_sock()

        if (self.__jclient == None):
            self.__jclient = jsoncomm.client(self.sock)

        output.dbg("Socket is "+str(self.sock),
                   self.__class__.__name__)
        return self.__jclient

    def send(self, obj):
        """Send object in JSON
        """
        sobj = simplejson.dumps(obj)
        self.get_sock().sock.send(sobj)

    def recv(self):
        """Receive and return pretty
        """
        return simplejson.dumps(simplejson.loads(self.__jclient.recv()),
                                                 indent=4)

    def list_gs(self):
        """List command
        """
        c = {}
        c["command"] = "list-gs-manifests"
        self.send(c)

    def refresh_gs(self, name):
        """Refresh command
        """
        c = {}
        c["command"] = "refresh-gs"
        c["name"] = name
        self.send(c)

    def stop_refresh_gs(self, name):
        """Stop-Refresh command
        """
        c = {}
        c["command"] = "stop-refresh-gs"
        c["name"] = name
        self.send(c)

##Print usage guide
def usage(mlc):
    """Display usage
    """
    print "Usage "+sys.argv[0]+" [options] command"
    print "\tm-lab client"
    print  "Options:"
    print "-h/--help\n\tPrint this usage guide"
    print "-v/--verbose\n\tVerbose output"
    print "--very-verbose\n\tVery verbose output"
    print
    print "Commands:"
    for cmd,desc in mlc.commands.items():
        print desc

mlc = mlclient()

#Parse options and arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hv",
                               ["help", 
                                "verbose","very-verbose"])
except getopt.GetoptError:
    print "Option error!"
    usage(mlc)
    sys.exit(2)

output.set_mode("INFO")
#Parse options
for opt,arg in opts:
    if (opt in ("-h","--help")):
        usage(mlc)
        sys.exit(0)
    elif (opt in ("-v","--verbose")):
        output.set_mode("DBG")
    elif (opt in ("--very-verbose")):
        output.set_mode("VDBG")
    else:
        print "Unhandled option :"+opt
        sys.exit(2)

if (len(args) == 0):
    output.err("No command found!", "mlclient")
    sys.exit(2)

if (args[0] not in mlc.commands):
    output.err("Unknown command!", "mlclient")
    sys.exit(2)

if (args[0] == "refresh-gs"):
    output.dbg("Running command "+args[0]+" "+args[1])
    mlc.refresh_gs(args[1])
elif (args[0] == "stop-refresh-gs"):
    output.dbg("Running command "+args[0]+" "+args[1])
    mlc.stop_refresh_gs(args[1])
elif (args[0] == "list-gs-manifests"):
    output.dbg("Running command "+args[0])
    mlc.list_gs()

output.info("Received "+mlc.recv(),
            mlc.__class__.__name__)
