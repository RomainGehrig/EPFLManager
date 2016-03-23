import os

from epflmanager.common import *
import epflmanager.components as components

class Schedule(object):
    @staticmethod
    def show(args):
        schedule_file = components.get("Config")["directories"]["schedule_file"]
        path = os.path.join(args.semester.fullpath(), schedule_file)
        if os.path.exists(path):
            display_img(path)
