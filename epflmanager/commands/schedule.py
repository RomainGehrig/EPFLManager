from epflmanager.common import *

import epflmanager.components as components

class Schedule(object):
    @staticmethod
    def show(args):
        schedule_file = components.get("Config")["directories"]["schedule_file"]
        schedule = args.semester.get_file(schedule_file)
        if schedule:
            display_img(schedule.fullpath())
