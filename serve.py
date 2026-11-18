# The dev server: Python's built-in file server, but every reply carries Cache-Control: no-store,
# which tells the browser to keep no copy. Without it, a browser may reuse an old copy of a file
# it fetched before, and a phone has no easy way to clear its cache.
# Usage, from the repo root: uv run --no-project python serve.py [port] [folder]
# (defaults: 8000 and the current folder). Ctrl+C stops it.
import functools
import http.server
import sys


class NoStoreHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):   # runs once per reply, errors included, just before the body
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
folder = sys.argv[2] if len(sys.argv) > 2 else '.'
handler = functools.partial(NoStoreHandler, directory=folder)   # serve folder, not the current one
print(f'Serving {folder} at http://localhost:{port}/ with caching off; Ctrl+C stops it')
try:
    http.server.ThreadingHTTPServer(('', port), handler).serve_forever()   # '': every network interface
except KeyboardInterrupt:
    pass
