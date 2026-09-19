from __future__ import annotations

from http.server import BaseHTTPRequestHandler


class HttpRequestHandler( BaseHTTPRequestHandler ):
   def do_GET( self ) -> None:
      self.send_error( 404, 'Not Found' )


   def do_POST( self ) -> None:
      self.send_error( 404, 'Not Found' )
