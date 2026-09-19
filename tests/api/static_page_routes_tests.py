from __future__ import annotations

from pathlib import Path

import pytest

import api.static_page_routes as static_page_routes
from api.static_page_routes import StaticPageRoutes


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


def Test_Serve_TestUnknownPath_ExpectFalse() -> None:
   assert StaticPageRoutes.serve( object(), '/missing' ) is False


def Test_Serve_TestMappedPage_ExpectSendsFile(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   sent: list[ Path ] = []
   monkeypatch.setattr(
      StaticPageRoutes,
      'PAGES',
      { '/stub.html': 'pages/stub.html' } )
   monkeypatch.setattr(
      static_page_routes.StaticFileSender,
      'send',
      lambda handler, filepath: sent.append( filepath ) )
   assert StaticPageRoutes.serve( object(), '/stub.html' ) is True
   assert sent == [ static_page_routes.Paths.ROOT / 'pages/stub.html' ]


def Test_Serve_TestRedirect_ExpectLocation(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      StaticPageRoutes,
      'REDIRECTS',
      { '/': '/stub.html' } )
   handler = _RecordingHandler()
   assert StaticPageRoutes.serve( handler, '/' ) is True
   assert handler.status == 302
   assert handler.headers[ 'Location' ] == '/stub.html'


def Test_Serve_TestPrefixedFile_ExpectSends(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   styles = tmp_path / 'styles'
   styles.mkdir()
   ( styles / 'app.css' ).write_text( '.stub {}', encoding='utf-8' )
   monkeypatch.setattr( static_page_routes.Paths, 'ROOT', tmp_path )
   monkeypatch.setattr( StaticPageRoutes, 'PREFIXES', ( '/styles/', ) )
   handler = _RecordingHandler()
   assert StaticPageRoutes.serve( handler, '/styles/app.css' ) is True
   assert handler.status == 200
   assert b'.stub {}' in handler.body
