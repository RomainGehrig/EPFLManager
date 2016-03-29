import os
import logging

import epflmanager.components as components
import epflmanager.parsers as parsers

logger = logging.getLogger(__name__)

class Path(object):
    """ Represents an abstract path in a filesystem """
    def __new__(cls, parent):
        def set_name(name, *args, **kwargs):
            obj = object.__new__(cls)
            obj.__init__(parent, name, *args, **kwargs)
            return obj

        return set_name

    def __init__(self, parent, name):
        self._cache = {}
        self.parent = parent
        self.name = name

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.name)

    def __repr__(self):
        return "<" + str(self) + ">"

    def __eq__(self, other):
        return (type(self) is type(other) and
            os.path.normpath(self.fullpath()) == os.path.normpath(other.fullpath()))
    def __hash__(self):
        return hash(os.path.normpath(self.fullpath()))

    def exists(self):
        return os.path.exists(self.fullpath())

    def is_file(self):
        return os.path.isfile(self.fullpath())

    def is_dir(self):
        return os.path.isdir(self.fullpath())

    def fullpath(self):
        parent_path = self.parent.fullpath() if isinstance(self.parent, Path) else self.parent
        return os.path.join(parent_path, self.name)

    def clear_cache(self):
        self._cache = {}

    @staticmethod
    def split_parent(path):
        basename = os.path.basename(path)
        if not basename:
            path = os.path.dirname(path)
            basename = os.path.basename(path)

        parent = os.path.dirname(path)
        return (parent, basename)

    @staticmethod
    def memoize(attr_name):
        def inner_mem(func):
            def inner_func(self, *args, **kwargs):
                if attr_name not in self._cache:
                    self._cache[attr_name] = func(self,*args,**kwargs)
                return self._cache[attr_name]
            return inner_func
        return inner_mem

class Directory(Path):
    """ Represent a directory in the filesystem """
    def read_file(self, filename, raiseException=False):
        path = os.path.join(self.fullpath(), filename)
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            if raiseException:
                raise

    def as_class(self, cls):
        """ Enable to "cast" the directory to other classes like SemesterDir/CourseDir """
        return cls(self.parent)(self.name)

    def _names_of_dirs(self):
        """ Return the directories in the current path (only dirname) """
        p = self.fullpath()
        return [d for d in os.listdir(p) if os.path.isdir(os.path.join(p,d))]

    def _names_of_files(self, hidden=False):
        """ Return the files in the specified path (only filename)
        Return hidden files if hidden is set to True. """
        p = self.fullpath()
        return [f for f in os.listdir(p) if os.path.isfile(os.path.join(p,f)) and f.startswith(".") <= hidden]

    @Path.memoize("dirs")
    def dirs(self):
        return list(map(Directory(self), self._names_of_dirs()))

    def create_directory_if_not_exists(self, path, directory_creation_confirm=True):
        """ Create a directory if it doesn't exist
        Returns a boolean indicating if, in the end, the directory exists
        Raise OSError if there is a problem while creating the directory """

        if os.path.exists(path):
            logger.info("%s exists and is %s directory." % (path, "a" if os.path.isdir(path) else "not a"))
            return os.path.isdir(path)

        console = components.get("Console")

        if directory_creation_confirm and not console.confirm("Create directory %s" % path):
            logger.warn("Directory %s was not created." % path)
            return False

        logger.info("Creating directory %s" % path)
        os.mkdir(path)
        return True
