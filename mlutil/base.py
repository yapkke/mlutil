##Base class
import copy
import simplejson

class manifest:
    """Base class for manifest

    Meaning object to store names files and directories

    @author ykk
    @date Jun 2011
    """
    ##Name for list for files
    FILE="/FILES/"
    def __init__(self):
        """Initialize
        """
        ##List of files
        self.files = {}

    def get_all_files(self, root=None, prefix=""):
        """Get list of all filenames
        
        @param root root directory to look at
        @param prefix prefix for names returned
        @return list of filenames (absolute filename)
        """
        cdir = root
        if (cdir == None):
            cdir = self.files
            prefix = ""

        r = []
        for n,d in cdir.items():
            if (n == manifest.FILE):
                for f in d:
                  r.append(prefix+f)
            else:
                r.extend(self.get_all_files(d, prefix+n+"/"))

        return r

    def get_files(self, root=None):
        """Get files in a directory
        
        @param root root directory to look at
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
        
        @param root root directory to look at
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

        @param root root directory to look at
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

        @param filename name of file
        @param root root directory to add file to
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

    def clear(self):
        """Clear manifest
        """
        self.files = {}

    def save_file(self, filename):
        """Save file listing in file

        @param filename name of file
        """
        fileRef = open(filename, "w")
        fileRef.write(simplejson.dumps(self.files))
        fileRef.close()

    def load_file(self, filename):
        """Load file listing from file

        @param filename name of file
        """
        try:
            fileRef = open(filename, "r")
            c = ""
            for l in fileRef:
                c += l
            fileRef.close()
            self.files = simplejson.loads(c)
        except IOError:
            self.files = {}

