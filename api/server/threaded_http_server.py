from __future__ import annotations

from http.server import ThreadingHTTPServer


class ThreadedHttpServer( ThreadingHTTPServer ):
   request_queue_size = 128
