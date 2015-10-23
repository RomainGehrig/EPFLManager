import requests
import getpass
import os
import pickle
from urllib import parse
from pyquery import PyQuery

COOKIE_FILE = "moodle.cookies"
MOODLE_URL = "http://moodle.epfl.ch"

def save_cookies(cookiejar, filename):
    with open(filename, "wb") as f:
        pickle.dump(cookiejar, f)

    return True

def load_cookies(filename):
    if not os.path.isfile(filename):
        return None

    with open(filename, "rb") as f:
        return pickle.load(f)

def authenticate():
    loginUrl = MOODLE_URL + "/login/"
    authUrl = MOODLE_URL + "/auth/tequila"
    teqUrl = "https://tequila.epfl.ch/cgi-bin/tequila/login?requestkey=%s"

    password = getpass.getpass()

    session = requests.session()
    login = session.request("get", loginUrl)

    loginData = parse.urlencode({"username": "gehrig", "password": password})
    loginData = loginData.encode("utf-8")
    reqkey = parse.parse_qs(parse.urlparse(login.url).query).get("requestkey")[0]

    teq = session.request("post", teqUrl % reqkey, data=loginData)
    del password
    del loginData

    if not "You are connected as" in teq.text:
        print("Authentication failed")
        import sys
        sys.exit(1)

    auth = session.request("get", authUrl)

    return session

cookies = load_cookies(COOKIE_FILE)

if cookies is not None:
    cookies.clear_expired_cookies()
    needed_cookies = ['MoodleSession', 'TequilaPHP', 'tequila_key', 'tequila_user']

if cookies is None or set(needed_cookies) != set(cookies.get_dict().keys()):
    print("Outdated or no cookies, need to reauthenticate")
    s = authenticate()
    save_cookies(s.cookies, COOKIE_FILE)
else:
    print("Good cookies, no need to reauthenticate")
    s = requests.session()
    s.cookies = cookies

def get_courses():
    p = PyQuery(s.request("get", MOODLE_URL + "/my/").text)

    courses = []
    p(".coc-course").find("h3").find("a").each(lambda i,e: courses.append(e.attrib))
    return courses

def get_course_resources(url):
    course_resp = s.request("get", url)

    pcourse = PyQuery(course_resp.text)

    links = []
    pcourse("h3.sectionname").parent().find("a").each(lambda i,e: links.append(e))
    attrs = list(map(lambda x: x.attrib, links))
    list(map(lambda ix: attrs[ix[0]].update({'text': ix[1].text_content()}), enumerate(links)))

    links = []
    pcourse("h3.sectionname").parent().each(lambda i,x: links.append({ "links": list(pcourse(x).find("a").map(lambda i,l: create_link(l))), "name": pcourse(x).find("h3.sectionname").text()}))

    return links

def create_link(pylink):
    d = {}
    d.update(pylink.attrib)
    d["text"] = pylink.text_content()
    return d

def download_file(url, localfile):
    CHUNK_SIZE = 1024
    resp = s.request("get", url, stream=True)
    with open(localfile, "wb") as f:
        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    return True
