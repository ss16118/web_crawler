import os
import sys, getopt
import re
from urllib.parse import urlparse
import requests
from urllib import parse
from html.parser import HTMLParser

DEFAULT_PREFIX = "https://"

"""
Retrieves the command line arguments
"""
def get_arguments(argv):
    starting_url = ""
    maximum_urls = 100
    maximum_threads = 8
    verbose = False
    log = False
    folder = None

    help_message = """Usage: main.py 
    -u: starting url <Required> 
    -n: number of pages to crawl/download <Default: 100> 
    -t: maximum number of threads to use <Default: 8>
    -v: whether to output all messages in console during crawling <Default: False>
    -l: whether logging is enabled <Default: False>
    -f: folder to store output files <Default: domain name of the url>"""

    if len(argv) == 0:
        print(help_message)
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "hu:n:t:vlf:")
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(help_message)
            sys.exit()
        elif opt == "-u":
            starting_url = arg
        elif opt == "-n":
            maximum_urls = int(arg)
        elif opt == "-t":
            maximum_threads = int(arg)
        elif opt == "-v":
            verbose = True
        elif opt == "-l":
            log = True
        elif opt == "-f":
            folder = arg

    if urlparse(starting_url).hostname is None:
        starting_url = DEFAULT_PREFIX + starting_url

    folder = os.path.join(os.pardir, urlparse(starting_url, "https").hostname) if folder is None else folder
    return starting_url, maximum_urls, maximum_threads, verbose, log, folder

"""
Retrieves the content of a url and return a string
"""
def retrieve_html_from_url(url):
    try:
        page = requests.get(url, timeout=3)
        if "text/html" in page.headers["Content-Type"]:
            content = page.text
            return content
        raise Exception("Content-Type of response is not html! URL: {}".format(url))
    except KeyError:
        raise Exception("HTTP response does not contain 'Content-Type' header")
    except Exception as ex:
        raise ex

"""
Essentially an HTML parser to parse the page content and retrieve the 
desired urls.
"""
class URLCollector(HTMLParser):

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href":
                    url = parse.urljoin(self.base_url, value)
                    if not url.lower().startswith("javascript"):
                        self.urls.add(url)

    def get_collected_urls(self):
        return self.urls

    def error(self, message):
        pass


"""
Saves the content of the web page in a file. Replaces
the invalid characters to make the file name valid.
"""
def save_page(content, directory, url):
    file_name = re.sub(r'[\\/:*?\"<>|\s]', '_', url)
    write_file(content, os.path.join(directory, file_name))


"""
Write the given content to the specified file path
"""
def write_file(content, path):
    with open(path, "w+", encoding="utf-8") as file:
        file.write(content)
        file.close()
