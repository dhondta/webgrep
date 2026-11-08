# Extending WebGrep

The handlers are defined in the `HANDLERS SECTION` of [`src/webgrep/__main__.py`](https://github.com/dhondta/webgrep/blob/main/src/webgrep/__main__.py). There are two kinds of handlers:

- **Preprocessors**, applied on downloaded resources ; these *replace* the content of the resource.
- **Tools**, applied after the resource is downloaded and processed ; these *derive* new resources.

-----

## Adding preprocessors

The preprocessors are defined in constants (always named in uppercase), according to the following convention:

```
[RESOURCE TYPE]_PREPROCESSORS
```

The related constant is a dictionary with the following structure:

- **Key** = Preprocessor name
- **Value** = tuple(*type*, *triggering function*, *unavailability error message*)

The followings are valid types:

- `binary`: a call to the help/usage message of the binary is performed to check for its existence ; if it fails, the *unavailability error message* is displayed.
- `function`: no check ; the function is to be embedded in WebGrep's code (as no check is performed, the *unavailability error message* can simply be `None`).
- `module`: an import is performed to check for its existence ; if it fails, the *unavailability error message* is displayed.

The *triggering function* has to take a `Resource` instance in input and to return a resource content (NOT the `Resource` instance !). This overwrites the content of the base resource, but this design is made to comply with this of the tools (see next section).

!!! note "Example: JSBeautifier"
    This applies to scripts ; we are therefore working on the `SCRIPT_PREPROCESSORS` and the key for the dictionary is `jsbeautifier`.

    [`jsbeautifier`](https://pypi.org/project/jsbeautifier/) is a Python module that *beautifies, unpacks or deobfuscates JavaScript*, *handling popular online obfuscators*. This is thus a `module` and the *unavailability error message* can simply be "*Python library required for deobfuscating Javascript ; consider running 'pip install jsbeautifier'*".

    The *triggering function* is then simply a lambda calling `jsbeautifier`, for example:

    ```python
    lambda resource: jsbeautifier.beautify(resource.content)
    ```

    The resulting tuple to be set as the value of the `jsbeautifier` key in the `SCRIPT_PREPROCESSORS` dictionary is thus:

    ```python
    ('module', lambda r: b(jsbeautifier.beautify(s(r.content))),
        "Python library required for deobfuscating...")
    ```

-----

## Adding tools

Just like the preprocessors, tools are defined in constants (always named in uppercase), according to the following convention:

```
[RESOURCE TYPE]_TOOLS
```

Once again, just like for the preprocessors, the related constant is a dictionary with the following structure:

- **Key** = Tool name
- **Value** = tuple(*type*, *triggering function*, *unavailability error message*)

The types are exactly the same as for the preprocessors (see before).

The *triggering function* has to take a `Resource` instance in input and to return a resource content (NOT the `Resource` instance !), as this sets the content of the NEW resource created by the tool, named after the base resource with the name of the tool appended.

!!! note "Example: Strings"
    This applies to images ; we are therefore working on the `IMAGE_TOOLS` and the key for the dictionary is `strings` (which is appended to the filename of the resulting resource when written to the temporary folder for grepping).

    The well-known `strings` tool does not need any introduction. This is a `binary` and the *unavailability error message* can simply be "*Binary required for getting strings from downloaded files ; consider running 'sudo apt-get install binutils'*".

    The *triggering function* can be `get_cmd("strings")`, which runs the tool on the resource in a subprocess.

    The resulting tuple to be set as the value of the `strings` key in the `IMAGE_TOOLS` dictionary is thus:

    ```python
    ('binary', get_cmd("strings"),
        "Binary required for getting strings from downloaded files ; ...")
    ```

!!! warning "Running external tools"
    Pass the command as a list of arguments, never through a shell (`shell=True`): the file names are derived from URLs that the Web page controls.
