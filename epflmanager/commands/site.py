from epflmanager.commands.common import *

SITE_FILENAME = "site.url"

class Site(object):
    @staticmethod
    def run(args):
        s = latest_semester()
        course_name = args.course
        try:
            course_directory = handle_ambiguity(s.filter_courses(lambda c: fuzzy_match(course_name, c,
                                                                                       key=lambda c_: c_.name)),
                                                display_func=lambda s: s.name)
            url, site = site_file_handler(course_directory.read_file(SITE_FILENAME))
            sys_open(url)
        except EmptyFileException:
            print("The site.url file in %s is empty." % course_directory)
        except NoChoiceException:
            pass
