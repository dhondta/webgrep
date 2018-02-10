from pip.download import PipSession as Pip
from pip.req import parse_requirements as parse
from setuptools import setup


setup(
  name = "webgrep-tool",
  version = "1.6",
  license = "GPLv3",
  description = "Web page Grep-like tool with additional features like JS deobfuscation and easy extensibility",
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  url = "https://github.com/dhondta/webgrep",
  keywords = ["grep", "webpage", "js-deobfuscator", "css-unminifier",
              "exif-metadata", "ocr"],
  scripts = ["webgrep"],
  python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
  install_requires=[str(i).split("(", 1)[0].strip() for i in \
                    parse("requirements.txt", session=Pip())],
)
