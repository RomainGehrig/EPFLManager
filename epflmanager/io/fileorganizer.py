import os
import logging

import epflmanager.components as components

logger = logging.getLogger(__name__)

class SemesterNotFound(Exception): pass

class CourseHandler(components.Component):
    """ Abstract the different directories that are used as semesters/courses """
    def __init__(self):
        config = components.get("Config")
        self._semester_directories = config["directories"].getlist("semester_directories")
        parent, name = Path.split_parent(config["directories"]["main_dir"])
        self._main_dir = Directory(parent)(name)

        # Cache
        self._semesters = {} # map from semester to courses

        super(CourseHandler, self).__init__("CourseHandler")

    def can_be_course_dir(self, d):
        """ Decide if a directory can be a course directory
        Need the directory's name only, not full path """
        if isinstance(d, Path):
            d = d.name
        return d[0] not in {"_", "."}

    def can_be_semester_dir(self, d):
        """ Decide if a directory can be a semester directory
        Need the directory's name only, not full path """
        if isinstance(d, Path):
            d = d.name
        return d in self._semester_directories

    def semesters(self):
        """ Returns all semesters """
        if not self._semesters:
           self._semesters = { d.as_class(Semester): [] for d in self._main_dir.dirs() if self.can_be_semester_dir(d) }
        return self._semesters.keys()

    def get_semester(self, name):
        semester = None
        for s in self.semesters():
            if s.name == name:
                return s
        else: # semester not found
            raise SemesterNotFound("No semester named %s found" % name)

    def sorted_semesters(self):
        """ Returns a sorted list of the semesters, the order is given by the
        `semester_directories` key in the configuration """
        semester_with_order = { name: value for value,name in enumerate(self._semester_directories) }
        return sorted(self.semesters(), key=lambda s: semester_with_order[s.name])

    def latest_semester(self):
        return self.sorted_semesters()[-1]

    def courses(self, semester=None):
        if semester is None:
            semester = self.latest_semester()

        if not self._semesters.get(semester, []):
            courses = [ c.as_class(CourseDir) for c in semester.courses ]
            self._semesters[semester] = courses

        return self._semesters[semester]

    def add_course(self, semester=None):
        # Possible ways to add a course:
        # - Inexisting directory
        # - Existing directory but not in the right place
        # - Choose format ? (camel, ...)
        if semester is None:
            semester = self.latest_semester()

        console = components.get("Console")
        semester_dir = semester.fullpath()

        course_name = console.input("Name of the course: ")
        directory = console.input("Semester directory [%s]: " % semester_dir, default=semester_dir)

        course_directory = os.path.join(directory, course_name)

        # The parent dir does not exist
        if not semester.create_directory_if_not_exists(directory):
            return False

        if os.path.exists(course_directory):
            console.warn("Path %s already exists" % course_directory)
            return False

        if not semester.create_directory_if_not_exists(course_directory):
            console.warn("Directory %s does not exist. Aborting" % course_directory)
            return False

        # Directory was created
        return True

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
    def read_file(self, filename):
        f = self.get_file(filename)
        return f.read() if f is not None else None

    def get_file(self, filename):
        files = list(filter(lambda f: f.name == filename, self.files()))
        return files[0] if len(files) != 0 else None

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

    def get_sites(self):
        """ Find the file containing the urls of interests for this course
            and return the parsed results """
        urls_file = components.get("Config")["directories"]["course_urls_file"]
        return CourseDir.course_urls_parser(self.get_file(urls_file).read())

class Semester(Directory):
    @Path.memoize("courses")
    def courses(self):
        course_handler = components.get("CourseHandler")
        return list(map(lambda c: c.as_class(CourseDir)
                       , filter(course_handler.can_be_course_dir, self.dirs())))

    def filter_courses(self, key=lambda x: x):
        return [c for c in self.courses() if key(c)]
