from __future__ import annotations

from pathlib import Path

import pytest

from api.server.page_strings import PageStrings
from api.server.static_file_sender import StaticFileSender


class _RecordingHandler():
   def __init__( self ) -> None:
      self.status: int | None = None
      self.headers: dict[ str, str ] = {}
      self.body = bytearray()
      self.wfile = self


   def send_response( self, code: int, message: str | None = None ) -> None:
      self.status = code


   def send_header( self, key: str, value: str ) -> None:
      self.headers[ key ] = value


   def end_headers( self ) -> None:
      return


   def send_error( self, code: int, message: str | None = None ) -> None:
      self.status = code


   def write( self, data: bytes ) -> int:
      self.body.extend( data )
      return len( data )


def Test_Send_TestExistingFile_ExpectOk(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   heading = 'Stub Heading'
   token = '{{ page.heading }}'
   filepath = tmp_path / 'page.html'
   filepath.write_text( f'<h1>{ token }</h1>', encoding='utf-8' )
   handler = _RecordingHandler()
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': heading } )

   StaticFileSender.send( handler, filepath )

   assert handler.status == 200
   assert heading.encode() in handler.body
   assert token.encode() not in handler.body


def Test_Send_TestMissingFile_ExpectNotFound( tmp_path: Path ) -> None:
   handler = _RecordingHandler()
   missing = tmp_path / 'missing.css'

   StaticFileSender.send( handler, missing )

   assert handler.status == 404
