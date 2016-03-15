import epflmanager.components as components
from epflmanager.commands.common import *

class Courses(object):
    @staticmethod
    def run(args):
        console = components.get("Console")

        console.print("All courses for this semester: ")
        for c in args.semester.courses():
            console.print("- %s" % (c.name))
