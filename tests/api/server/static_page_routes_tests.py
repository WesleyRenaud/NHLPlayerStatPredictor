from __future__ import annotations

from pathlib import Path

import pytest

import api.server.static_page_routes as static_page_routes
from api.server.static_page_routes import StaticPageRoutes


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
   path = '/missing'

   served = StaticPageRoutes.serve( object(), path )

   assert served is False


def Test_Serve_TestMappedPage_ExpectSendsFile(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   sent: list[ Path ] = []
   path = '/stub.html'
   page = 'pages/stub.html'
   monkeypatch.setattr(
      StaticPageRoutes,
      'PAGES',
      { path: page } )
   monkeypatch.setattr(
      static_page_routes.StaticFileSender,
      'send',
      lambda handler, filepath: sent.append( filepath ) )

   served = StaticPageRoutes.serve( object(), path )

   assert served is True
   assert sent == [ static_page_routes.Paths.ROOT / page ]


def Test_Serve_TestRedirect_ExpectLocation(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   source = '/'
   target = '/stub.html'
   handler = _RecordingHandler()
   monkeypatch.setattr(
      StaticPageRoutes,
      'REDIRECTS',
      { source: target } )

   served = StaticPageRoutes.serve( handler, source )

   assert served is True
   assert handler.status == 302
   assert handler.headers[ 'Location' ] == target


def Test_Serve_TestPrefixedFile_ExpectSends(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   styles = tmp_path / 'styles'
   styles.mkdir()
   css = '.stub {}'
   ( styles / 'app.css' ).write_text( css, encoding='utf-8' )
   path = '/styles/app.css'
   handler = _RecordingHandler()
   monkeypatch.setattr( static_page_routes.Paths, 'ROOT', tmp_path )
   monkeypatch.setattr( StaticPageRoutes, 'PREFIXES', ( '/styles/', ) )

   served = StaticPageRoutes.serve( handler, path )

   assert served is True
   assert handler.status == 200
   assert css.encode() in handler.body
