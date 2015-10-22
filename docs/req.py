import requests
import getpass
from urllib import parse
from pyquery import PyQuery


mUrl = "http://moodle.epfl.ch"
loginUrl = mUrl + "/login/"
authUrl = mUrl + "/auth/tequila"
teqUrl = "https://tequila.epfl.ch/cgi-bin/tequila/login?requestkey=%s"

password = getpass.getpass()

s = requests.session()
login = s.request("get", loginUrl)

loginData = parse.urlencode({"username": "gehrig", "password": password})
loginData = loginData.encode("utf-8")
reqkey = parse.parse_qs(parse.urlparse(login.url).query).get("requestkey")[0]

teq = s.request("post", teqUrl % reqkey, data=loginData)

if not "You are connected as" in teq.text:
    print("Authentication failed")
    import sys
    sys.exit(1)

auth = s.request("get", authUrl)

test = s.request("get", mUrl + "/my/")
p = PyQuery(test.text)

courses = []
p(".coc-course").find("h3").find("a").each(lambda i,e: courses.append(e.attrib))
