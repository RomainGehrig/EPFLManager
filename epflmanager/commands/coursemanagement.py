import epflmanager.components as components
from epflmanager.common import *
from epflmanager.io.console import *

class CourseCommands(object):
    @staticmethod
    def listing(args):
        console = components.get("Console")
        adjustement = 20
        console.print("All courses for this semester: ")
        console.print("%s   %s" % ("Course:".ljust(adjustement), "Linked with Moodle:"))
        for c in args.semester.courses():
            console.print("- %s %s" % (c.name.ljust(adjustement), "[x]" if c.is_linked_with_moodle else ""))

    @staticmethod
    def add(args):
        ch = components.get("CourseHandler")
        console = components.get("Console")
        course_name = console.input("Name of the course: ")

        ch.add_course(course_name, semester=args.semester)

    @staticmethod
    def link(args):
        console = components.get("Console")
        course_name = args.course
        s = args.semester
        try:
            course = console.choose_from(
                s.filter_courses(lambda c: fuzzy_match(course_name, c.name) and not c.is_linked_with_moodle),
                msg="What course do you want?",
                display_func=lambda s: s.name)
            moodle_id = console.input("What is the moodle id of %s ? " % course.name)
            course.link_with_moodle(moodle_id)
            console.info("Course linked!")
        except NoChoiceException:
            pass
        except UserQuitException:
            pass

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
