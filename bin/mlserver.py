#!/usr/bin/env python
import getopt
import sys
import yapc.core as core
import yapc.interface as yapc
import yapc.log.output as output
import yapc.comm.json as jsoncomm

class mlserver(yapc.daemon):
    def __init__(self):
        yapc.daemon.__init__(self)
        ##UNIX domain socket for JSON commands
        self.sock = "mls.sock"
        ##Force bind JSON socket
        self.forcejson = True

    def run(self):
        server = core.core()
        jsonconn = jsoncommm.jsonserver(server, file=self.sock,
                                        forcebind=self.forcejson)

        server.run()        

##Print usage guide
def usage():
    """Display usage
    """
    print "Usage "+sys.argv[0]+" [options] command <parameters>"
    print "\tm-lab server"
    print  "Options:"
    print "-h/--help\n\tPrint this usage guide"
    print "-v/--verbose\n\tVerbose output"
    print "--very-verbose\n\tVery verbose output"
    print "-d/--daemon\n\tRun as daemon"

mls = mlserver()

#Parse options and arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hvdp:",
                               ["help","verbose","daemon", 
                                "very-verbose", "port=", "flow-removed"])
except getopt.GetoptError:
    print "Option error!"
    usage()
    sys.exit(2)

output.set_mode("INFO")
#Parse options
for opt,arg in opts:
    if (opt in ("-h","--help")):
        usage()
        sys.exit(0)
    elif (opt in ("-v","--verbose")):
        output.set_mode("DBG")
    elif (opt in ("--very-verbose")):
        output.set_mode("VDBG")
    elif (opt in ("-d","--daemon")):
        mls.daemon=True
    else:
        print "Unhandled option :"+opt
        sys.exit(2)

mls.start()

