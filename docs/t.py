import getpass

from http.client import HTTPConnection, HTTPSConnection
from http.cookiejar import CookieJar
from urllib import request, parse

cookiejar = CookieJar()
opener = request.build_opener(request.HTTPCookieProcessor(cookiejar))

password = getpass.getpass()

# First: get a cookie and a redirect
connMoodle = HTTPConnection("moodle.epfl.ch", 80)
connMoodle.request("GET", "/auth/tequila/index.php")
resp_ = connMoodle.getresponse()
resp_.read()

# Second: POST data to the login url
cookies = resp_.headers.get_all("Set-Cookie")
cookie_str = "; ".join(cookies)
reqkey = parse.parse_qs(parse.urlparse(resp_.headers.get("Location")).query).get("requestkey")[0]

loginURL = "https://tequila.epfl.ch/cgi-bin/tequila/login"
data = parse.urlencode({"username": "gehrig", "password": password})
data = data.encode("utf-8")

connTequila = HTTPSConnection("tequila.epfl.ch")
connTequila.request("POST", "/cgi-bin/tequila/login?requestkey" + reqkey, body=data)

#resp = opener.open("http://moodle.epfl.ch/auth/tequila/index.php")
#loginURL = "https://tequila.epfl.ch/cgi-bin/tequila/login"
#moodleTestURL = "http://moodle.epfl.ch/my/"
#
#data = parse.urlencode({"username": "gehrig", "password": password})
#data = data.encode("utf-8")
#reqkey = '?requestkey=' + parse.parse_qs(parse.urlparse(resp.url).query).get("requestkey")[0]
#resp2 = opener.open(loginURL + reqkey, data)
#
#test1 = opener.open(moodleTestURL)



#url = parse.urlencode({ "password": password, 'key':"asdasd" })
