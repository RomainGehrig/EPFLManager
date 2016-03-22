import os
import logging

import epflmanager.components as components

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
        if isinstance(parent, File):
            raise Exception("A path cannot have a file parent")

        self._cache = {}
        self.parent = parent
        self.name = name

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.name)

    def __repr__(self):
        return "<" + str(self) + ">"

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
        f = self.get_file(filename, raiseException=raiseException)
        return f.read() if f is not None else ""

    def get_file(self, filename, raiseException=False):
        files = list(filter(lambda f: f.name == filename, self.files()))
        f = files[0] if len(files) != 0 else None
        if f is None and raiseException:
            raise FileNotFoundError("File %s was not found. Directory: %s" % (filename, self.fullpath()))
        return f

    def as_class(self, cls):
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

    @Path.memoize("files")
    def files(self):
        return list(map(File(self), self._names_of_files()))

    def create_directories_if_not_exists(self, path,
                                         directory_creation_confirm=True,
                                         parent_creation_confirm=True,
                                         dont_create_parent=False):
        """ Create a directory and its parent (if needed/wanted)
        Return a boolean indicating if, in the end, the wanted directory exists
        Raise OSError if there is a problem while creating some directory """

        # Existing directory
        if os.path.exists(path) and os.path.isdir(path):
            return True

        console = components.get("Console")

        # Also handles the case where path doesn't have an ending slash (backslash on Windows)
        parent = os.path.dirname(os.path.abspath(path))

        if not os.path.exists(parent) and dont_create_parent:
            logger.warn("The parent directory %s does not exist. Cannot create %s" % (parent, path))
            return False

        # Parent creation, a bit different to the self.create_directory_if_not_exists, not so invoked here
        if not os.path.exists(parent):
            # Ask user if ok to create the parent
            if parent_creation_confirm and not console.confirm("Create parent directory %s" % parent):
                logger.warn("Parent directory %s was not created. Cannot create %s." % (parent, path))
                return False

            # User accepted (or was not asked) to create the parent
            os.mkdirs(parent)

        return self.create_directory(path, directory_creation_confirm)

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

class File(Path):
    """ Represent a file in the filesystem """
    def read(self):
        with open(self.fullpath(), "r") as f:
            return f.read()

class CourseDir(Directory):
    def __str__(self):
        return self.name

    def course_urls(self):
        """ Find the file containing the urls of interests for this course
            and return the parsed results """
        urls_file = components.get("Config")["directories"]["course_urls_file"]
        return CourseDir.course_urls_parser(self.read_file(urls_file))

    @staticmethod
    def course_urls_parser(content):
        """ Parse the content given and returns a list of tuples (url,website) """
        import re
        # Accepted inputs examples
        # 1) http://example.com Label of the site
        # 2) http://example.com
        # TODO Use a regex to match a link?
        regex = re.compile("^\s*(?P<url>\S+)\s*(?P<label>(?<=\s).+)?(?<=\S)\s*$")

        sites = []
        for line in content.splitlines():
            m = regex.match(line)
            if m is None: # ignore invalid lines
                line = line.strip()
                if line:
                    logger.warn("Invalid non-empty line was found while parsing the course urls. Line: \"%s\"" % line)
                continue

            url = m.groupdict().get('url')
            label = m.groupdict().get('label')
            label = label if label is not None else "Default"
            sites.append((url,label))

        logger.debug("Found sites %s." % str(sites))
        return sites


class SemesterDir(Directory):
    @Path.memoize("courses")
    def courses(self):
        course_handler = components.get("CourseHandler")
        return list(map(lambda c: c.as_class(CourseDir)
                       , filter(course_handler.can_be_course_dir, self.dirs())))

    def filter_courses(self, key=lambda x: x):
        return [c for c in self.courses() if key(c)]
