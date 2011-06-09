#!/usr/bin/env python
import getopt
import sys

import yapc.core as core
import yapc.interface as yapc
import yapc.log.output as output
import yapc.comm.json as jsoncomm
import yapc.util.memcacheutil as mcutil

import mlutil.cache as mlcache
import mlutil.googlestorage as gs

class mlserver(yapc.daemon):
    """mlab server

    @author ykk
    @date May 2011
    """
    def __init__(self):
        yapc.daemon.__init__(self)
        ##Force bind JSON socket
        self.forcejson = True
        mcutil.memcache_mode = mcutil.MEMCACHE_MODE["LOCAL"]

    def run(self):
        server = core.core()
        config = mlcache.config(server)
        jsonconn = jsoncomm.jsonserver(server, file=config.get_sock(),
                                       forcebind=self.forcejson)
        
        gsmgr = gs.manager(server, config)
        
        server.run()

##Print usage guide
def usage():
    """Display usage
    """
    print "Usage "+sys.argv[0]+" [options]"
    print "\tm-lab server"
    print  "Options:"
    print "-h/--help\n\tPrint this usage guide"
    print "-v/--verbose\n\tVerbose output"
    print "--very-verbose\n\tVery verbose output"
    print "-d/--daemon\n\tRun as daemon"

mls = mlserver()

#Parse options and arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hvd",
                               ["help","daemon", 
                                "verbose","very-verbose"])
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

