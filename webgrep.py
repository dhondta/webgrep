#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "Alexandre D'Hondt"
__email__ = "alexandre.dhondt@gmail.com"
__version__ = "1.2"
__copyright__ = """License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."""
__repository__ = "https://github.com/dhondta/webgrep"
__doc__ = """Search for PATTERN in each input URL and its related resources
 (images, scripts and style sheets).
PATTERN is, by default, a basic regular expression (BRE).
Important note: webgrep does not handle recursion (in other words, it does not
                spider additional web pages).
Example: webgrep -i 'hello world' http://www.example.com
"""

# -------------------- IMPORTS SECTION --------------------
import argparse
import base64
import gc
import logging
import os
import re
import requests
import shutil
import signal
import sys
from os.path import basename, dirname, exists, join
from subprocess import call, Popen, PIPE, STDOUT
P3 = sys.version_info >= (3,0)
# Python2/3 specific imports
if P3:
    from urllib.request import getproxies
    from urllib.parse import urlparse, urljoin
else:
    from urllib import getproxies
    from urlparse import urljoin, urlparse
# BeautifulSoup
try:
    import bs4
except ImportError:
    print("BeautifulSoup is not installed !\nPlease run 'sudo pip{} install"
          " beautifulsoup4' before continuing.".format(["", "3"][P3]))
    sys.exit(1)
# colorize logging
try:
    import coloredlogs
    colored_logs_present = True
except ImportError:
    print("(Install 'coloredlogs' for colored logging)")
    colored_logs_present = False
# disable annoying requests warnings
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except AttributeError:
    print("Failed to disable warnings for requests !\nPlease run 'sudo pip{} "
          "install --upgrade requests' to fix it.".format(["", "3"][P3]))
    sys.exit(1)
logging.getLogger("requests").setLevel(logging.CRITICAL)


# -------------------- CONSTANTS SECTION --------------------
CSS_IMG_REGEX = re.compile(b'url\(([^)]+)\)' if P3 else r'url\(([^)]+)\)')
CSS_INDENT = 2
CSS_MINIFIED_THRESHOLD = 256
DATE_FORMAT = '%H:%M:%S'
DEVNULL = open(os.devnull, 'w')
IMG_NAME = 'raw-image-{:>03}.{}'
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
PROXIES = getproxies() or {k.split('_')[0].lower(): os.environ[k] for k in \
    ['HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY'] if k in os.environ.keys()}
RESOURCE_TYPES = ['image', 'script', 'style']
TEMP_DIR = '/tmp/webgrep'


# -------------------- HANDLERS SECTION ---------------------
# Categories:
# - preprocessors: applied on downloaded resources ; these REPLACE the resource
# - tools: applied after resource download and processing ; these DERIVE new
#          resources
# Naming convention:
#   [resource type]_[preprocessors|tools]
#   e.g. STYLE_TOOLS, IMAGE_PREPROCESSORS
# Structure: dictionary with
# - key: the name of the binary or module
# - value: tuple of the form (type, handler, message if not exists)
#    NB: the handler always takes a Resource object in argument
# Handlers are automatically set as attributes in 'args'
get_cmd = lambda t: lambda r: Popen([t, r.rel_fn], stdout=PIPE,
                              stderr=DEVNULL, cwd=args.tmp).communicate()[0]

def css_unminifier(res):
    """
    Minimalistic CSS unminifying function.
    """
    if res.type != "style":
        return
    # CSS is considered minified if any line is longer than a given length
    if any([len(l) > CSS_MINIFIED_THRESHOLD for l in res.content.split('\n')]):
        res.content = re.sub("\*\/", "*/\n\r", res.content)
        res.content = re.sub("\{", " {\n\r" + " " * CSS_INDENT, res.content)
        res.content = re.sub(";", ";\n\r" + " " * CSS_INDENT, res.content)
        res.content = re.sub("\}", ";\n\r}\n\r", res.content)
    return res.content


def tesseract(res):
    """
    Tesseract handler for applying OCR on images.
    """
    if res.type != "image":
        return
    output = []
    for i in range(3,11):
        cmd = ['tesseract', res.rel_fn, 'stdout', '-psm', str(i)]
        result = Popen(cmd, stdout=PIPE, stderr=DEVNULL, cwd=args.tmp) \
                     .communicate()[0].strip()
        if len(result) > 0:
            for line in result.split(['\n', b'\n'][P3]):
                if line not in output:
                    output.append(line)
    return ['\n', b'\n'][P3].join(output)


IMAGE_TOOLS = {
    "exiftool": ('binary', get_cmd("exiftool"),
                 "Binary required for getting image EXIF info ;\n"
                 " consider running 'sudo apt-get install exiftool'"),
    "strings": ('binary', get_cmd("strings"),
                "Binary required for getting strings from downloaded files ;"
                "\n consider running 'sudo apt-get install strings'"),
    "tesseract": ('binary', tesseract,
                  "Binary required for trying OCR on images ;"
                  "\n consider running 'sudo apt-get install tesseract-ocr'"),
}
SCRIPT_PREPROCESSORS = {
    "jsbeautifier": ('module', lambda r: jsbeautifier.beautify(r.content),
                     "Python library required for deobfuscating Javascript ;"
                     "\n consider running 'sudo pip{} install jsbeautifier'"
                     .format(["", "3"][P3])),
}
STYLE_PREPROCESSORS = {
    "unminifier": ('function', css_unminifier, None),
}


# -------------------- FUNCTIONS SECTION --------------------
def __exit_handler(signal=None, frame=None, code=0):
    """
    Exit handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    if 'args' in globals():
        if args.keep:
            logger.info("Temporary files are available at {}".format(args.tmp))
        else:
            logger.debug("Removing temporary folder {}".format(args.tmp))
            shutil.rmtree(args.tmp)
    logging.shutdown()
    sys.exit(code)
# bind termination signal (Ctrl+C) to exit handler
signal.signal(signal.SIGINT, __exit_handler)


def __installed(item, itype, message=None):
    """
    Item existence check ; display message if the item is not installed and 
     return boolean so that it can be determined if the item can be used.

    :param item: item to be checked
    :param itype: item type (binary | module | function)
    :param message: message to be displayed if the item is not installed
    :return: True if the item is installed, False otherwise.
    """
    if itype == 'binary':
        try:
            call([item, '--help'], stdout=DEVNULL, stderr=STDOUT)
            return True
        except OSError:
            if message is not None:
                logger.warn(message)
            return False
    elif itype == 'module':
        try:
            globals()[item] = __import__(item)
            return True
        except ImportError:
            if message is not None:
                logger.warn(message)
            return False
    elif itype == 'function':
        # no check required ; this relates to a locally declared function
        return True
    else:
        logger.warn("Unknown item type ({})".format(itype))


# --------------------- CLASSES SECTION ---------------------
class ArgCollectOption(argparse.Action):
    """
    Argparse action for handling keyword arguments collection in grep_opts
     so that these can be passed to grep.
    """
    def __call__(self, parser, args, values, option_string=None):
        if not hasattr(args, "grep_opts") or args.grep_opts is None:
            args.grep_opts = []
        if values is not None:
            if len(self.dest) == 1:
                args.grep_opts.append("-" + self.dest)
                args.grep_opts.append("{}".format(values))
            elif len(self.dest) > 1:
                dest = self.dest.replace('_', '-')
                args.grep_opts.append("--{}={}".format(dest, values))
        delattr(args, self.dest)


class ArgVersion(argparse.Action):
    """
    Display version by calling -V/--version.
    """
    def __call__(self, parser, args, values, option_string=None):
        print("webgrep {}".format(__version__))
        print(__copyright__)
        print("\nWritten by {}, see <{}>.".format(__author__, __repository__))
        globals()['__exit_handler']()


class GetHeader(argparse.Action):
    """
    Collect HTTP headers.
    """
    def __call__(self, parser, args, values, option_string=None):
        if not hasattr(args, "headers") or args.headers is None:
            args.headers = {}
        if values is not None:
            args.headers[self.dest.capitalize()] = values
        delattr(args, self.dest)


class ProxySetting(argparse.Action):
    """
    Manually set proxy setting.
    """
    def __call__(self, parser, args, values, option_string=None):
        if values is not None:
            PROXIES[self.dest] = values
        delattr(args, self.dest)


class Resource(object):
    """
    Class for downloading web page and its related resources and for grepping
     each downloaded data.
    """
    grep_exclude = ["image"]
    headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64;"
                             " rv:50.0) Gecko/20100101 Firefox/50.0",
               'Accept': "text/html,application/xhtml+xml,application/"
                         "xml;q=0.9,*/*;q=0.8",
               'Accept-Language': "en-US,en;q=0.5",
               'Accept-Encoding': "gzip, deflate",
               'Connection': "keep-alive",
               'DNT': "1",
               'Upgrade-Insecure-Requests': "1"}

    def __init__(self, url, restype="page"):
        self.url = url
        self.netloc = urlparse(self.url).netloc
        self.type = restype
        url_path = urlparse(url).path
        fn = basename(url_path) or "index.html"
        fp = dirname(url_path).strip('/')
        self.rel_fn = join(self.netloc, fp, fn)
        self.abs_fn = join(args.tmp, self.rel_fn)
        abs_fp = dirname(self.abs_fn)
        if not exists(abs_fp):
            os.makedirs(abs_fp)

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        del self
        gc.collect()

    def _derive_resources(self, handlers={}):
        """
        Derive new resources by applying available tools as defined in the
         global constants (see HANDLERS SECTION).
        """
        attr = "{}_tools".format(self.type)
        if not hasattr(args, attr):
            return
        for tool, handler in getattr(args, attr):
            fn = "{}-{}.txt".format(self.rel_fn, tool)
            with Resource(fn, "derived") as res:
                logger.debug("> Deriving {}".format(res.abs_fn))
                if not exists(res.abs_fn):
                    with open(res.abs_fn, 'wb') as f:
                        content = handler(self)
                        f.write(bytes(content, 'utf-8') if P3 and not \
                                isinstance(content, bytes) else content)
                res.grep()

    def _is_allowed(self, netloc):
        """
        Handle only same-origin or also external resources.
        """
        return netloc is None or not args.same_origin or \
            (args.same_origin and self.netloc == netloc)
        # netloc is None when it is about a web page

    def download(self, netloc=None):
        """
        Download the resource then save it to a temporary folder. Afterwards,
         trigger grep and particular handling.
        """
        if not self._is_allowed(netloc):
            return
        # useful e.g. if --keep-files was used ; allows to re-grep on different
        #  keywords without re-downloading everything
        if exists(self.abs_fn):
            with open(self.abs_fn, 'rb') as f:
                self.content = f.read()
            self.grep().handle()
            return
        logger.debug("> Downloading {}".format(self.url))
        self.headers.update(args.headers)
        req = requests.Request('GET', self.url, headers=self.headers).prepare()
        try:
            resp = session.send(req, proxies=PROXIES if args.proxy else {},
                                verify=False, stream=True)
        except requests.exceptions.ProxyError as e:
            if bool(PROXIES):
                # try next requests disabling the proxy
                logger.debug("Disabling proxy settings")
                globals()['PROXIES'] = {}
                resp = session.send(req, proxies=PROXIES if args.proxy else {},
                                    verify=False, stream=True)        
            else:
                # proxy already disabled, just throw the exception
                raise e
        Resource.pprint_req(req)
        Resource.pprint_resp(resp)
        if resp.status_code == 200:
            # images are handled separately in chunks, no preprocessor applied
            if self.type == "image":
                with open(self.abs_fn, 'wb') as f:
                    for chunk in resp:
                        f.write(chunk)
                self.content = ''
            # other types of resources are handled with preprocessors
            else:
                self.content = resp.text.encode(resp.encoding) if \
                    resp.encoding is not None else resp.text
                attr = '{}_preprocessors'.format(self.type)
                if hasattr(args, attr):
                    for tool, handler in getattr(args, attr):
                        logger.debug("> Preprocessing with {}".format(tool))
                        self.content = handler(self)
                with open(self.abs_fn, 'wb') as f:
                    f.write(bytes(self.content, 'utf-8') if P3 and not \
                            isinstance(self.content, bytes) else self.content)
            self.grep().handle()
        else:
            logger.error("Failed to get {} ({} - {})".format(self.url,
                             resp.status_code, resp.reason))

    def grep(self):
        """
        Call built-in grep command on the downloaded resource then remove it.
        """
        if self.type not in self.grep_exclude:
            logger.debug("> Grepping {}".format(self.abs_fn))
            cmd = ' '.join(['grep', '--color=always']
                           + (args.grep_opts or []) \
                           + [args.pattern, self.rel_fn])
            logger.debug(">> Command: {}".format(cmd))
            out = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=args.tmp,
                        shell=True).communicate()[0]
            # NB: despite the fact that shell=True is not recommended, it is
            #  used as, otherwise, the command is not properly handled
            #  regarding patterns with quotes
            if len(out) > 0:
                print(out.decode('utf-8'))
        return self

    def handle(self):
        """
        Handle the downloaded resource according to its type.
        - web page: search for images (also handle raw images), scripts and
                    style sheets
        - images: apply multiple tools then only grep on these results
        - scripts: try to deobfuscate then also grep on these results
        - style sheets: search for image references then download them for 
                        normal image handling
        """
        if self.type == "page":
            soup = bs4.BeautifulSoup(self.content, 'html.parser')
            # download images
            raw_img = 0
            for img in soup.find_all("img", src=True):
                # handle raw base64-encoded images
                if img['src'].startswith("data:image"):
                    try:
                        imgt, data = img['src'].split(";")
                        enc, data = data.split(",")
                        if enc != "base64":
                            raise Exception("Bad image encoding")
                        fn = IMG_NAME.format(raw_img, imgt.split('/')[1])
                        with Resource(fn, "image") as res:
                            with open(res.abs_fn, 'wb') as f:
                                f.write(base64.b64decode(data))
                            res.grep().handle()
                        raw_img += 1
                    except Exception as e:
                        logger.exception(str(e))
                        continue
                # otherwise, handle it as a normal resource
                else:
                    url = urljoin(self.url, img['src'])
                    with Resource(url, "image") as res:
                        res.download(self.netloc)
                del res
                gc.collect()
            # download scripts
            for script in soup.find_all("script", src=True):
                url = urljoin(self.url, script.attrs['src'])
                with Resource(url, "script") as res:
                    res.download(self.netloc)
            # download styles
            for link in soup.find_all("link", href=True, rel="stylesheet"):
                url = urljoin(self.url, link.attrs['href'])
                with Resource(url, "style") as res:
                    res.download(self.netloc)
        elif self.type == "image":
            # handle each image tool defined in IMAGE_TOOLS constant
            self._derive_resources()
        elif self.type == "style":
            # search for image URLs in the style sheet
            for img in CSS_IMG_REGEX.findall(self.content):
                img_url = img.strip(b"\'\"" if P3 else "\'\"").decode()
                url = urljoin(self.url, img_url)
                with Resource(url, "image") as res:
                    res.download(self.netloc)

    @staticmethod
    def pprint_req(request):
        """
        Pretty print method for debugging HTTP communication.
        """
        data = "\n\n    {}\n".format(request.body) \
                if request.method == "POST" else "\n"
        logger.debug("Sent request:\n    {} {}\n{}".format( \
            request.method, request.url,
            '\n'.join('    {}: {}'.format(k, v) \
                for k, v in sorted(request.headers.items()))) + data)

    @staticmethod
    def pprint_resp(response):
        """
        Pretty print method for debugging HTTP communication.
        """
        logger.debug("Received response:\n    {} {}\n{}\n"
            .format(response.status_code, response.reason,
            '\n'.join('    {}: {}'.format(k, v) \
                for k, v in sorted(response.headers.items()))))


# ----------------------- MAIN SECTION ----------------------
if __name__ == '__main__':
    global logger, session, args
    parser = argparse.ArgumentParser(
        prog=__file__.lstrip('./'), description=__doc__, add_help=False,
        usage="%(prog)s [OPTION]... PATTERN [URL]...",
        epilog="Please report bugs on GitHub: {}".format(__repository__),
        formatter_class=argparse.RawTextHelpFormatter)
    # argument groups are willingly the same as in grep
    regex = parser.add_argument_group("Regexp selection and interpretation")
    regex_pat = regex.add_mutually_exclusive_group()
    regex_pat.add_argument("-e", "--regexp", dest="pattern", default=None,
                           help="use PATTERN for matching")
    regex_pat.add_argument("-f", "--file", action=ArgCollectOption,
                           help="obtain PATTERN from FILE")
    regex_type = regex.add_mutually_exclusive_group()
    regex_type.add_argument("-E", "--extended-regexp", dest="grep_opts",
                            const="-E", action="append_const", help="PATTERN "
                            "is an extended regular expression (ERE)")
    regex_type.add_argument("-F", "--fixed-strings", dest="grep_opts",
                            const="-F", action="append_const", help="PATTERN "
                            "is a set of newline-separated fixed strings")
    regex_type.add_argument("-G", "--basic-regexp", dest="grep_opts",
                            const="-G", action="append_const",
                            help="PATTERN is a basic regular expression (BRE)")
    regex_type.add_argument("-P", "--perl-regexp", dest="grep_opts",
                            const="-P", action="append_const",
                            help="PATTERN is a Perl regular expression")
    regex.add_argument("-i", "--ignore-case", dest="grep_opts",
                       const="-i", action="append_const",
                       help="ignore case distinctions")
    regex.add_argument("-w", "--word-regexp", dest="grep_opts",
                       const="-w", action="append_const",
                       help="force PATTERN to match only whole words")
    regex.add_argument("-x", "--line-regexp", dest="grep_opts",
                       const="-x", action="append_const",
                       help="force PATTERN to match only whole lines")
    regex.add_argument("-z", "--null-data", dest="grep_opts",
                       const="-z", action="append_const",
                       help="a data line ends in 0 byte, not newline")
    misc = parser.add_argument_group("Miscellaneous")
    misc.add_argument("-s", "--no-messages", dest="grep_opts",
                      const="-s", action="append_const",
                      help="suppress error messages")
    misc.add_argument("-v", "--invert-match", dest="grep_opts",
                      const="-v", action="append_const",
                      help="select non-matching lines")
    misc.add_argument("-V", "--version", nargs=0, action=ArgVersion,
                      help="print version information and exit")
    misc.add_argument("--help", action="help",
                      help="display this help and exit")
    # ----- START new arguments -----
    misc.add_argument("--verbose", action="store_true", help="verbose mode")
    misc.add_argument("--keep-files", dest="keep", action="store_true",
                      help="keep temporary files in the temporary directory")
    misc.add_argument("--temp-dir", dest="tmp", default=TEMP_DIR,
                      help="define the temporary directory (default: {})"
                           .format(TEMP_DIR))
    # ----- END new arguments -----
    output = parser.add_argument_group("Output control")
    output.add_argument("-m", "--max-count", dest="m", metavar="NUM", type=int,
                        action=ArgCollectOption,
                        help="stop after NUM matches")
    output.add_argument("-b", "--byte-offset", dest="grep_opts",
                        const="-b", action="append_const",
                        help="print the byte offset with output lines")
    output.add_argument("-n", "--line-number", dest="grep_opts",
                        const="-n", action="append_const",
                        help="print line number with output lines")
    output.add_argument("--line-buffered", dest="grep_opts",
                        const="--line-buffered", action="append_const",
                        help="flush output on every line")
    output.add_argument("-H", "--with-filename", dest="grep_opts",
                        const="-H", action="append_const",
                        help="print the file name for each match")
    output.add_argument("-h", "--no-filename", dest="grep_opts",
                        const="-h", action="append_const",
                        help="suppress the file name prefix on output")
    output.add_argument("--label", dest="label", metavar="LABEL", type=str,
                        action=ArgCollectOption,
                        help="use LABEL as the standard input filename prefix")
    output.add_argument("-o", "--only-matching", dest="grep_opts",
                        const="-o", action="append_const",
                        help="show only the part of a line matching PATTERN")
    output.add_argument("-q", "--quiet", "--silent", dest="grep_opts",
                        const="-q", action="append_const",
                        help="suppress all normal output")
    output_type = output.add_mutually_exclusive_group()
    output_type.add_argument("--binary-files", dest="binary_files",
                             metavar="TYPE", choices=['binary', 'text',
                             'without-match'], default=None,
                             action=ArgCollectOption,
                             help="assume that binary files are TYPE;\nTYPE "
                                  "is 'binary', 'text', or 'without-match'")
    output_type.add_argument("-a", "--text", dest="grep_opts",
                             const="-a", action="append_const",
                             help="equivalent to --binary-files=text")
    output_type.add_argument("-I", dest="grep_opts",
                             const="-I", action="append_const",
                             help="equivalent to --binary-files=without-match")
    output_match = output.add_mutually_exclusive_group()
    output_match.add_argument("-L", "--files-without-match", dest="grep_opts",
                              const="-L", action="append_const", help="print "
                              "only names of FILEs containing no match")
    output_match.add_argument("-l", "--files-with-match", dest="grep_opts",
                              const="-l", action="append_const", help="print "
                              "only names of FILEs containing matches")
    output.add_argument("-c", "--count", dest="grep_opts",
                        const="-c", action="append_const",
                        help="print only a count of matching lines per FILE")
    output.add_argument("-T", "--initial-tab", dest="grep_opts",
                        const="-T", action="append_const",
                        help="make tabs line up (if needed)")
    output.add_argument("-Z", "--null", dest="grep_opts",
                        const="-Z", action="append_const",
                        help="print 0 byte after FILE name")
    context = parser.add_argument_group("Context control")
    context.add_argument("-B", "--before-context", dest="B", metavar="NUM",
                         type=int, action=ArgCollectOption,
                         help="print NUM lines of leading context")
    context.add_argument("-A", "--after-context", dest="A", metavar="NUM",
                         type=int, action=ArgCollectOption,
                         help="print NUM lines of trailing context")
    context.add_argument("-C", "--context", dest="C", metavar="NUM", type=int,
                         action=ArgCollectOption,
                         help="print NUM lines of output context")
    regex_pat.add_argument("pattern", metavar="PATTERN", nargs='?',
                           default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("url", metavar="URL", nargs='+', help=argparse.SUPPRESS)
    # ----- START new arguments -----
    web = parser.add_argument_group("Web options")
    web.add_argument("--external-resources", dest="same_origin",
                     action="store_false",
                     help="also download non-same-origin resources")
    web.add_argument("--cookie", action=GetHeader,
                     help="use a session cookie in the HTTP headers")
    web.add_argument("--referer", action=GetHeader,
                     help="provide the referer in the HTTP headers")
    web = parser.add_argument_group("Proxy settings (by default, system proxy "
                                    "settings are used)")
    web.add_argument("-d", "--disable-proxy", dest="proxy",
                     action="store_false", help="manually disable proxy")
    web.add_argument("--http-proxy", dest="http", action=ProxySetting,
                     help="manually set the HTTP proxy")
    web.add_argument("--https-proxy", dest="https", action=ProxySetting,
                     help="manually set the HTTPS proxy")
    # ----- END new arguments -----
    args = parser.parse_args()
    if args.pattern is None:
        parser.error("no pattern provided")
    args.pattern = "'{}'".format(args.pattern.strip("\'\""))
    if not hasattr(args, "headers"):
        args.headers = {}
    # configure logging and get the root logger
    args.verbose = [logging.INFO, logging.DEBUG][args.verbose]
    logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT,
                        level=args.verbose)
    logger = logging.getLogger()
    if colored_logs_present:
        coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT
        coloredlogs.DEFAULT_DATE_FORMAT = DATE_FORMAT
        coloredlogs.install(args.verbose)
    # attach tools and preprocessors to args
    for item in ['tools', 'preprocessors']:
        for res in RESOURCE_TYPES:
            attr = '{}_{}'.format(res, item).upper()
            if attr in globals():
                setattr(args, attr.lower(), [(k, v[1]) for k, v in \
                        globals()[attr].items() if __installed(k, v[0], v[2])])
    # running the main stuff
    try:
        session = requests.Session()
        logger.debug("Creating temporary folder {}".format(args.tmp))
        if not exists(args.tmp):
             os.makedirs(args.tmp)
        done = []
        for url in args.url:
            if url in done:
                continue
            logger.debug("Downloading page {} and its associated resources"
                         .format(url))
            with Resource(url) as page:
                page.download()
            done.append(url)
    except Exception as e:
        logger.exception("Unexpected error: {}".format(str(e)))
        __exit_handler(code=1)
    # gracefully close after running the main stuff
    __exit_handler()

