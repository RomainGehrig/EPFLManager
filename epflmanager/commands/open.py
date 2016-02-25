import os

from epflmanager.commands.site import Site
from epflmanager.commands.common import *

class Open(object):
    @staticmethod
    def run(args,manager):
        if args.target == "site":
            Site.run(args,manager)
        elif args.target == "dir" or args.target == "d":
            s = latest_semester()
            course_name = args.course
            course = manager.choose_from(
                s.filter_courses(lambda c: fuzzy_match(course_name, c, key=lambda c_: c_.name)), display_func=lambda s: s.name)
            if course:
                manager.print(course.fullpath())
