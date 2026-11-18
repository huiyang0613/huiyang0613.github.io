#!/usr/bin/env python3
"""Serve a local preview; rebuild changed content when the page is refreshed."""
import argparse
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import sys
import threading
import runpy

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

lock = threading.Lock()
last_signature = None


def rebuild():
    global last_signature
    sources = [ROOT / "_data/profile.json", ROOT / "templates/index.html", ROOT / "assets/icons.svg", Path(__file__).with_name("build.py")]
    sources.extend(sorted((ROOT / "_publications").glob("*.json")))
    signature = tuple((str(p), p.stat().st_mtime_ns) for p in sources)
    with lock:
        if signature != last_signature:
            runpy.run_path(str(ROOT / "scripts/build.py"))["build"]()
            last_signature = signature


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] in {"/", "/index.html"}:
            try:
                rebuild()
            except Exception as exc:
                self.send_error(500, f"Build failed: {exc}")
                return
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    rebuild()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), functools.partial(Handler, directory=str(ROOT)))
    print(f"Local: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
