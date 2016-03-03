import os

import epflmanager.components as components
from epflmanager.commands.site import Site
from epflmanager.commands.common import *

class Open(object):
    @staticmethod
    def run(args):
        console = components.get("Console")
        if args.target == "site":
            Site.run(args)
        elif args.target == "dir" or args.target == "d":
            s = latest_semester()
            course_name = args.course
            course = console.choose_from(
                s.filter_courses(lambda c: fuzzy_match(course_name, c, key=lambda c_: c_.name)), display_func=lambda s: s.name)
            if course:
                console.print(course.fullpath())
