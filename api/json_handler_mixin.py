from __future__ import annotations

import json
from typing import Any


class JsonHandlerMixin():
   def _read_json_body( self ) -> dict[ str, Any ]:
      content_length = int( self.headers[ 'Content-Length' ] )
      post_data = self.rfile.read( content_length )
      return json.loads( post_data.decode( 'utf-8' ) )


   def _write_json( self, payload: Any, status: int = 200 ) -> None:
      body = json.dumps( payload ).encode( 'utf-8' )
      self.send_response( status )
      self.send_header( 'Content-type', 'application/json' )
      self.send_header( 'Content-Length', str( len( body ) ) )
      self.end_headers()
      self.wfile.write( body )
