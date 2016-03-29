import unittest

from epflmanager.parsers import course_urls_parser, moodle_file_parser
from components import setup_config

class MoodleConfigParser(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_empty_content(self):
        content = ""
        config = moodle_file_parser(content)
        self.assertIsNotNone(config)

    def test_returns_configparser_instance(self):
        import configparser
        content = "[test]\nkey=value"
        config = moodle_file_parser(content)
        self.assertIsInstance(config, configparser.ConfigParser)

class CourseURLSTest(unittest.TestCase):

    DEFAULT_LABEL = "Default"
    SOME_URL = "https://google.com"

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_empty_content(self):
        content = ""
        expected = []
        self.assertListEqual(expected, course_urls_parser(content))

    def test_simple_url(self):
        content = "{}".format(self.SOME_URL)
        expected = [(self.SOME_URL, self.DEFAULT_LABEL)]
        self.assertListEqual(expected, course_urls_parser(content))

    def test_simple_url_with_spaces_in_beginning(self):
        content = "  \t  {}".format(self.SOME_URL)
        expected = [(self.SOME_URL, self.DEFAULT_LABEL)]
        self.assertListEqual(expected, course_urls_parser(content))

    def test_simple_url_with_one_word_label(self):
        content = "{} google".format(self.SOME_URL)
        expected = [(self.SOME_URL, "google")]
        self.assertListEqual(expected, course_urls_parser(content))

    def test_simple_url_with_multiple_words_label(self):
        content = "{} google is the site".format(self.SOME_URL)
        expected = [(self.SOME_URL, "google is the site")]
        self.assertListEqual(expected, course_urls_parser(content))

    def test_simple_url_with_unicode_label(self):
        unicode_label = "هاسكل" # Apparently Haskell in arabic
        content = "{} {}".format(self.SOME_URL, unicode_label)
        expected = [(self.SOME_URL, unicode_label)]
        self.assertListEqual(expected, course_urls_parser(content))

    def test_simple_url_with_useless_spaces_in_label(self):
        content = "{}     \t    google is the site   \t    ".format(self.SOME_URL)
        expected = [(self.SOME_URL, "google is the site")]
        self.assertListEqual(expected, course_urls_parser(content))

    def test_multiple_urls_with_label(self):
        content = "{}     \t    google is the site   \t  \n https://moodle.epfl.ch moodle place for everyone ".format(self.SOME_URL)
        expected = [(self.SOME_URL, "google is the site"), ("https://moodle.epfl.ch", "moodle place for everyone")]
        self.assertListEqual(expected, course_urls_parser(content))
