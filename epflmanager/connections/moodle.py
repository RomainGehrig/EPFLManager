import requests
import os
import pickle
from urllib import parse
from collections import defaultdict

from pyquery import PyQuery

import epflmanager.components as components

# Notes:
# - not connected/enrolled if `enrol` in the response url when trying to access resources
# -

# TODO:
# - Set an expiration time (4h ?) on cookies as they are not correctly set by moodle
#

class Moodle(object):
    def __init__(self):
        config = components.get("Config")

        self._cookies = None # we don't directly use the session.cookies to load/save cookies
        self._cookie_file = config["moodle"]["cookie_file"]
        self._main_url = config["moodle"]["main_url"]
        self._course_url = config["moodle"]["course_url"]
        self._session = requests.session()

        self._important_cookies = {'MoodleSession', 'TequilaPHP', 'tequila_key', 'tequila_user'}

        # Used as caches
        self._courses = None
        self._resources = defaultdict(list)

        self.load_cookies()

    def connect(self):
        console = components.get("Console")
        cookies = self._cookies

        if cookies is not None:
            cookies.clear_expired_cookies()

        if cookies is None or not self._important_cookies.issubset(set(cookies.get_dict().keys())):
            logger.info("Outdated or no cookies, need to reauthenticate")
            console.info("Outdated or no cookies, need to reauthenticate")
            self.authentication_process()
        else:
            logger.info("Good cookies, no need to reauthenticate")
            self._session.cookies = cookies

    def save_cookies(self, cookies):
        with open(self._cookie_file, "wb") as f:
            pickle.dump(cookies, f)

    def load_cookies(self):
        """
        Try to load cookies from the cookie file.
        Fail silently if the file does not exist.
        """
        try:
            with open(self._cookie_file, "rb") as f:
                self._cookies = pickle.load(f)
        except FileNotFoundError:
            pass

    def authentication_process(self):
        loginUrl = self._main_url + "/login/"
        authUrl = self._main_url + "/auth/tequila"
        teqUrl = "https://tequila.epfl.ch/cgi-bin/tequila/login?requestkey=%s"

        login = self._session.request("get", loginUrl)

        console = components.get("Console")
        gaspar = console.input("Gaspar user: ")
        password = console.password()

        loginData = parse.urlencode({"username": gaspar, "password": password})
        loginData = loginData.encode("utf-8")

        reqkey = parse.parse_qs(parse.urlparse(login.url).query).get("requestkey")[0]

        teq = self._session.request("post", teqUrl % reqkey, data=loginData)
        del gaspar
        del password
        del loginData

        if not "You are connected as" in teq.text:
            console.error("Authentication failed")

        auth = self._session.request("get", authUrl)
        self._cookies = self._session.cookies

        # As the authentication is successful, we save the cookies collected
        self.save_cookies(self._cookies)

    @property
    def courses(self):
        # hackish way to get the id
        def get_course_id(url):
            return int(url[url.rindex('id=')+3:])

        if not self._courses:
            p = PyQuery(self._session.request("get", self._main_url + "/my/").text)
            courses = []
            p(".coc-course").find("h3").find("a").each(lambda i,e: courses.append(e.attrib))
            self._courses = { course['title']: get_course_id(course['href']) for course in courses }

        return self._courses

    def course_resources(self, course_id):
        def create_link(pylink):
            d = {}
            d.update(pylink.attrib)
            d["text"] = pylink.text_content()
            return d

        if not self._resources[course_id]:
            course_resp = self._session.request("get", self._course_url.format(course_id=course_id))

            pcourse = PyQuery(course_resp.text)

            links = []
            pcourse("h3.sectionname").parent().find("a").each(lambda i,e: links.append(e))
            attrs = list(map(lambda x: x.attrib, links))
            list(map(lambda ix: attrs[ix[0]].update({'text': ix[1].text_content()}), enumerate(links)))

            links = []
            pcourse("h3.sectionname").parent().each(lambda i,x: links.append({ "links": list(pcourse(x).find("a").map(lambda i,l: create_link(l))), "name": pcourse(x).find("h3.sectionname").text()}))
            links
            self._resources[course_id] = links

        return self._resources[course_id]

#def download_file(s, url, localfile):
#    CHUNK_SIZE = 1024
#    resp = s.request("get", url, stream=True)
#    with open(localfile, "wb") as f:
#        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
#            if chunk:
#                f.write(chunk)
#
#    return True
