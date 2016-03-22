import os
import logging

logger = logging.getLogger(__name__)

def sys_open(arg):
    # TODO: security
    if arg:
        arg = arg.split()[0]
        logger.debug("Opening '%s'" % arg)
        os.system("open %s" % (arg))

def display_img(path):
    # TODO: security
    if path:
        path = path.split()[0]
        os.system("imgcat %s" % (path))

def fuzzy_match(to_match, model, case_insensitive=True):
    """ Return True iff the to_match "fuzzy matches" the model.
    Not so fuzzy for the moment """
    lower = lambda x: x.lower() if case_insensitive else lambda x: x

    return lower(model).startswith(lower(to_match))
