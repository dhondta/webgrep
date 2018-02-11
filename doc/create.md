## Understanding the Workflow

When entering the workflow, WebGrep of course creates a new `Resource` instance with the input URL. Note that this URL can be this of a Web page or an image or whatever.

This then implies two processes:

1. **Create**: Creating and grepping the resource.

    ![](imgs/webgrep-create.png)
    


2. **Handle**: Handling resource instance's content, that is, deriving new resources from raw data inside the content and parsing this for links to other resources.

    ![](imgs/webgrep-handle.png)
    


Thanks to the first process, **Create**, the resource is downloaded or loaded from cache, preprocessed and then grepped before giving the hand to the second process. In the *Create* process, *Preprocessors* are functions that will transform resource's content before being grepped. It allows to make the grepping process more consistent as, for example, if an obfuscated minified JavaScript is grepped on a given keyword, it is less likely to find matches or if so, due to the minification, it will return the entire script.

Thanks to the second process, **Handle**, the recursion is achieved as, after having been grepped, resource's content is parsed for discovering new resources and handling them one at a time.


-----

## Adding Preprocessors

The preprocessors are defined in constants (always named in uppercase), according to the following convention:

```
[RESOURCE TYPE]_PREPROCESSORS
```

The related constant is a dictionary with the following structure:

- **Key** = Preprocessor name
- **Value** = tuple(*type*, *triggering function*, *unavailability error message*)

The followings are valid types:

- `binary`: a call to binary's help/usage message is performed to check for its existence ; if fail, the *unavailability error message* is displayed.
- `function`: no check ; the function is to be embedded in WebGrep's script (as no check is performed, the *unavailability error message* can simply be `None`).
- `module`: an import is performed to check for its existence ; if fail, the *unavailability error message* is displayed.

The *triggering function* has to take a `Resource` instance in input and to return a resource content (NOT the `Resource` instance !). This will overwrite base resource's content but this design is made to comply with this of the tools (see next subsection).

!!! note "Example: JSBeautifier"
    This applies to scripts ; we are therefore working on the `SCRIPT_PREPROCESSORS` and the key for the dictionary will be `jsbeautifier`.
    
    [`jsbeautifier`](https://pypi.python.org/pypi/jsbeautifier) is a Python module that *beautify, unpack or deobfuscate JavaScript*, *handling popular online obfuscators*. This is thus a `module` and the *unavailability error message* can simply be "*Python library required for deobfuscating Javascript ; consider running 'sudo pip install jsbeautifier'*".
    
    The *triggering function* is then simply a lazy function calling `jsbeautifier` as, for example:
    
        ::python
        lambda resource: jsbeautifier.beautify(resource.content)
    
    The resulting tuple to be set as the value corresponding to the `jsbeautifier` key in the `SCRIPT_PREPROCESSORS` dictionary is thus:
    
        ::python
        ('module', lambda r: jsbeautifier.jsbeautify(r.content),
            "Python library required for deobfuscating...")

-----

## Adding Tools

Just like for the preprocessors, tools are defined in constants (always named in uppercase), according to the following convention:

```
[RESOURCE TYPE]_TOOLS
```

Once again, just like for the preprocessors, the related constant is a dictionary with the following structure:

- **Key** = Tool name
- **Value** = tuple(*type*, *triggering function*, *unavailability error message*)

The types are exactly the same as for the preprocessors (see before).

The *triggering function* has to take a `Resource` instance in input and to return a resource content (NOT the `Resource` instance !), as this will set the content of the NEW resource created by the tool and named using base resource's name while appending the name of the tool applied.

!!! note "Example: Strings"
    This applies to images ; we are therefore working on the `IMAGE_TOOLS` and the key for the dictionary will be `strings` (which will be appended to the filename of the resulting resource when written to a temporary folder for grepping).
    
    The well-known `strings` tool doesn't need any introduction. This is a `binary` and the *unavailability error message* (while a bit useless, I think, as it is normally present on most Linux today...) can simply be "*Binary required for getting strings from downloaded files ; consider running 'sudo apt-get install strings'*".
    
    The *triggering function* is now a custom calling function or can also be `get_cmd("strings")` which will care for calling a subprocess applying on the resource.
        
    The resulting tuple to be set as the value corresponding to the `scripts` key in the `IMAGE_TOOLS` dictionary is thus:
    
        ::python
        ('binary', get_cmd("strings"),
            "Binary required for getting strings from downloaded files ; ...")
