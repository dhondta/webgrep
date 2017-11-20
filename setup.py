from setuptools import setup


setup(
  name = "webgrep",
  version = "1.0",
  license = "GPLv3",
  description = "Web page Grep-like tool with additional features like JS deobfuscation and easy extensibility",
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  url = "https://github.com/dhondta/webgrep",
  keywords = ["grep", "webpage", "js-deobfuscator", "css-unminifier",
              "exif-metadata", "ocr"],
  scripts = ["webgrep"],
  python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
)
