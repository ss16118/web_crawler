# Web Crawler

This is a simple Python implementation of a multi-threaded web crawler. By giving the program
a starting URL, it will crawl and download all other pages which are linked to that page until
a specified limit is reached.

### Quick Start
To run the program, first clone the repo, set up a Python virtual environment, and run 
`pip install -r requirements` to install all dependent libraries.

It is preferred to use Python version >= 3.7, as the behaviour of the program
may be different when using a lower version of Python.

To start collecting and downloading URLs, simply type the following into the terminal
```
> cd src
> python main.py -u <starting_url>
``` 
The downloaded pages will be stored in a folder one level above the current
directory, and all the URLs will be listed in a file named _result.out_ in the
same folder. By default, the program prints out all the URLs that have been
crawled in the console along with other statistics. To disable that, you will
need to open _main.py_ and remove the last line, namely `manager.print_statistics()`.

### Command-line Options

| Options | Description | Default |
|---------|-------------|---------|
|   -h    | Prints the help message with all command-line options.  |     |
|   -u    | (__Required__) The URL from which the crawler will collect the initial set of links.  |   |
|   -n    | Maximum number of URLs to crawl / pages to download.   | 100 |
|   -t    | Maximum number of threads used to crawl the pages.     |  8  |
|   -f    | The path to the folder where the downloaded pages will be stored. | A folder in the root directory whose name is the domain name of the starting_url |
|   -v    | If set, the program prints messages to the console during the crawl. If not set, a progress bar will be displayed instead | Not Set |
|   -l    | If set, the program saves log messages to a log file.  | Not Set |

### Implementation
The implementation of the crawler can be found in the file _web_crawler.py_. The program has a centralised
set to store all the URLs that have been crawled and a queue that keeps track of all the URLs to pages
that need to be saved. 

The current implementation uses _x_ worker threads (_x_ specified by 
maximum_threads) to crawl pages simultaneously. The function passed to each worker is called `__crawl()`.
The function contains essentially a loop that never ends until the required number of pages have been crawled
or the queue is empty. At each iteration, the worker retrieves one URL from the queue, parses it, and downloads
its HTML content. Through many trials of experimentation, it was discovered that on average, if
the program is run with 8 threads, the URLs and pages will be collected and downloaded more than __80%__ 
faster than with only a single thread.

Originally, the program uses a `ThreadPoolExecutor` to distribute the work and forces the executor
to shut down when the goal is met. However, during many trials, it was found that at times, pending futures
will not be canceled even if the parameters in `ThreadPoolExecutor.shutdown()` have been set correctly.
According to the information which I found online, it might be caused by the race condition internal
to the library, as specified by this [post](https://bugs.python.org/issue31783). I have attempted to
find other means to avoid this problem, and since it came to no avail, I decided to opt for this implementation
as opposed to using the `ThreadPoolExecutor`.


### Possible Improvements
* Although the current program aims to never crawl the same page multiple times, the URLs that are stored in the 
`crawled` set are not in their canonical form. That is to say, "https://www.google.com", "http://www.google.com",
and "https://www.google.com/" will be regarded as different pages and will all be crawled. Therefore,
it might be helpful in the future to implement a function that normalises all URLs.
* Currently, the crawler only counts the number of links that cannot be crawled. Later on, more details
about these "invalid links" should also be recorded, so that we have a better understanding of the
nature of the invalidity (i.e. whether it is caused by a timeout or authentication error).
