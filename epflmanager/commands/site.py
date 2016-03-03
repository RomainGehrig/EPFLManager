import epflmanager.components as components
from epflmanager.commands.common import fuzzy_match, site_file_reader, sys_open
from epflmanager.io.fileorganizer import *
from epflmanager.io.console import *

SITE_FILENAME = "site.url"

class Site(object):
    @staticmethod
    def run(args):
        s = components.get("CourseHandler").latest_semester()
        course_name = args.course
        console = components.get("Console")
        try:
            course = console.choose_from(
                s.filter_courses(lambda c: fuzzy_match(course_name, c.name)),
                msg="What course do you want?",
                display_func=lambda s: s.name)

            url, site = console.choose_from(site_file_reader(course.read_file(SITE_FILENAME)),
                                            msg="Possible sites for %s" % course.name,
                                            display_func=lambda x: "%s (%s)" % (x[1].ljust(12),x[0]))
            sys_open(url)
        except NoChoiceException:
            console.warn("The %s file in %s is empty." % (SITE_FILENAME, course_name))
        except UserQuitException:
            pass
