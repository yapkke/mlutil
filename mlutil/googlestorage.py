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
        self.manifests = {}
        ##Reference to refresh task
        self.__refreshs = {}
        ##Reference to config
        self.config = config
        
        server.register_cleanup(self)
        server.register_event_handler(jsoncomm.message.name, self)

    def add_gs(self, bucket_name, manifest_name=None, name=None):
        """Add gs manifest
        
        @param bucket_name name of bucket
        @param manifest_name name of manifest file (default to <bucket_name>.gsmanifest)
        @param name name (default to bucket_name)
        """
        if (name == None):
            name = bucket_name
        if (manifest_name == None):
            manifest_name = bucket_name+".gsmanifest"

        self.config.config["gs-manifests"][name] = manifest_name
        self.manifests[name]= manifest(self.server, name, bucket_name, 
                                       self.config.get_full_gs_path(manifest_name))
        self.__refreshs[name]=refresh_manifest(self.manifests[name])

    def processevent(self, event):
        """Process event

        @param event event to handle
        @return True
        """
        if (isinstance(event, jsoncomm.message)):
            reply = {}
            reply["request"] = event.message
            if (event.message["command"] == "refresh-gs"):
                name = event.message["name"]
                reply["name"] = name
                if (name not in self.__refreshs):
                    reply["error"] = "No such manifest"
                elif (not self.__refreshs[name].is_running()):
                    self.__refreshs[name] = refresh_manifest(self.manifests[name])
                    self.__refreshs[name].start()
                    reply["status"] = "started"
                else:
                    output.warn("Google storage refresh is in process,"+\
                                    " will not start another",
                                self.__class__.__name__)
                    reply["status"] = "already running"

            elif (event.message["command"] == "stop-refresh-gs"):
                name = event.message["name"]
                reply["name"] = name
                output.dbg("Stopping gs refresh of "+name,
                           self.__class__.__name__)
                if (name not in self.__refreshs):
                    reply["error"] = "No such manifest"
                elif (not self.__refreshs[name].is_running()):
                    reply["status"] = "not running"
                else:
                    self.__refreshs[name].stop()
                    while (self.__refreshs[name].is_running()):
                        time.sleep(0.1)
                    reply["status"] = "stopped"

            elif (event.message["command"] == "list-gs-manifests"):
                reply["manifests"] = []
                for name, m in self.manifests.items():
                    reply["manifests"].append(name)
    
            #Send reply
            event.reply(reply)
            
        return True

    def cleanup(self):
        """Cleanup process
        """
        for name,r in self.__refreshs.items():
            if (r.is_running()):
                r.stop()

class manifest(yapc.cleanup, base.manifest):
    """Google storage manifest
    
    @author ykk
    @date Jun 2011
    """
    def __init__(self, server, name, bucket_name, manifest_name):
        """Initialize

        @param core yapc core
        @param name name of manifest
        @param bucket_name name of bucket
        @param manifest_name name of manifest
        """
        base.manifest.__init__(self, name)
        ##Reference to configuration
        self.manifest_name = manifest_name
        self.load_manifest()
        ##Bucket
        self.bucket = bucket_name

        server.register_cleanup(self)

    def get_projects(self):
        """Get project names
        
        @return list of project names
        """
        return self.get_dir_names()

    def load_manifest(self):
        """Load content of manifest
        """
        self.load_file(self.manifest_name)
        
    def save_manifest(self):
        """Save content of manifest
        """
        self.save_file(self.manifest_name)

    def cleanup(self):
        """Cleanup manifest
        """
        self.save_manifest()

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
