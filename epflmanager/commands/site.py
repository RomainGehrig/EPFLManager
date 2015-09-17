from epflmanager.commands.common import *

SITE_FILENAME = "site.url"

class Site(object):
    @staticmethod
    def run(args):
        s = latest_semester()
        course_name = args.course
        course = handle_ambiguity(s.filter_courses(lambda c: fuzzy_match(course_name, c, key=lambda c_: c_.name)), exit_on_failure=True, display_func=lambda s: s.name)

        if course:
            sys_open(course.read_file(SITE_FILENAME))
