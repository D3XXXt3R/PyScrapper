import datetime
import getopt
import json
import re
import sys

import google
import requests
from bs4 import BeautifulSoup

proxies = {}
technology = set()
vendor_id = set()
list_to_write = []
now = datetime.datetime.now()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hus", ["help", "url", "search"])
        load_proxies()
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Help")
            sys.exit()
        elif opt in ("-u", "--url"):
            data = open_f()
            search_url(sys.argv[2:], data)
        elif opt in ("-s", "--search"):
            google_search(sys.argv[2:])


def google_search(words):
    words = " ".join(words)
    data = open_f()
    for url in google.search(words, num=5, stop=1):
        search_url(url, data)


def search_url(url, data):
    if isinstance(url, list):
        url = url[0]
    print(url)
    list_to_write.append(url)
    try:
        r = requests.get(url, proxies=proxies)
    except requests.exceptions.ProxyError:
        r = requests.get(url)
    cookies = return_cookies(r)
    soup = BeautifulSoup(r.content, "html.parser")
    for i, j in data["apps"].items():
        if "website" in j:
            if j["website"].find(check_url(url)) > -1:
                technology.add(i)
        if "headers" in j:
            if "Set-Cookie" in j["headers"] and cookies != None:
                if j["headers"]["Set-Cookie"] in cookies:
                    technology.add(i)
    # print(r.headers)
    check_header(r.headers)
    return_cookies(r)
    check_script(str(soup), data)
    check_implies(data)
    # check_script(data)
    security_raport()
    list_to_write.append(technology)
    save_raport(list_to_write)
    print(technology)


def open_f():
    technologies = json.load(open('apps.json'))
    return technologies


def check_header(header):
    for i in header.keys():
        if i == "Server":
            technology.add(header[i])
        if i == "X-Powered-By":
            technology.add(header[i])
        if i == "X-Generator":
            technology.add(header[i])


def return_cookies(req):
    cookies = req.cookies.items()
    if len(cookies) > 0:
        return cookies[0]
    else:
        return None


def check_implies(data):
    for i, j in data["apps"].items():
        if "implies" in j:
            if not isinstance(j["implies"], list):
                if j["implies"] in technology:
                    technology.add(j["implies"])


def check_script(data, tag):
    for i, j in data["apps"].items():
        if "script" in j:
            print(str(tag))


# def get_ext(url):
#     """Return the filename extension from url, or ''."""
#     parsed = urlparse3(url)
#     root, ext = splitext(parsed.path)
#     return ext  # or ext[1:] if you don't want the leading '.'


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
    list_to_write.append(score)
    print(score)


def security_raport():
    for i in technology:
        security_mark(i)
    for i in vendor_id:
        check_vendor(i)


def save_raport(list_to_write_arg):
    f = open(now.strftime("%Y_%m_%d") + now.strftime("%H") + "_result" + ".txt", "a")
    for i in list_to_write:
        f.write(str(i) + "\n")
    f.write("\n")
    f.close()


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
                    ip = j.encode_contents().decode(encoding="utf-8")
                if counter == 1:
                    port = j.encode_contents().decode(encoding="utf-8")
                if counter == 6:
                    https = j.encode_contents().decode(encoding="utf-8")
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


"""This function is from builwith Python lib"""
"""https://github.com/claymation/python-builtwith"""
def check_script(html, data):
    for app_name, app_spec in data['apps'].items():
        for key in 'html', 'script':
            snippets = app_spec.get(key, [])
            if not isinstance(snippets, list):
                snippets = [snippets]
            for snippet in snippets:
                if contains(str(html), snippet):
                    technology.add(app_name)
                    break

    # check meta
    # XXX add proper meta data parsing
    metas = dict(
            re.compile('<meta[^>]*?name=[\'"]([^>]*?)[\'"][^>]*?content=[\'"]([^>]*?)[\'"][^>]*?>',
                       re.IGNORECASE).findall(
                    html))
    for app_name, app_spec in data['apps'].items():
        for name, content in app_spec.get('meta', {}).items():
            if name in metas:
                if contains(metas[name], content):
                    technology.add(app_name)
                    break

"""This function is from builwith Python lib """
"""https://github.com/claymation/python-builtwith"""
def contains(v, regex):
    """Removes meta data from regex then checks for a regex match
    """
    return re.compile(regex.split('\\;')[0], flags=re.IGNORECASE).search(v)


if __name__ == "__main__":
    main(sys.argv[1:])
