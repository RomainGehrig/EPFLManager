import os
import sys
import logging

from epflmanager.io import *

Logger = logging.getLogger(__name__)

EPFL_DIR = "/Users/cranium/Documents/EPFL/"
SEMESTER_VALID_DIRS = ["BA", "MA"]

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
        return list(map(Directory(self), dirs_in(self.fullpath())))

    @Path.memoize("files")
    def files(self):
        return list(map(File(self), files_in(self.fullpath())))

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
        return list(map(CourseDir(self), filter(is_course_dir, dirs_in(self.fullpath()))))

    def filter_courses(self, key=lambda x: x):
        return [c for c in self.courses() if key(c)]

def sys_open(arg):
    # TODO: security
    if arg:
        arg = arg.split()[0]
        logger.debug("Opening '%s'" % arg)
        os.system("open %s" % (arg))

def display_img(path):
    # TODO: security
    if path:
        path = path.split()[0]
        os.system("imgcat %s" % (path))

def is_course_dir(d):
    """ Decide if a directory can be a course directory
    Need the directory's name only, not full path """
    return d[0].isupper()

def is_semester_dir(d):
    """ Decide if a directory can be a semester directory
    Need the directory's name only, not full path """
    return any(map(lambda sd: d.startswith(sd), SEMESTER_VALID_DIRS))

def dirs_in(p):
    """ Return only the directories in the specified path (only dirname) """
    return [d for d in os.listdir(p) if os.path.isdir(os.path.join(p,d))]

def files_in(p, hidden=False):
    """ Return only the files in the specified path (only filename)
    Return hidden files if hidden is set to True """
    return [f for f in os.listdir(p) if os.path.isfile(os.path.join(p,f)) and f.startswith(".") <= hidden]

def semesters():
    """ Returns all semesters """
    return [ Semester(EPFL_DIR)(d) for d in dirs_in(EPFL_DIR) if is_semester_dir(d) ]

def latest_semester():
    # As semesters returns full paths, it may be useful to sort only on
    # the last dir instead of the full path
    return sorted(semesters(), key=lambda s: s.name, reverse=True)[0]

def courses(semester=None):
    if semester is None:
        semester = latest_semester()

    return [ c for c in dirs_in(semester) ]

def fuzzy_match(to_match, model, case_insensitive=True):
    """ Return True iff the to_match "fuzzy matches" the model.
    Not so fuzzy for the moment """
    lower = lambda x: x.lower() if case_insensitive else lambda x: x

    return lower(model).startswith(lower(to_match))

def site_file_reader(content):
    import re
    # Accepted inputs examples
    # 1) http://example.com Label of the site
    # 2) http://example.com
    # TODO Use a regex to match a link?
    regex = re.compile("^\s*(?P<url>\S+)\s*(?P<label>(?<=\s)\S*)?\s*$")

    sites = []
    for line in content.splitlines():
        m = regex.match(line)
        if m is None:
            continue

        url = m.groupdict().get('url')
        label = m.groupdict().get('label','Default')
        sites.append((url,label))

    logger.debug("Found sites %s." % str(sites))
    return sites
