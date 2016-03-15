from epflmanager.commands.common import *

import epflmanager.components as components

class Horaire(object):
    @staticmethod
    def run(args):
        horaire = args.semester.get_file("horaire.png")
        if horaire:
            display_img(horaire.fullpath())
