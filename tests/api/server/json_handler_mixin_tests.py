from __future__ import annotations

from io import BytesIO
import json

from api.server.json_handler_mixin import JsonHandlerMixin


class _RecordingHandler( JsonHandlerMixin ):
   def __init__( self ) -> None:
      self.status: int | None = None
      self.headers: dict[ str, str ] = {}
      self.body = bytearray()
      self.wfile = self
      self.rfile = BytesIO()


   def send_response( self, code: int, message: str | None = None ) -> None:
      self.status = code


   def send_header( self, key: str, value: str ) -> None:
      self.headers[ key ] = value


   def end_headers( self ) -> None:
      return


   def write( self, data: bytes ) -> int:
      self.body.extend( data )
      return len( data )


def Test_WriteJson_TestPayload_ExpectEncodedBody() -> None:
   handler = _RecordingHandler()
   payload = { 'names': [ 'Stub Alpha' ] }
   handler._write_json( payload )
   assert handler.status == 200
   assert handler.headers[ 'Content-type' ] == 'application/json'
   assert json.loads( handler.body.decode( 'utf-8' ) ) == payload


def Test_ReadJsonBody_TestPayload_ExpectDecodedObject() -> None:
   payload = { 'query': 'Stub Alpha' }
   encoded = json.dumps( payload ).encode( 'utf-8' )
   handler = _RecordingHandler()
   handler.headers[ 'Content-Length' ] = str( len( encoded ) )
   handler.rfile = BytesIO( encoded )
   assert handler._read_json_body() == payload
