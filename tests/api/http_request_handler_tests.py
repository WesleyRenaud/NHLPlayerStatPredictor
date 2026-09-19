from __future__ import annotations

import threading
from urllib.error import HTTPError
from urllib.request import urlopen

from api.http_request_handler import HttpRequestHandler
from api.threaded_http_server import ThreadedHttpServer


def Test_DoGet_TestUnknownPath_ExpectNotFound() -> None:
   server = ThreadedHttpServer( ( '127.0.0.1', 0 ), HttpRequestHandler )
   thread = threading.Thread( target=server.serve_forever, daemon=True )
   thread.start()

   try:
      port = server.server_address[ 1 ]

      try:
         urlopen( f'http://127.0.0.1:{ port }/', timeout=5 )
         raise AssertionError( 'Expected HTTP 404' )
      except HTTPError as error:
         assert error.code == 404
   finally:
      server.shutdown()
      server.server_close()
