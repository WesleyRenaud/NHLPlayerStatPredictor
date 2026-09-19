from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler
import threading
from typing import Any
from urllib.request import urlopen

from api.shared.enums.position import Position
from api.threaded_http_server import ThreadedHttpServer


PARALLEL_GET_COUNT = 80


class _OkHandler( BaseHTTPRequestHandler ):
   def do_GET( self ) -> None:
      self.send_response( 200 )
      self.send_header( 'Content-type', 'text/plain' )
      self.end_headers()
      self.wfile.write( b'ok' )


   def log_message( self, format: str, *args: Any ) -> None:
      return


def Test_RequestQueueSize_TestClassDefault_ExpectLargerThanFive() -> None:
   assert ThreadedHttpServer.request_queue_size > 5


def Test_ServeForever_TestParallelGets_ExpectAllSucceed() -> None:
   server = ThreadedHttpServer( ( '127.0.0.1', 0 ), _OkHandler )
   thread = threading.Thread( target=server.serve_forever, daemon=True )
   thread.start()

   try:
      port = server.server_address[ Position.SECOND ]
      url = f'http://127.0.0.1:{ port }/'

      def fetch() -> int:
         with urlopen( url, timeout=5 ) as response:
            return response.status

      with ThreadPoolExecutor( max_workers=PARALLEL_GET_COUNT ) as executor:
         statuses = list( executor.map( lambda _: fetch(), range( PARALLEL_GET_COUNT ) ) )

      assert statuses == [ 200 ] * PARALLEL_GET_COUNT
   finally:
      server.shutdown()
      server.server_close()
