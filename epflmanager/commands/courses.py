import epflmanager.components as components
from epflmanager.commands.common import *

class Courses(object):
    @staticmethod
    def run(args):
        courses = latest_semester().courses()
        manager = components.get("Console")
        manager.print("All courses for this semester: ")

        for c in courses:
            manager.print("- %s" % (c.name))
