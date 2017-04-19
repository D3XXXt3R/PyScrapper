import getopt
import sys

import requests
from bs4 import BeautifulSoup

#popular_technology = ["wp-content", "jquery", "css", "javascript"]
technology = set()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hu", ["help", "url"])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Help")
            sys.exit()
        elif opt in ("-u", "--url"):
            search_url(sys.argv[2:])
            print("test argument")
        elif opt in ("-s", "--search"):
            print("search word")


def search_url(url):
    r = requests.get("".join(url))
    soup = BeautifulSoup(r.content)
    # print(soup)
    for tag in soup.find_all("link", href=True):
        if str(tag).find("wp-content"):
            technology.add("wp-content")
        if str(tag).find("jquery"):
            technology.add("jquery")
        if str(tag).find("css"):
            technology.add("css")
        if str(tag).find("script"):
            technology.add("javascript")
    print("Technology on scanned website " + str(technology))


if __name__ == "__main__":
    main(sys.argv[1:])
