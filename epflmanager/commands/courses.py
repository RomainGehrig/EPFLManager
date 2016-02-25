from epflmanager.commands.common import *

class Courses(object):
    @staticmethod
    def run(args,manager):
        courses = latest_semester().courses()
        manager.print("All courses for this semester: ")

        for c in courses:
            manager.print("- %s" % (c.name))
