from epflmanager.commands.common import *

class Courses(object):
    def run(args):
        courses = latest_semester().courses()
        print("All courses for this semester: ")

        for c in courses:
            print("- %s" % (c.name))
