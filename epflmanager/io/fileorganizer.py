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
        SEMESTER_VALID_DIRS = components.get("Config").get("SEMESTER_VALID_DIRS")
        return any(map(lambda sd: d.startswith(sd), SEMESTER_VALID_DIRS))

    def dirs_in(self, p):
        """ Return only the directories in the specified path (only dirname) """
        return [d for d in os.listdir(p) if os.path.isdir(os.path.join(p,d))]

    def files_in(self, p, hidden=False):
        """ Return only the files in the specified path (only filename)
        Return hidden files if hidden is set to True """
        return [f for f in os.listdir(p) if os.path.isfile(os.path.join(p,f)) and f.startswith(".") <= hidden]

    def semesters(self):
        """ Returns all semesters """
        EPFL_DIR = components.get("Config").get("EPFL_DIR")
        return [ Semester(EPFL_DIR)(d) for d in self.dirs_in(EPFL_DIR) if self.is_semester_dir(d) ]

    def get_semester(self, name):
        semester = None
        for s in self.semesters():
            if name == s.name:
                return s
        else: # semester not found
            raise SemesterNotFound("No semester named %s found" % name)

    def latest_semester(self):
        # As semesters returns full paths, it may be useful to sort only on
        # the last dir instead of the full path
        return sorted(self.semesters(), key=lambda s: s.name, reverse=True)[0]

    def courses(self, semester=None):
        if semester is None:
            semester = self.latest_semester()
        return [ c for c in self.dirs_in(semester) ]

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
