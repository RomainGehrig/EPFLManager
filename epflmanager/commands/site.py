from epflmanager.commands.common import *

SITE_FILENAME = "site.url"

class Site(object):
    @staticmethod
    def run(args):
        s = latest_semester()
        course_name = args.course
        course_directory = handle_ambiguity(s.filter_courses(lambda c: fuzzy_match(course_name, c,
                                                                                   key=lambda c_: c_.name)),
                                            display_func=lambda s: s.name)

        if course_directory:
            sys_open(site_file_handler(course_directory.read_file(SITE_FILENAME))[0])
