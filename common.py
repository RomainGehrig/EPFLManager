import os
import sys

EPFL_DIR = "/Users/cranium/Documents/EPFL/"
SEMESTER_VALID_DIRS = ["BA", "MA"]
SITE_FILENAME = "site.url"

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

class Course(Directory):
    def get_url(self):
        url = list(filter(lambda f: f.name == SITE_FILENAME, self.files()))
        return url[0].read() if len(url) != 0 else None

class Semester(Directory):
    def __init__(self, *args):
        super(Directory, self).__init__(*args)

    @Path.memoize("courses")
    def courses(self):
        return list(map(Course(self), filter(is_course_dir, dirs_in(self.fullpath()))))

def sys_open(arg):
    # TODO: security
    os.system("open %s" % (arg.split()[0]))

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
    """ Returns all semesters dirs (full path) """
    return [os.path.join(EPFL_DIR,d) for d in dirs_in(EPFL_DIR) if is_semester_dir(d)]

def latest_semester(): 
    # As semesters returns full paths, it may be usefull to sort only on
    # the last dir instead of the full path
    return sorted(semesters(), reverse=True)[0]

def courses(semester=None):
    if semester is None:
        semester = latest_semester()

    return [ c for c in dirs_in(semester) ]

def autocomplete_course(course, semester=None):
    """ Returns all possible courses that may match the course argument """
    return [ c for c in courses(semester) if c.lower().startswith(course.lower()) ]

def handle_ambiguity(possible_choices, display_failure=True, exit_on_failure=False):
    def exit():
        if exit_on_failure:
            sys.exit(1)
    def display(s):
        if display_failure:
            print(s)

    if len(possible_choices) == 1:
        return possible_choices[0]
    elif len(possible_choices) == 0:
        display("No choice found")
        exit()
    else:
        display("Ambiguous choices: %s" % (",".join(possible_choices)))
        exit()
    
    return False

