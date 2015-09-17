#!/usr/bin/python

from common import *

class Horaire(object):
    @staticmethod
    def run(args):
        horaire = latest_semester().get_file("horaire.png")
        if horaire:
            display_img(horaire.fullpath())
