# `webgrep`

```console
$ webgrep [OPTION]... PATTERN [URL]...
```

`webgrep` downloads each URL, saves it to a temporary folder (`/tmp/webgrep` by default, see `--temp-dir`) and greps it with the `grep` tool. With `-r` or `-R`, it also downloads and greps the images, scripts and style sheets of the page, after preprocessing them (see [How it works](../internals.md)).

## Methodology

1. Only grep the Web page:

    ```console
    $ webgrep keyword http://example.com
    ```

2. Then grep the Web page and its same-origin resources:

    ```console
    $ webgrep -r keyword http://example.com
    ```

3. Now grep the Web page with all its related resources:

    ```console
    $ webgrep -R keyword http://example.com
    ```

4. If relevant, also grep the HTTP headers (e.g. for inspecting a cookie):

    ```console
    $ webgrep cookie http://example.com --include-headers
    ```

!!! tip "Re-grepping without downloading again"
    With `--keep-files`, the downloaded resources are kept in the temporary folder with a cache, so that a next run with `--keep-files` greps them for another pattern without downloading them again.

## Options

```console
$ webgrep --help
usage: webgrep [OPTION]... PATTERN [URL]...

Search for PATTERN in each input URL and its related resources (images, scripts and style sheets).
By default,
 - resources are NOT downloaded
 - response HTTP headers are NOT included in grepping ; use '--include-headers'
 - PATTERN is a basic regular expression (BRE) ; use '-E' for extended (ERE)
Important note: webgrep does not handle recursion (in other words, it does not spider additional web pages).
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

Please report bugs on GitHub: https://github.com/dhondta/webgrep/issues/new
```
