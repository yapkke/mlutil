##Base class
import yapc.util.memcacheutil as mc
import yapc.log.output as output

import copy
import simplejson

class manifest:
    """Base class for manifest

    Meaning object to store names files and directories

    @author ykk
    @date Jun 2011
    """
    def __init__(self, name):
        """Initialize
        
        @param name unique name for manifest
        """
        ##Unique name
        self.name = name

        mc.get_client()
        
    def get_dir_prefix(self):
        """Return prefix for diretory
        
        @return directory prefix
        """
        return self.name+"//DIRS//"
    
    def get_file_prefix(self):
        """Return prefix for file
        
        @return filey prefix
        """
        return self.name+"//FILE//"
    
    def make_dir(self, dirname, dir=None):
        """Make directory

        like mkdir -p

        @param dirname name of directory
        @param dir directory to start from
        @return final directory name
        """
        cdir = dir
        if (cdir == None):
            cdir = ""

        #Create/traverse directory
        fdir = dirname.split("/")
        for d in fdir:
            c = mc.get(self.get_dir_prefix()+cdir)
            if (c == None):
                c = []
            if (d not in c):
                c.append(d)
            mc.set(self.get_dir_prefix()+cdir, c)
            cdir += d+"/"

        return cdir

    def load_dict(self, dictionary, prefix=""):
        """Load from dictionary
        
        @param dictionary dictionary
        """
        cdir = ""
        if (prefix != ""):
            cdir = prefix
        
        c = mc.get(self.get_file_prefix()+cdir)
        if (c == None):
            c = []
        for f in dictionary["FILES"]:
            c.append(f)
        mc.set(self.get_file_prefix()+cdir, c)
    
        c = mc.get(self.get_dir_prefix()+cdir)
        if (c == None):
            c = []
            for d in dictionary["DIRS"]:
                c.append(d["NAME"])
                self.load_dict(d, cdir+d["NAME"]+"/")
        mc.set(self.get_dir_prefix()+cdir, c)

    def delete_file(self, filename, dir=None):
        """Delete file
        
        @param filename name of file
        """
        cdir = dir
        if (cdir == None):
            cdir = ""

        fdir=(cdir+filename).split("/")
        cdir=self.make_dir("/".join(fdir[:-1]))
        
        c = mc.get(self.get_file_prefix()+cdir)
        if ((c != None) and 
            (fdir[-1] in c)):
            c.remove(fdir[-1])
            return True
        return False

    def add_file(self, filename, dir=None):
        """Add file with name

        @param filename name of file
        @param dir directory to add file to
        @return True if success
        """
        cdir = dir
        if (cdir == None):
            cdir = ""

        fdir=(cdir+filename).split("/")
        cdir=self.make_dir("/".join(fdir[:-1]))
        
        #Add file to directory
        c = mc.get(self.get_file_prefix()+cdir)
        if (c == None):
            c = []
        if (fdir[-1] in c):
            output.warn("Duplicate file: "+filename,
                        self.__class__.__name__)
            return False
        else:
            c.append(fdir[-1])
            mc.set(self.get_file_prefix()+cdir, c)
            return True

    def get_dirs(self, root=None):
        """Get subdirectories in a directory

        @param root root directory to look at
        @return clone of dictionary of directories
        """
        cdir = root
        if (cdir == None):
            cdir = ""
            
        c = mc.get(self.get_dir_prefix()+cdir)
        if (c == None):
            return []
        else:
            return c

    def get_files(self, root=None):
        """Get files in a directory
        
        @param root root directory to look at
        @return clone of list of files
        """
        cdir = root
        if (cdir == None):
            cdir = ""

        c = mc.get(self.get_file_prefix()+cdir)
        if (c == None):
            return []
        else:
            return c

    def get_all_files(self, root=None, prefix=""):
        """Get list of all filenames
        
        @param root root directory to look into
        @param prefix prefix for names returned
        @return list of filenames (absolute filename)
        """
        cdir = root
        if (cdir == None):
            cdir = ""
        
        r = []
        for f in self.get_files(cdir):
            r.append(prefix+cdir+f)

        for d in self.get_dirs(cdir):
            r.extend(self.get_all_files(cdir+d+"/", prefix))

        return r

    def __str__(self):
        """String representation
        """
        r = self.get_dict()
        return simplejson.dumps(r, indent=1)

    def get_dict(self, root=None):
        """Return dictionary object

        @param root root directory to look at
        @return 
        """
        r = {}
        cdir = root
        if (cdir == None):
            cdir = ""

        r["NAME"] = cdir[:-1].strip().split("/")[-1]
        r["FILES"] = self.get_files(cdir)
        r["DIRS"] = []
        for d in self.get_dirs(cdir):
            r["DIRS"].append(self.get_dict(root=cdir+d+"/"))

        return r

    def save_file(self, filename):
        """Save file listing in file

        @param filename name of file
        """
        fileRef = open(filename, "w")
        fileRef.write(str(self))
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
            self.load_dict(simplejson.loads(c))
        except IOError:
            pass

    def clear(self):
        """Clear manifest
        """
        self.delete_dir("")

    def delete_dir(self, root):
        """Delete directory recursively
        
        All files and subdirectories of directory will be deleted, 
        but directory will remain.

        @param root root directory to start delete
        """
        c = mc.get(self.get_file_prefix()+root)
        if (c != None):
            mc.delete(self.get_file_prefix()+root)
        
        c = mc.get(self.get_dir_prefix()+root)
        if (c != None):
            for dir in c:
                self.delete_dir(root+dir+"/")
            mc.delete(self.get_dir_prefix()+root)
