##Handle all Google storage stuff
import yapc.interface as yapc

class file:
    """Class to describe file in Google storage

    @author ykk
    @date May 2011
    """
    def __init__(self, name, date=None, experiment=None):
        """Initialize
        """
        ##Filename
        self.name = name
        ##Date
        self.date = date
        ##Experiment
        self.experiment = experiment

class manifest:
    """Index or manifest for Google storage

    @author ykk
    @date May 2011
    """
    def __init__(self):
        """Initialize
        """
        ##Dictionary of file description indexed by filename
        self.files = {}

    def refresh(self):
        """Refresh index
        """
        pass

