# How it works

## Overall design

WebGrep processes the input resource by resource, meaning that it first greps the Web page, then downloads and greps resource by resource, so that it behaves just like the normal `grep` tool. For this purpose, files are downloaded and saved to a temporary folder (`/tmp/webgrep` by default, see `--temp-dir`).

In terms of a class diagram, it gives a `Resource` class that recursively composes other instances, as depicted in the following figure:

![Resource class](img/webgrep-resource.png)

-----

## Understanding the workflow

When entering the workflow, WebGrep creates a new `Resource` instance with the input URL. Note that this URL can be this of a Web page, an image or whatever.

This then implies two processes:

1. **Create**: Creating and grepping the resource.

    ![Create process](img/webgrep-create.png)

2. **Handle**: Handling the content of the resource instance, that is, deriving new resources from raw data inside the content and parsing it for links to other resources.

    ![Handle process](img/webgrep-handle.png)

Thanks to the first process, **Create**, the resource is downloaded or loaded from cache, preprocessed and then grepped before giving the hand to the second process. In the *Create* process, *Preprocessors* are functions that transform the content of the resource before it is grepped. It makes the grepping process more consistent as, for example, if an obfuscated minified JavaScript is grepped on a given keyword, it is less likely to find matches or, if so, due to the minification, it returns the entire script.

Thanks to the second process, **Handle**, the recursion is achieved as, after having been grepped, the content of the resource is parsed for discovering new resources and handling them one at a time.

-----

## Resource handlers

| Resource type | Handler                                        | Kind         |
|---------------|------------------------------------------------|--------------|
| Web page      | inline scripts and styles extraction           | preprocessor |
| Image         | EXIF metadata (`exiftool`)                     | tool         |
| Image         | steganography, empty passphrase (`steghide`)   | tool         |
| Image         | strings (`strings`)                            | tool         |
| Image         | OCR (`tesseract`)                              | tool         |
| Script        | beautifying and deobfuscation (`jsbeautifier`) | preprocessor |
| Style sheet   | unminifying (regular expressions)              | preprocessor |

The images referenced in the style sheets are also processed. See [Extending WebGrep](extending.md) for adding handlers.

-----

## Grepping

Each resource is grepped by running `grep` with the options given to `webgrep`, in the temporary folder. The pattern and the file name are passed to `grep` as separate arguments, never through a shell: the file names are derived from URLs that the Web page controls.
