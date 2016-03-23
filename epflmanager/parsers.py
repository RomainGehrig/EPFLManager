import logging

logger = logging.getLogger(__name__)


def moodle_file_parser(content):
    """ Parse the content given and return a ConfigParser object """
    import configparser
    moodle = configparser.ConfigParser()
    moodle.read_string(content)

    return moodle

def course_urls_parser(content):
    """ Parse the content given and returns a list of tuples (url,website) """
    import re
    # Accepted inputs examples
    # 1) http://example.com Label of the site
    # 2) http://example.com
    # TODO Use a regex to match a link?
    regex = re.compile("^\s*(?P<url>\S+)\s*(?P<label>(?<=\s).+)?(?<=\S)\s*$")

    sites = []
    for line in content.splitlines():
        m = regex.match(line)
        if m is None: # ignore invalid lines
            line = line.strip()
            if line:
                logger.warn("Invalid non-empty line was found while parsing the course urls. Line: \"%s\"" % line)
            continue

        url = m.groupdict().get('url')
        label = m.groupdict().get('label')
        label = label if label is not None else "Default"
        sites.append((url,label))

    logger.debug("Found sites %s." % str(sites))
    return sites
