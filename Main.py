import getopt
import json
import re
import sys

# import builtwith

import requests
from bs4 import BeautifulSoup

proxies = {}
technology = set()
vendor_id = set()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hut", ["help", "url", "test proxy"])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Help")
            sys.exit()
        elif opt in ("-u", "--url"):
            search_url(sys.argv[2:])
            # print("test argument")
        elif opt in ("-s", "--search"):
            print("search word")
        elif opt in ("-t", "--test proxy"):
            pass
            # print("test proxy ok")


def search_url(url):
    data = open_f()
    load_proxies()
    try:
        r = requests.get("https://codex.wordpress.org/Pages", proxies=proxies)
    except requests.exceptions.ProxyError:
        print("Proxy Error")
    cookies = return_cookies(r)
    soup = BeautifulSoup(r.content, "html.parser")
    # print r.content
    for tag in soup.findAll("script", src=True):
        print(tag)
    for i, j in data["apps"].items():
        if "website" in j:
            if j["website"].find(check_url("https://jquery.com/")) > -1:
                technology.add(i)
        if "headers" in j:
            if "Set-Cookie" in j["headers"] and cookies != None:
                if j["headers"]["Set-Cookie"] in cookies:
                    technology.add(i)
    print(r.headers)
    for i in r.headers.keys():
        if i == "Server":
            technology.add(r.headers[i])
            print(r.headers[i])
        if i == "X-Powered-By":
            technology.add(r.headers[i])
        if i == "X-Generator":
            technology.add(r.headers[i])
    return_cookies(r)
    check_implies(data)
    for i in technology:
        security_mark(i)
    for i in vendor_id:
        check_vendor(i)
    print(technology)


def return_cookies(req):
    cookies = req.cookies.items()
    print(cookies)
    if len(cookies) > 0:
        return cookies[0]
    else:
        return None


# def get_ext(url):
#     """Return the filename extension from url, or ''."""
#     parsed = urlparse3(url)
#     root, ext = splitext(parsed.path)
#     return ext  # or ext[1:] if you don't want the leading '.'


def open_f():
    technologies = json.load(open('apps.json'))
    return technologies


def check_implies(data):
    for i, j in data["apps"].items():
        if "implies" in j:
            if not isinstance(j["implies"], list):
                if j["implies"] in technology:
                    technology.add(j["implies"])


def security_mark(technology):
    r = requests.get("https://www.cvedetails.com/vendor-search.php?search=" + technology)
    soup = BeautifulSoup(r.content, "html.parser")
    for i in soup.find_all(class_="listtable"):
        for j in i.find_all("a", href=True):
            if str(j).find("vendor_id-") > -1:
                vendor_id.add(re.findall('\d+', str(j))[0])


def check_vendor(id):
    score = 0
    r = requests.get("https://www.cvedetails.com/vulnerability-list/vendor_id-" + id)
    soup = BeautifulSoup(r.content, "html.parser")
    for i in soup.findAll(class_="cvssbox"):
        score += float(i.encode_contents().decode(encoding="utf-8"))
    for i in soup.findAll(class_="paging"):
        for j in i.find_all("b"):
            score /= float(j.encode_contents().decode(encoding="utf-8"))
    print(score)


def check_url(url):
    if url.startswith('http'):
        url = url.replace("http://", "")
    if url.startswith('https'):
        url = url.replace("https://", "")
    if url.endswith("/"):
        url = url[:len(url) - 1]
    return url


def load_proxies():
    counter = 0
    ip = ""
    port = ""
    https = ""
    r = requests.get("https://free-proxy-list.net/")
    soup = BeautifulSoup(r.content, "html.parser")
    for tag in soup.find_all(class_="block-settings"):
        for i in tag.find_all("tbody"):
            for j in i.find_all("td"):
                if counter == 0:
                    ip = j.encode_contents()
                    # print(j.encode_contents())
                if counter == 1:
                    port = j.encode_contents()
                    # print(j.encode_contents())
                if counter == 6:
                    https = j.encode_contents()
                    # print(j.encode_contents())
                if counter == 7:
                    add_to_dict(ip, port, https)
                    counter = -1
                counter += 1
    print(proxies)


def add_to_dict(ip, port, https):
    if https == "yes":
        proxies['https'] = "https://" + str(ip) + ":" + str(port)
    else:
        proxies['http'] = "http://" + str(ip) + ":" + str(port)


if __name__ == "__main__":
    main(sys.argv[1:])
