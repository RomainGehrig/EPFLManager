import os

from epflmanager.commands.site import Site
from epflmanager.commands.common import *

class Open(object):
    @staticmethod
    def run(args):
        if args.target == "site":
            Site.run(args)
        elif args.target == "dir" or args.target == "d":
            s = latest_semester()
            course_name = args.course
            course = handle_ambiguity(s.filter_courses(lambda c: fuzzy_match(course_name, c, key=lambda c_: c_.name)), exit_on_failure=True, display_func=lambda s: s.name)
            if course:
                print(course.fullpath())
