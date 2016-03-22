import os
import logging

import epflmanager.components as components

logger = logging.getLogger(__name__)

class SemesterNotFound(Exception): pass

class CourseHandler(components.Component):
    def __init__(self):
        super(CourseHandler, self).__init__("CourseHandler")

    def is_course_dir(self, d):
        """ Decide if a directory can be a course directory
        Need the directory's name only, not full path """
        return d[0].isupper()

    def is_semester_dir(self, d):
        """ Decide if a directory can be a semester directory
        Need the directory's name only, not full path """
        semester_directories = components.get("Config")["directories"].getlist("semester_directories")
        return d in semester_directories

    def dirs_in(self, p):
        """ Return only the directories in the specified path (only dirname) """
        return [d for d in os.listdir(p) if os.path.isdir(os.path.join(p,d))]

    def files_in(self, p, hidden=False):
        """ Return only the files in the specified path (only filename)
        Return hidden files if hidden is set to True. """
        return [f for f in os.listdir(p) if os.path.isfile(os.path.join(p,f)) and f.startswith(".") <= hidden]

    def semesters(self):
        """ Returns all semesters """
        main_dir = components.get("Config")["directories"]["main_dir"]
        return [ Semester(main_dir)(d) for d in self.dirs_in(main_dir) if self.is_semester_dir(d) ]

    def get_semester(self, name):
        semester = None
        for s in self.semesters():
            if name == s.name:
                return s
        else: # semester not found
            raise SemesterNotFound("No semester named %s found" % name)

    def sorted_semesters(self):
        """ Returns a sorted list of the semesters, the order is given by the
        `semester_directories` key in the configuration """
        semester_directories = components.get("Config")["directories"].getlist("semester_directories")
        semester_with_order = { name: value for value,name in enumerate(semester_directories) }
        return sorted(self.semesters(), key=lambda s: semester_with_order[s.name])

    def latest_semester(self):
        return self.sorted_semesters()[-1]

    def courses(self, semester=None):
        if semester is None:
            semester = self.latest_semester()
        return [ c for c in self.dirs_in(semester) ]

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
        if not self.create_directory_if_not_exists(directory):
            return False

        if os.path.exists(course_directory):
            console.warn("Path %s already exists" % course_directory)
            return False

        if not self.create_directory_if_not_exists(course_directory):
            console.warn("Directory %s does not exist. Aborting" % course_directory)
            return False

        # Directory was created
        return True


class Path(object):
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

    def fullpath(self):
        parent_path = self.parent.fullpath() if isinstance(self.parent, Path) else self.parent
        return os.path.join(parent_path, self.name)

    def clear_cache(self):
        self._cache = {}

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
    def read_file(self, filename):
        f = self.get_file(filename)
        return f.read() if f is not None else None

    def get_file(self, filename):
        files = list(filter(lambda f: f.name == filename, self.files()))
        return files[0] if len(files) != 0 else None

    @Path.memoize("dirs")
    def dirs(self):
        ch = components.get("CourseHandler")
        return list(map(Directory(self), ch.dirs_in(self.fullpath())))

    @Path.memoize("files")
    def files(self):
        ch = components.get("CourseHandler")
        return list(map(File(self), ch.files_in(self.fullpath())))

class File(Path):
    def read(self):
        with open(self.fullpath(), "r") as f:
            return f.read()

class CourseDir(Directory):
    def __str__(self):
        return self.name

class Semester(Directory):
    @Path.memoize("courses")
    def courses(self):
        course_handler = components.get("CourseHandler")
        return list(map(CourseDir(self),
                        filter(course_handler.is_course_dir,
                               course_handler.dirs_in(self.fullpath()))))

    def filter_courses(self, key=lambda x: x):
        return [c for c in self.courses() if key(c)]
