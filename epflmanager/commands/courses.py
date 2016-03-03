import epflmanager.components as components
from epflmanager.commands.common import *

class Courses(object):
    @staticmethod
    def run(args):
        courses = latest_semester().courses()
        console = components.get("Console")
        console.print("All courses for this semester: ")

        for c in courses:
            console.print("- %s" % (c.name))
