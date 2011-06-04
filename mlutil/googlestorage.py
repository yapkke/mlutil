##Handle all Google storage stuff
import yapc.interface as yapc
import yapc.log.output as output
import yapc.comm.json as jsoncomm
import time

class manager(yapc.component):
    """Class to manage Google storage

    @author ykk
    @date Jun 2011
    """
    def __init__(self, server):
        """Initialize
        
        @param server yapc core
        """
        self.server = server
        server.register_event_handler(jsoncomm.message.name, self)

    def processevent(self, event):
        """Process event

        @param event event to handle
        @return True
        """
        if (isinstance(event, jsoncomm.message)):
            refresh = refresh_manifest()
            refresh.start()
            output.dbg("Doing other thing", self.__class__.__name__)
            output.dbg("Doing other thing", self.__class__.__name__)
            output.dbg("Doing other thing", self.__class__.__name__)

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

    def task(self):
        """Main task
        """
        output.dbg("Running", self.__class__.__name__)
        time.sleep(10)
        output.dbg("End", self.__class__.__name__)

    
