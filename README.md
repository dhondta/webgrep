<p align="center"><img src="https://github.com/dhondta/webgrep/raw/master/doc/imgs/logo.png"></p>
<h1 align="center">WebGrep <a href="https://twitter.com/intent/tweet?text=WebGrep%20-%20Grep%20Web%20pages%20and%20their%20resources%20using%20JS%20deobfuscation,%20CSS%20unminifying%20and%20image%20OCR.%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fwebgrep%0D%0A&hashtags=python,grep,webpage,ocr,tesseract,cssunminifier,jsdeobfuscation,jsbeautifier,ctftools"><img src="https://img.shields.io/badge/Tweet--lightgrey?logo=twitter&style=social" alt="Tweet" height="20"/></a></h1>
<h3 align="center">Grep Web pages and their resources.</h3>

[![PyPi](https://img.shields.io/pypi/v/webgrep-tool.svg)](https://pypi.python.org/pypi/webgrep-tool/)
![Platform](https://img.shields.io/badge/platform-linux-yellow.svg)
[![Read The Docs](https://readthedocs.org/projects/webgrep/badge/?version=latest)](http://webgrep.readthedocs.io/en/latest/?badge=latest)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/webgrep/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/webgrep?targetFile=requirements.txt)
[![Requirements Status](https://requires.io/github/dhondta/webgrep/requirements.svg?branch=master)](https://requires.io/github/dhondta/webgrep/requirements/?branch=master)
[![License](https://img.shields.io/pypi/l/webgrep-tool.svg)](https://pypi.python.org/pypi/webgrep-tool/)


This self-contained tool relies on the well-known [`grep`](https://linux.die.net/man/1/grep) tool for grepping Web pages. It binds nearly every option of the original tool and also provides additional features like deobfuscating Javascript or appyling OCR on images before grepping downloaded resources.

```session
$ pip install webgrep-tool
```

## :fast_forward:  Quick Start

1. Help

 ```session
 $ webgrep --help
usage: webgrep [OPTION]... PATTERN [URL]...

Search for PATTERN in each input URL and its related resources
 (images, scripts and style sheets).
By default,
 - resources are NOT downloaded
 - response HTTP headers are NOT included in grepping ; use '--include-headers'
 - PATTERN is a basic regular expression (BRE) ; use '-E' for extended (ERE)
Important note: webgrep does not handle recursion (in other words, it does not
                spider additional web pages).
Examples:
  webgrep example http://www.example.com     # will only grep on HTML code
  webgrep -r example http://www.example.com  # will only grep on LOCAL images, ...
  webgrep -R example http://www.example.com  # will only grep on ALL images, ...

Regexp selection and interpretation:
  -e REGEXP, --regexp REGEXP
                        use PATTERN for matching
  -f FILE, --file FILE  obtain PATTERN from FILE
  -E, --extended-regexp
                        PATTERN is an extended regular expression (ERE)
  -F, --fixed-strings   PATTERN is a set of newline-separated fixed strings
  -G, --basic-regexp    PATTERN is a basic regular expression (BRE)
  -P, --perl-regexp     PATTERN is a Perl regular expression
  -i, --ignore-case     ignore case distinctions
  -w, --word-regexp     force PATTERN to match only whole words
  -x, --line-regexp     force PATTERN to match only whole lines
  -z, --null-data       a data line ends in 0 byte, not newline

Miscellaneous:
  -s, --no-messages     suppress error messages
  -v, --invert-match    select non-matching lines
  -V, --version         print version information and exit
  --help                display this help and exit
  --verbose             verbose mode
  --keep-files          keep temporary files in the temporary directory
  --temp-dir TMP        define the temporary directory (default: /tmp/webgrep)

Output control:
  -m NUM, --max-count NUM
                        stop after NUM matches
  -b, --byte-offset     print the byte offset with output lines
  -n, --line-number     print line number with output lines
  --line-buffered       flush output on every line
  -H, --with-filename   print the file name for each match
  -h, --no-filename     suppress the file name prefix on output
  --label LABEL         use LABEL as the standard input filename prefix
  -o, --only-matching   show only the part of a line matching PATTERN
  -q, --quiet, --silent
                        suppress all normal output
  --binary-files TYPE   assume that binary files are TYPE;
                        TYPE is 'binary', 'text', or 'without-match'
  -a, --text            equivalent to --binary-files=text
  -I                    equivalent to --binary-files=without-match
  -L, --files-without-match
                        print only names of FILEs containing no match
  -l, --files-with-match
                        print only names of FILEs containing matches
  -c, --count           print only a count of matching lines per FILE
  -T, --initial-tab     make tabs line up (if needed)
  -Z, --null            print 0 byte after FILE name

Context control:
  -B NUM, --before-context NUM
                        print NUM lines of leading context
  -A NUM, --after-context NUM
                        print NUM lines of trailing context
  -C NUM, --context NUM
                        print NUM lines of output context

Web options:
  -r, --local-resources
                        also grep local resources (same-origin)
  -R, --all-resources   also grep all resources (even non-same-origin)
  --include-headers     also grep HTTP headers
  --cookie COOKIE       use a session cookie in the HTTP headers
  --referer REFERER     provide the referer in the HTTP headers

Proxy settings (by default, system proxy settings are used):
  -d, --disable-proxy   manually disable proxy
  --http-proxy HTTP     manually set the HTTP proxy
  --https-proxy HTTPS   manually set the HTTPS proxy

Please report bugs on GitHub: https://github.com/dhondta/webgrep

 ```
 
2. Example

 ```session
 $ ./webgrep -R Welcome https://github.com
       Welcome home, <br>developers
 
 ```


## :pushpin: Resource *Handlers*

**Definitions**:
- *Resource* (what is being processed):  Web page, images, Javascript, CSS
- *Handler* (how a resource is processed): CSS unminifying, OCR, deobfuscation, EXIF data retrieval, ...

The handlers are defined in the `# --...-- HANDLERS SECTION --...--` of the code. Currently available handlers :
1. Images
  - EXIF: using `exiftool`
  - Steganography: using `steghide` (with a blank password)
  - Strings: using `strings`
  - OCR: using `tesseract`
2. Scripts
  - Javascript beautifying and deobfuscation: using `jsbeautifier`
3. Styles
  - Unminifying: using regular expressions

Note: images found in the CSS files are also processed.


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/webgrep](https://reporoster.com/stars/dark/dhondta/webgrep)](https://github.com/dhondta/webgrep/stargazers)

[![Forkers repo roster for @dhondta/webgrep](https://reporoster.com/forks/dark/dhondta/webgrep)](https://github.com/dhondta/webgrep/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
