import epflmanager.components as components
from epflmanager.common import *
from epflmanager.io.console import *

class CourseCommands(object):
    @staticmethod
    def listing(args):
        console = components.get("Console")

        console.print("All courses for this semester: ")
        for c in args.semester.courses():
            console.print("- %s" % (c.name))

    @staticmethod
    def add(args):
        ch = components.get("CourseHandler")
        ch.add_course(semester=args.semester)

    @staticmethod
    def go_to_url(args):
        s = args.semester
        course_name = args.course
        console = components.get("Console")

        try:
            course = console.choose_from(
                s.filter_courses(lambda c: fuzzy_match(course_name, c.name)),
                msg="What course do you want?",
                display_func=lambda s: s.name)

            url, site = console.choose_from(course.course_urls(),
                                            msg="URLs for %s" % course.name,
                                            display_func=lambda x: "%s (%s)" % (x[1].ljust(12),x[0]))
            sys_open(url)
        except NoChoiceException:
            console.warn("The %s file in %s is empty." % (urls_file, course_name))
        except UserQuitException:
            pass
