##Handle all Google storage stuff
import yapc.interface as yapc
import yapc.log.output as output
import yapc.comm.json as jsoncomm

from oauth2_plugin import oauth2_plugin
import boto

import copy
import time

GOOGLE_STORAGE = 'gs'
MLAB_BUCKET = 'm-lab'

class manager(yapc.component, yapc.cleanup):
    """Class to manage Google storage

    @author ykk
    @date Jun 2011
    """
    def __init__(self, server, config):
        """Initialize
        
        @param server yapc core
        @param config config object
        """
        ##Reference to yapc core
        self.server = server
        ##Reference to manifest
        self.manifest = manifest(server, config)
        ##Reference to refresh task
        self.__refresh = refresh_manifest()

        server.register_cleanup(self)
        server.register_event_handler(jsoncomm.message.name, self)
        
    def processevent(self, event):
        """Process event

        @param event event to handle
        @return True
        """
        if (isinstance(event, jsoncomm.message)):
            reply = {}
            reply["request"] = event.message
            if (event.message["command"] == "refresh-gs"):
                if (not self.__refresh.is_running()):
                    self.__refresh = refresh_manifest()
                    self.__refresh.start()
                    reply["status"] = "started"
                else:
                    output.warn("Google storage refresh is in process,"+\
                                    " will not start another",
                                self.__class__.__name__)
                    reply["status"] = "already running"

            elif (event.message["command"] == "stop-refresh-gs"):
                output.dbg("Stopping gs refresh",
                           self.__class__.__name__)
                if (not self.__refresh.is_running()):
                    reply["status"] = "not running"
                else:
                    self.__refresh.stop()
                    while (self.__refresh.is_running()):
                        time.sleep(0.1)
                    reply["status"] = "stopped"
            
            #Send reply
            event.reply(reply)
            
        return True

    def cleanup(self):
        """Cleanup process
        """
        if (self.__refresh.is_running()):
            self.__refresh.stop()

class manifest(yapc.cleanup):
    """Google storage manifest
    
    @author ykk
    @date Jun 2011
    """
    FILE="/FILES/"
    def __init__(self, server, config):
        """Initialize

        @param config local cache configuration
        """
        ##Reference to configuration
        self.config = config
        ##List of files
        self.files = {}

        server.register_cleanup(self)

    def get_files(self, root=None):
        """Get files in a directory
        
        @return clone of list of files
        """
        cdir = root
        if (cdir == None):
            cdir = self.files
        if (manifest.FILE in cdir):
            return cdir[manifest.FILE][:]
        else:
            return []

    def get_dir_names(self, root=None):
        """Get names of subdirectories in a directory
        
        @return list of names
        """
        cdir = root
        if (cdir == None):
            cdir = self.files
        names = []
        for n,d in cdir.items():
            if (n != manifest.FILE):
                names.append(n)
        return names

    def get_dirs(self, root=None):
        """Get subdirectories in a directory

        @return clone of dictionary of directories
        """
        cdir = root
        if (cdir == None):
            cdir = self.files
        dirs = copy.deepcopy(cdir)
        if (manifest.FILE in dirs):
            del dirs[manifest.FILE]
        return dirs

    def add_file(self, filename, root=None):
        """Add file with name
        """
        cdir = root
        if (cdir == None):
            cdir = self.files

        #Create/traverse directory
        dir = filename.split("/")
        for d in dir[:-1]:
            if (d not in cdir):
                cdir[d] = {}
            cdir = cdir[d]

        #Add file to directory
        if (manifest.FILE not in cdir):
            cdir[manifest.FILE] = []
        cdir[manifest.FILE].append(dir[-1])
        
    def save_cache(self):
        """Save content of cache
        """
        fileRef = open(self.config.get_gs_cache(), "w")
        fileRef.close()

    def cleanup(self):
        """Cleanup cache
        """
        self.save_cache()

class refresh_manifest(yapc.async_task):
    """Async task to list all objects in Google storage

    @author ykk
    @date Jun 2011
    """
    def __init__(self):
        """Initialize
        """
        yapc.async_task.__init__(self)
        ##Use to indicate is stopping the task is desired
        self.__to_stop = False

    def stop(self):
        """Try to stop task
        """
        self.__to_stop = True

    def task(self):
        """Main task
        """
        uri = boto.storage_uri(MLAB_BUCKET, GOOGLE_STORAGE)
        for obj in uri.get_bucket():
            output.dbg(obj.name,
                       self.__class__.__name__)
            if (self.__to_stop):
                break

    
