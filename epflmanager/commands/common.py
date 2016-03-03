import os
import logging

from epflmanager.io import *

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

def site_file_reader(content):
    import re
    # Accepted inputs examples
    # 1) http://example.com Label of the site
    # 2) http://example.com
    # TODO Use a regex to match a link?
    regex = re.compile("^\s*(?P<url>\S+)\s*(?P<label>(?<=\s).+)?(?<=\S)\s*$")

    sites = []
    for line in content.splitlines():
        m = regex.match(line)
        if m is None:
            continue

        url = m.groupdict().get('url')
        label = m.groupdict().get('label')
        label = label if label is not None else "Default"
        sites.append((url,label))

    logger.debug("Found sites %s." % str(sites))
    return sites
