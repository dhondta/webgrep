# Installation

## System requirements

- **Platform**: Linux
- **Prerequisite**: the `grep` tool
- **Python**: 3.10 or later

## Installing WebGrep

WebGrep is available on [PyPI](https://pypi.org/project/webgrep-tool/) as `webgrep-tool` (do not confuse it with the [`webgrep`](https://pypi.org/project/webgrep/) package, which has nothing to do with this tool):

```console
$ pip install webgrep-tool
```

This installs the `webgrep` command.

## Optional tools

The image handlers rely on external tools. WebGrep works without them: a missing tool is skipped with a warning (use `-s` to silence it).

| Tool        | Used for                                   | Debian/Ubuntu package    |
|-------------|--------------------------------------------|--------------------------|
| `exiftool`  | getting EXIF metadata from images          | `libimage-exiftool-perl` |
| `steghide`  | extracting hidden data (empty passphrase)  | `steghide`               |
| `strings`   | getting printable strings from images      | `binutils`               |
| `tesseract` | applying OCR on images                     | `tesseract-ocr`          |

```console
$ sudo apt-get install libimage-exiftool-perl steghide binutils tesseract-ocr
```
