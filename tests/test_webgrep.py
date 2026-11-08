# -*- coding: UTF-8 -*-
import base64
import functools
import re
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest

from webgrep import __version__
from webgrep.__main__ import main


# 1x1 transparent PNG
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
PAGE = """<html>
<head>
  <title>Test page</title>
  <link rel="stylesheet" href="style.css">
  <script src="script.js"></script>
  <script>var inline_flag = "FLAG-INLINE-SCRIPT";</script>
  <style>.inline { content: "FLAG-INLINE-STYLE"; }</style>
</head>
<body>
  <p>Welcome to the FLAG-PAGE test</p>
  <img src="img.png">
  <img src="data:image/png;base64,{png}">
  <img src="missing.png">
</body>
</html>
"""
SCRIPT = 'function f(){var a="FLAG-SCRIPT";return a}'
STYLE = ".a{color:red;background:url('bg.png')}.b{content:\"FLAG-STYLE\"}" + ".c{margin:0}" * 30


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    root = tmp_path_factory.mktemp("site")
    (root / "index.html").write_text(PAGE.replace("{png}", base64.b64encode(PNG).decode()))
    (root / "script.js").write_text(SCRIPT)
    (root / "style.css").write_text(STYLE)
    (root / "img.png").write_bytes(PNG)
    (root / "bg.png").write_bytes(PNG)
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:{}/".format(server.server_address[1])
    server.shutdown()


def run(monkeypatch, capsys, tmp_path, *argv):
    monkeypatch.setattr(sys, "argv", ["webgrep", "-d", "--temp-dir", str(tmp_path / "webgrep")] + list(argv))
    with pytest.raises(SystemExit) as e:
        main()
    # strip grep's color codes
    return e.value.code, re.sub(r"\x1b\[[0-9;]*[mK]", "", capsys.readouterr().out)


def test_version(monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "-V")
    assert code == 0
    assert "webgrep {}".format(__version__) in out


def test_no_pattern(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["webgrep", "-e"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 2


def test_page_only(site, monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "FLAG", site)
    assert code == 0
    assert "FLAG-PAGE" in out
    # resources are not grepped by default
    assert "FLAG-SCRIPT" not in out
    assert "FLAG-STYLE\"" not in out
    # the temporary folder is removed without --keep-files
    assert not (tmp_path / "webgrep").exists()


def test_inline_items(site, monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "FLAG-INLINE", site)
    assert code == 0
    assert "FLAG-INLINE-SCRIPT" in out
    assert "FLAG-INLINE-STYLE" in out


def test_local_resources(site, monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "-r", "--verbose", "-o", "FLAG-[A-Z]*", site)
    assert code == 0
    for flag in ["FLAG-PAGE", "FLAG-SCRIPT", "FLAG-STYLE"]:
        assert flag in out


def test_all_resources_and_headers(site, monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "-R", "-i", "--include-headers", "--cookie", "a=b",
                    "--referer", site, "content-type", site)
    assert code == 0
    assert "Content-type" in out or "Content-Type" in out


def test_regexp_option(site, monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "-E", "-e", "FLAG-(PAGE|NONE)", "-m", "1", site)
    assert code == 0
    assert "FLAG-PAGE" in out


def test_shell_metacharacters_not_interpreted(site, monkeypatch, capsys, tmp_path):
    # the pattern and file names are passed to grep as arguments, never through a shell
    code, out = run(monkeypatch, capsys, tmp_path, "FLAG$(echo -PAGE)", site)
    assert code == 0
    assert "FLAG-PAGE" not in out


def test_keep_files(site, monkeypatch, capsys, tmp_path):
    code, out = run(monkeypatch, capsys, tmp_path, "--keep-files", "-r", "FLAG-SCRIPT", site)
    assert code == 0
    assert "FLAG-SCRIPT" in out
    assert (tmp_path / "webgrep" / "cache.json").exists()


def test_local_file(monkeypatch, capsys, tmp_path):
    page = tmp_path / "page.html"
    page.write_text("<html><body>FLAG-LOCAL</body></html>")
    code, out = run(monkeypatch, capsys, tmp_path, "FLAG", page.as_uri())
    assert code == 0
    assert "FLAG-LOCAL" in out
