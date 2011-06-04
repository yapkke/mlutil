##Handle all Google storage stuff
import yapc.interface as yapc
import yapc.log.output as output
import yapc.comm.json as jsoncomm

from oauth2_plugin import oauth2_plugin
import boto

import time

GOOGLE_STORAGE = 'gs'
MLAB_BUCKET = 'm-lab'

class manager(yapc.component):
    """Class to manage Google storage

    @author ykk
    @date Jun 2011
    """
    def __init__(self, server):
        """Initialize
        
        @param server yapc core
        """
        ##Reference to yapc core
        self.server = server
        ##Reference to refresh task
        self.__refresh = refresh_manifest()

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

    
