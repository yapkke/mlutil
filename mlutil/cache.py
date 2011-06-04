##Handle all local cache
import yapc.interface as yapc
import yapc.log.output as output
import os
import simplejson

DEFAULT_LOCAL_CONFIG="~/.mlutil"

class manifest:
    """Index or manifest of local files

    @author ykk
    @date May 2011
    """
    def __init__(self):
        """Initialize
        """
        pass

class config(yapc.cleanup):
    """Configuration file

    @author ykk
    @date May 2011
    """
    def __init__(self, server=None):
        """Initialize

        @param server reference to yapc core
        """
        if (server != None):
            server.register_cleanup(self)

        ##Path
        self.path = os.path.expanduser(DEFAULT_LOCAL_CONFIG)
        ##Dictionary of configuration parameters
        self.config = {}
        if (os.path.exists(self.path)):
            self.read_config()
        self.init_config()
        ##Create path if not exist
        self.check_path()

    def init_config(self):
        """Return initial default configuration
        """
        if ("path" not in self.config):
            self.config["path"] = "~/mlutil"
        if ("sock" not in self.config):
            self.config["sock"] = "mls.sock"
        if ("gs-cache" not in self.config):
            self.config["gs-cache"] = "gs.cache"

        return self.config

    def get_gs_cache(self):
        """Get cache file for Google storage
        """
        return self.get_path()+"/"+self.config["gs-cache"]

    def get_sock(self):
        """Get socket
        """
        return self.get_path()+"/"+self.config["sock"]

    def get_path(self):
        """Get path
        """
        return os.path.expanduser(self.config["path"])

    def check_path(self):
        """Create path if not exist
        """
        p = self.get_path()
        if (not os.path.exists(p)):
            output.info("Creating path "+p,
                        self.__class__.__name__)
            os.makedirs(p)

    def cleanup(self):
        """Cleanup configuration
        """
        self.write_config()
        output.dbg("Saved configuration",
                   self.__class__.__name__)

    def read_config(self):
        """Read configuration file
        """
        output.dbg("Reading configuration file "+str(self.path),
                   self.__class__.__name__)
        fileRef = open(self.path, "r")
        c = ""
        for line in fileRef:
            c += line
        fileRef.close()

        self.config = simplejson.loads(c)

    def write_config(self):
        """Write configuraiton file
        """
        output.dbg("Writing configuration file "+str(self.path),
                   self.__class__.__name__)
        c = simplejson.dumps(self.config, sort_keys=True, indent=4 * ' ')
        fileRef = open(self.path, "w")
        fileRef.write(c)
        fileRef.close()

