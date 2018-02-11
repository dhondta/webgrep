## Introduction

The WebGrep tool aims to grep a Web page and, if required, its related resources but with some additional features for preprocessing and deriving new resources.

For this purpose, WebGrep :

- Relies on the common `grep` tool.
- Mimics every option of this tool except `-r` (recursive) as, by design, WebGrep is not aimed to crawl Web pages.
- Gets page-related resources like images, scripts and style sheets.
- Holds extra features for applying transformations on these resources in order to get more relevant results.


Quick example:

``` sh
$ webgrep Welcome https://github.com
      Welcome home, <br>developers

```

-----

## System Requirements

- **Platform**: Linux
- **Prerequisite**: `grep` tool
- **Python**: 2 or 3

-----

## Installation

This tool is available on [PyPi](https://pypi.python.org/pypi/webgrep-tool/) (DO NOT confuse with this [package](https://pypi.python.org/pypi/webgrep/), this has nothing to do with the WebGrep tool) and can be simply installed using Pip via `sudo pip install webgrep-tool`.

-----

## Rationale

During multiple scenario's in my professional life, I required to search for keywords in the sources of various Web pages but also in the related resources like scripts and images. After parsing some projects on GitHub, I realized there was no consistent tool for handling Grep-like functionality for the Web pages.

Moreover, taking into account that there can be hidden/obfuscated data/stuffs in Web pages or their related resources (e.g. an obfuscated JavaScript), I wanted a tool that could integrate such features extensively while keeping a self-contained characteristic for easy integration into the operating system as a `/usr/bin/` tool.

It can easilly be shown that lots of Web servers are using minified CSS or obfuscated minified JavaScripts and that grepping such resources would be useless because of their nature. Therefore, the required tool has to be able to transform resources as much as possible in order to make them greppable.

-----

## Definitions

In the remainder of this documentation, the following terms are used:

- **Resource**: The main entity ; can be a Web page, an image, a script, a style sheet or anything else.

- **Preprocessors**: These are transformations applied based on the resource type ; can be a JavaScript deobfuscator, a CSS unminifier, ...

- **Tools**: These are alternative tools that can be used to derive new resources based on the resource type ; can be `exiftool` or `tesseract-ocr` for an image, ...
