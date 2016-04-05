import os
import logging
from collections import OrderedDict

import epflmanager.components as components
from epflmanager.io import *

logger = logging.getLogger(__name__)

class SemesterNotFound(Exception): pass
class CourseNotFound(Exception): pass

class CourseHandler(components.Component):
    """ Abstract the different directories that are used as semesters/courses """
    def __init__(self):
        self._init()
        super().__init__("CourseHandler")

    def _init(self):
        """ Read Config and empty caches """
        config = components.get("Config")
        self._semester_directories = config.getlist("directories", "semester_directories")
        parent, name = Path.split_parent(config["directories"]["main_dir"])
        self._main_dir = Directory(parent)(name)

        # Cache
        self._semesters = {} # map from semester to (map from names to courses)
        self._courses = {} # map from name to courses

    def can_be_course_dir(self, d):
        """ Decide if a directory can be a course directory
        Need the directory's name only, not full path """
        if isinstance(d, Path):
            d = d.name
        return d[0] not in {"_", "."}

    def is_semester_dir(self, d):
        """ Decide if a directory can be a semester directory
        Need the directory's name only, not full path """
        if isinstance(d, Path):
            d = d.name
        return d in self._semester_directories

    def semesters(self):
        """ Returns all semesters """
        if not self._semesters:
           self._semesters = { d.as_class(SemesterDir): {} for d in self._main_dir.dirs() if self.is_semester_dir(d) }
        return list(self._semesters.keys())

    def get_semester(self, name):
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
        sem = self.sorted_semesters()
        if len(sem) == 0:
            raise SemesterNotFound("No semester was found.")
        return sem[-1]

    def courses(self, semester=None):
        if semester is None:
            semester = self.latest_semester()

        if not self._semesters.get(semester, None):
            courses = ( (c.name,c.as_class(CourseDir)) for c in semester.courses() )
            self._semesters[semester] = OrderedDict(courses)

        return list(self._semesters[semester].values())

    def get_course(self, course_name, semester=None):
        """ Try to retreive a course by its name, raise a CourseNotFound exception if
        there is no such course """
        if semester is None:
            semester = self.latest_semester()

        # initialize the courses
        courses = self.courses(semester=semester)
        if not course_name in self._semesters[semester]:
            raise CourseNotFound("Course %s could not be found" % course_name)

        return self._semesters[semester][course_name]

    def add_course(self, course_name, semester=None, ask_confirmation=False):
        # Possible ways to add a course:
        # - Inexisting directory
        # - Existing directory but not in the right place
        # - Choose format ? (camel, ...)
        if semester is None:
            semester = self.latest_semester()

        semester_dir = semester.fullpath()
        course_directory = os.path.join(semester_dir, course_name)

        console = components.get("Console")
        if not semester.create_directory_if_not_exists(course_directory, ask_confirmation):
            console.warn("Directory %s was not created. Aborting." % course_directory)
            return False

        # Directory was created
        return True

    def moodle_id_for_course(self, course):
        try:
            config = course.read_moodle_config()
            return config["course"]["moodle_id"]
        except (KeyError, MoodleFileNotFound):
            raise CourseNotLinkedWithMoodle("Course %s is not linked with Moodle." % course.name)

    def link_course_with_moodle(self, course, moodle_id):
        import configparser

        moodle_config = None
        try:
            moodle_config = course.read_moodle_config()
            logger.debug("Moodle file for %s exists and was read." % course)
            if not "course" in moodle_config:
                moodle_config.add_section("course")
            moodle_config["course"]["moodle_id"] = str(moodle_id)
        except MoodleFileNotFound:
            logger.info("Creating the moodle config for the course %s" % course.name)
            moodle_config = CourseHandler.moodle_config_skeleton(course_name=course.name, moodle_id=moodle_id)

        course.write_moodle_config(moodle_config)

    @staticmethod
    def moodle_config_skeleton(course_name, moodle_id):
        from configparser import ConfigParser
        config = ConfigParser()
        config.add_section("course")
        config['course']['course_name'] = course_name
        config['course']['moodle_id'] = str(moodle_id)
        return config
