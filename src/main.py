from web_crawler import *

"""
Project Description:
Implement a very simple web crawler. It should accept a single starting URL,
such as https://news.ycombinator.com, as its input. It should download the
web page available at the input URL and extract the URLs of other pages linked
to from the HTML source code. Although there are several types of link in HTML,
just looking at the href attribute of tags will be sufficient for this task.
It should then attempt to download each of those URLs in turn to find even more
URLs, and then download those, and so on. The program should stop after it has
discovered 100 unique URLs and print them (one URL per line) as its output.
"""
if __name__ == "__main__":
    starting_url, maximum_urls, maximum_threads, verbose, log, folder = get_arguments(sys.argv[1:])
    manager = WebCrawlerManager(starting_url, maximum_urls, maximum_threads, folder, log, verbose)
    manager.initialise()
    manager.start_crawling()
    manager.print_statistics()
