import threading
import time
from queue import Queue
from utils import *
import logging

DEFAULT_DOWNLOAD_DIR = "pages/"
DEFAULT_LOG_FILE_DIR = "log/"
DEFAULT_LOG_FILE = "output.log"
DEFAULT_RESULT_FILE = "result.out"
MIN_PROCESS_TIME = 5

class WebCrawlerManager:
    def __init__(self, starting_url, maximum_urls, maximum_threads, folder, log, verbose):
        self.lock = threading.Lock()
        self.folder = folder

        queue = Queue()
        queue.put(starting_url)
        self.queue = queue
        self.crawled = set()
        self.log = log
        self.verbose = verbose
        self.maximum_urls = maximum_urls
        self.maximum_threads = maximum_threads

        # Variables used for collecting statistics
        self.start_time = 0
        self.end_time = 0
        self.failed_url_count = 0
        self.discovered_urls = 0

    """
    Initialises the setting by creating the folders and 
    crawling the starting url and saving the links it contains
    to the 'crawled' set.
    """
    def initialise(self):
        # Create the project directory for the starting url
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
            if self.verbose:
                print("Created directory {} for the starting url".format(self.folder))

        # Create the folder where all downloaded web pages should be stored
        download_folder = os.path.join(self.folder, DEFAULT_DOWNLOAD_DIR)
        if not os.path.exists(download_folder):
            os.mkdir(download_folder)
            if self.verbose:
                print("Created directory {} to store all downloaded web pages".format(download_folder))

        # Initialize logging settings
        self.__initialize_logging()

        # Crawl the page identified by starting_url
        try:
            starting_url = self.queue.get()
            page_content, retrieved_urls = self.__collect_links(starting_url)
            self.__record_results(starting_url, page_content, retrieved_urls)
        except Exception as ex:
            print("Failed to collect urls from starting url: {}".format(ex))

    """
    Initialises the logging setting by specifying the logging file path as well as the 
    loggin format. 
    """
    def __initialize_logging(self):
        # If "log" is set to True, create the folder to store the log file
        # and set up the logging configuration
        if self.log:
            log_folder = os.path.join(self.folder, DEFAULT_LOG_FILE_DIR)
            if not os.path.exists(log_folder):
                os.mkdir(log_folder)
                if self.verbose:
                    print("Created directory {} to store the log file".format(log_folder))
            log_file = os.path.join(log_folder, DEFAULT_LOG_FILE)
            logging.basicConfig(filename=log_file, encoding="utf-8", format='%(asctime)s %(levelname)s:%(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    """
    Downloads the HTML content from the url and adds the retrieved urls to 'queue'.
    """
    def __record_results(self, url, page_content, retrieved_urls):
        with self.lock:
            if len(self.crawled) < self.maximum_urls:
                save_page(page_content, os.path.join(self.folder, DEFAULT_DOWNLOAD_DIR), url)
                if self.verbose:
                    print("Saved page: {}".format(url))
                self.crawled.add(url)

                for url_to_crawl in retrieved_urls:
                    if url_to_crawl not in self.queue.queue and url_to_crawl not in self.crawled:
                        self.discovered_urls += 1
                        self.queue.put(url_to_crawl)

    """
    Starts the process by creating the worker threads.
    """
    def start_crawling(self):
        self.start_time = time.time()
        # Creates threads to start collecting links
        for _ in range(self.maximum_threads):
            crawler = threading.Thread(target=self.__crawl)
            crawler.daemon = True
            crawler.start()

        # Keep the process running for a minimum amount of time to
        # make sure the process quits before the queue is empty.
        while (len(self.crawled) < self.maximum_urls
               and len(self.queue.queue) > 0) or time.time() - self.start_time < MIN_PROCESS_TIME:
            pass
        self.end_time = time.time()

        message = "Crawling terminated!"
        if self.verbose:
            print(message)
        if self.log:
            logging.info(message)
        self.__save_results_to_file()

    """
    The job given to the worker thread. As long as there are urls in the waiting queue
    and the maximum number of urls count is not met, the worker will keep retrieving
    urls from the start of the queue and crawl them. 
    """
    def __crawl(self):
        while len(self.crawled) < self.maximum_urls and len(self.queue.queue) > 0:
            url = self.queue.get()
            try:

                page, collected_urls = self.__collect_links(url)
                self.__record_results(url, page, collected_urls)

            except Exception as ex:
                self.failed_url_count += 1
                message = "Failed to crawl url: {}\nError: {}".format(url, ex)
                if self.verbose:
                    print(message)
                if self.log:
                    logging.warning(message)
    """
    Retrieves the HTML content of a url as well as the links it contains
    """
    def __collect_links(self, url):
        message = "Thread {} is crawling {}...".format(threading.current_thread().ident, url)
        if self.verbose:
            print(message)
        if self.log:
            logging.info(message)
        page = retrieve_html_from_url(url)
        parser = URLCollector(url)
        parser.feed(page)
        return page, parser.get_collected_urls()

    """
    Outputs the statistics collected during the crawl
    """
    def print_statistics(self):
        print("======== Statistics ========")
        print("Number of threads: {}".format(self.maximum_threads))
        print("Number of unique links crawled: {}".format(len(self.crawled)))
        print("Number of unique links discovered: {}".format(self.discovered_urls))
        print("Number of links that cannot be crawled: {}".format(self.failed_url_count))
        print("Total time taken: {:.5f}s".format(self.end_time - self.start_time))
        print("Average time taken per page: {:.5f}s".format((self.end_time - self.start_time) / len(self.crawled)))
        for ix, item in enumerate(self.crawled):
            print("{}. {}".format(ix + 1, item))

    """
    Save the crawled urls to the result file
    """
    def __save_results_to_file(self):
        result_file = os.path.join(self.folder, DEFAULT_RESULT_FILE)
        message = "Save crawled urls to {}".format(result_file)
        if self.verbose:
            print(message)
        if self.log:
            logging.info(message)

        result = "\n".join(list(self.crawled))
        write_file(result, result_file)
