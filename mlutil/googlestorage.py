##Handle all Google storage stuff
import yapc.interface as yapc
import yapc.log.output as output
import yapc.comm.json as jsoncomm

import mlutil.base as base

from oauth2_plugin import oauth2_plugin
import boto

import time

GOOGLE_STORAGE = 'gs'

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
        self.manifest = manifest(server, config, "m-lab", "m-lab")
        ##Reference to refresh task
        self.__refresh = refresh_manifest(self.manifest)

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
                    self.__refresh = refresh_manifest(self.manifest)
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
        
            elif (event.message["command"] == "list-projects"):
                reply["projects"] = self.manifest.get_projects()
    
            #Send reply
            event.reply(reply)
            
        return True

    def cleanup(self):
        """Cleanup process
        """
        if (self.__refresh.is_running()):
            self.__refresh.stop()

class manifest(yapc.cleanup, base.manifest):
    """Google storage manifest
    
    @author ykk
    @date Jun 2011
    """
    def __init__(self, server, config, name, bucket):
        """Initialize

        @param core yapc core
        @param config local cache configuration
        @param name name of manifest
        """
        base.manifest.__init__(self, name)
        ##Reference to configuration
        self.config = config
        self.load_cache()
        ##Bucket
        self.bucket = bucket

        server.register_cleanup(self)

    def get_projects(self):
        """Get project names
        
        @return list of project names
        """
        return self.get_dir_names()

    def load_cache(self):
        """Load content of cache
        """
        self.load_file(self.config.get_gs_cache())
        
    def save_cache(self):
        """Save content of cache
        """
        self.save_file(self.config.get_gs_cache())

    def cleanup(self):
        """Cleanup cache
        """
        self.save_cache()

class refresh_manifest(yapc.async_task):
    """Async task to list all objects in Google storage

    @author ykk
    @date Jun 2011
    """
    def __init__(self, manifest):
        """Initialize
        """
        yapc.async_task.__init__(self)
        ##Use to indicate is stopping the task is desired
        self.__to_stop = False
        ##Reference to manifest
        self.manifest = manifest

    def stop(self):
        """Try to stop task
        """
        self.__to_stop = True

    def task(self):
        """Main task
        """
        count = 0
        self.manifest.clear()
        uri = boto.storage_uri(self.manifest.bucket, GOOGLE_STORAGE)
        for obj in uri.get_bucket():
            self.manifest.add_file(obj.name)
            count += 1
            if ((count % 1000) == 0):
                output.info("Listed and processed "+str(count)+" files",
                            self.__class__.__name__)
            if (self.__to_stop):
                break
        output.info("Listed and processed "+str(count)+" files",
                    self.__class__.__name__)

