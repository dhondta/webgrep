## Overview

Grepping with WebGrep can be performed using the following methodology:

1. Only grep the Web page:

        $ webgrep keyword http://example.com

2. Then grep the Web page and its same-origin resources:

        $ webgrep -r keyword http://example.com

3. Now grep the Web page with all its related resources:

        $ webgrep -R keyword http://example.com

4. If relevant, also grep the HTTP headers (e.g. for inspecting a cookie):

        $ webgrep cookie http://example.com --include-headers

-----

## Overall Design

WebGrep will process the input resource by resource, meaning that it will first grep on the Web page, then download and grep resource by resource, so that it behaves just like the normal `grep` tool. For this purpose, files will be downloaded and saved to a temporary folder (`/tmp/webgrep` by default, can be tuned ; see the help of the tool).

In term of a class diagram, it gives a `Resource` class that recursively composes other instances, like depicted in the following figure:

![](imgs/webgrep-resource.png)

For a deeper understanding on how WebGrep works with this class, please see the next section.
