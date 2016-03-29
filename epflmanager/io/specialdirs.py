import logging

import epflmanager.components as components
import epflmanager.parsers as parsers
from .fileorganizer import Path, Directory

logger = logging.getLogger(__name__)

class MoodleFileNotFound(FileNotFoundError): pass
class CourseURLsFileNotFound(FileNotFoundError): pass

# Should not really be here but avoid circular dependencies
class CourseNotLinkedWithMoodle(Exception): pass

class CourseDir(Directory):
    """
    A CourseDir is a directory with a little bit more to it: as it "knows"
    it has the content of a certain course, it can provide different functions
    to query its content. However, while it knows it has some kind of important
    files, it doesn't know how to interprete/parse them so it must query the
    CourseHandler to obtain such information.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def moodle_filename(self):
        return components.get("Config")["directories"]["moodle_config_file"].format(course_name=self.name)

    @property
    def moodle_file_path(self):
        return os.path.join(self.fullpath(), self.moodle_filename)

    @property
    def course_urls_filename(self):
        return components.get("Config")["directories"]["course_urls_file"]

    @property
    def course_urls_file_path(self):
        return os.path.join(self.fullpath(), self.course_urls_filename)

    @property
    def is_linked_with_moodle(self):
        ch = components.get("CourseHandler")
        try:
            return ch.moodle_id_for_course(self) is not None
        except CourseNotLinkedWithMoodle:
            return False

    def read_moodle_config(self):
        try:
            return parsers.moodle_file_parser(self.read_file(self.moodle_filename, raiseException=True))
        except FileNotFoundError as e:
            strerr = e.args[0]
            raise MoodleFileNotFound(strerr)

    def link_with_moodle(self, moodle_id):
        ch = components.get("CourseHandler")
        ch.link_course_with_moodle(self, moodle_id)

    def write_moodle_config(self, config):
        with open(self.moodle_file_path, "w") as f:
            config.write(f)

    def course_urls(self):
        """ Find the file containing the urls of interests for this course
            and return the parsed results """
        try:
            return parsers.course_urls_parser(self.read_file(self.course_urls_filename, raiseException=True))
        except FileNotFoundError as e:
            strerr = e.args[0]
            raise CourseURLsFileNotFound(strerr)

class SemesterDir(Directory):
    @Path.memoize("courses")
    def courses(self):
        course_handler = components.get("CourseHandler")
        return list(map(lambda c: c.as_class(CourseDir)
                       , filter(course_handler.can_be_course_dir, self.dirs())))

    def filter_courses(self, key=lambda x: x):
        return [c for c in self.courses() if key(c)]
