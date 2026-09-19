from __future__ import annotations

from pathlib import Path

import pytest

from api.page_strings import PageStrings
from api.static_file_sender import StaticFileSender


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
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': 'Stub Heading' } )
   filepath = tmp_path / 'page.html'
   filepath.write_text( '<h1>{{ page.heading }}</h1>', encoding='utf-8' )
   handler = _RecordingHandler()
   StaticFileSender.send( handler, filepath )
   assert handler.status == 200
   assert b'Stub Heading' in handler.body
   assert b'{{ page.heading }}' not in handler.body


def Test_Send_TestMissingFile_ExpectNotFound( tmp_path: Path ) -> None:
   handler = _RecordingHandler()
   StaticFileSender.send( handler, tmp_path / 'missing.css' )
   assert handler.status == 404
