from __future__ import annotations

from .http_request_handler import HttpRequestHandler
from .threaded_http_server import ThreadedHttpServer


class ServerRunner():
   DEFAULT_PORT = 9000

   @classmethod
   def run( cls, port: int = DEFAULT_PORT ) -> None:
      httpd = ThreadedHttpServer( ( 'localhost', port ), HttpRequestHandler )
      print( 'Server listening on port: ', port )
      httpd.serve_forever()
