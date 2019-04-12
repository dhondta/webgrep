[![PyPi](https://img.shields.io/pypi/v/webgrep-tool.svg)](https://pypi.python.org/pypi/webgrep-tool/)
![Platform](https://img.shields.io/badge/platform-linux-yellow.svg)
[![Read The Docs](https://readthedocs.org/projects/webgrep/badge/?version=latest)](http://webgrep.readthedocs.io/en/latest/?badge=latest)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/webgrep/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/webgrep?targetFile=requirements.txt)
[![Requirements Status](https://requires.io/github/dhondta/webgrep/requirements.svg?branch=master)](https://requires.io/github/dhondta/webgrep/requirements/?branch=master)
[![License](https://img.shields.io/pypi/l/webgrep-tool.svg)](https://pypi.python.org/pypi/webgrep-tool/)


## Table of Contents

   * [Introduction](#introduction)
   * [System Requirements](#system-requirements)
   * [Installation](#installation)
   * [Quick Start](#quick-start)
   * [Design Principles](#design-principles)
   * [Resource *Handlers*](#resource-handlers)
   * [Issues management](#issues-management)


## Introduction

This self-contained tool relies on the well-known `grep` tool for grepping Web pages. It binds nearly every option of the original tool and also provides additional features like deobfuscating Javascript or appyling OCR on images before grepping downloaded resources.


## System Requirements

This script was tested on an Ubuntu 16.04 with Python 2.7 and Python 3.5.

Its Python logic mostly uses standard built-in modules but also some particular tool- or preprocessor-related modules. It makes calls to `grep`.


## Installation

 ```session
 $ sudo pip install webgrep-tool
 ```

 > **Behind a proxy ?**
 > 
 > Do not forget to add option `--proxy=http://[user]:[pwd]@[host]:[port]` to your pip command.


## Quick Start

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


## Design principles:

- Maximum use of Python-builtin modules.
- For non-standard imports ;
  - trigger exit if not installed and display the command for installing these
  - do not trigger exit if not installed, display the command for installing these and continue execution without the related functionality
- No modularity (principle of self-contained tool) so that it can simply be copied in `/usr/bin` with dependencies other than the non-standard imports.


## Resource *Handlers*

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


## Issues management

Please [open an Issue](https://github.com/dhondta/webgrep/issues/new) if you want to contribute or submit suggestions. 

If you want to build and submit new handlers, please open a Pull Request.
