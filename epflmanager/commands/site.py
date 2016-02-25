from epflmanager.commands.common import *

SITE_FILENAME = "site.url"

class Site(object):
    @staticmethod
    def run(args,manager):
        s = latest_semester()
        course_name = args.course
        try:
            course_directory = manager.choose_from(
                s.filter_courses(lambda c: fuzzy_match(course_name, c.name)),
                display_func=lambda s: s.name)

            url, site = manager.choose_from(site_file_reader(course_directory.read_file(SITE_FILENAME)),
                                            display_func=lambda x: "%s (%s)" % (x[1].ljust(12),x[0]))
            sys_open(url)
        except NoChoiceException:
            manager.warn("The %s file in %s is empty." % (SITE_FILENAME, course_name))
        except UserQuitException:
            pass
