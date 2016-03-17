import epflmanager.components as components
from epflmanager.common import *

class Courses(object):
    @staticmethod
    def run(args):
        console = components.get("Console")

        console.print("All courses for this semester: ")
        for c in args.semester.courses():
            console.print("- %s" % (c.name))

    @staticmethod
    def add(args):
        ch = components.get("CourseHandler")
        ch.add_course(semester=args.semester)
