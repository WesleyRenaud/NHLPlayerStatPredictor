from __future__ import annotations

import json
from pathlib import Path
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from api.http_request_handler import HttpRequestHandler
from api.page_strings import PageStrings
import api.player_names.controllers.player_names_controller as player_names_controller
from api.player_names.player_name_summary import PlayerNameSummary
from api.player_names.player_names_routes import PlayerNamesRoutes
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
import api.static_page_routes as static_page_routes
from api.static_page_routes import StaticPageRoutes
from api.team import Team
from api.threaded_http_server import ThreadedHttpServer


def _start_server() -> ThreadedHttpServer:
   server = ThreadedHttpServer( ( '127.0.0.1', 0 ), HttpRequestHandler )
   thread = threading.Thread( target=server.serve_forever, daemon=True )
   thread.start()
   return server


def _stub_site( tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None:
   ( tmp_path / 'page.html' ).write_text(
      '<form id="player-name">{{ page.heading }}</form>',
      encoding='utf-8' )
   styles = tmp_path / 'styles'
   styles.mkdir()
   ( styles / 'app.css' ).write_text( '.stub {}', encoding='utf-8' )
   monkeypatch.setattr( static_page_routes.Paths, 'ROOT', tmp_path )
   monkeypatch.setattr(
      StaticPageRoutes,
      'PAGES',
      { '/stub.html': 'page.html' } )
   monkeypatch.setattr(
      StaticPageRoutes,
      'REDIRECTS',
      { '/': '/stub.html' } )
   monkeypatch.setattr( StaticPageRoutes, 'PREFIXES', ( '/styles/', ) )
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': 'Stub Heading' } )


def Test_DoGet_TestAppPage_ExpectLookupPage(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   _stub_site( tmp_path, monkeypatch )
   server = _start_server()

   try:
      port = server.server_address[ Position.SECOND ]
      response = urlopen(
         f'http://127.0.0.1:{ port }/stub.html',
         timeout=5 )
      body = response.read()
   finally:
      server.shutdown()
      server.server_close()

   assert response.status == 200
   assert b'player-name' in body
   assert b'Stub Heading' in body
   assert b'{{' not in body


def Test_DoGet_TestRoot_ExpectRedirectsToAppPage(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   _stub_site( tmp_path, monkeypatch )
   server = _start_server()

   try:
      port = server.server_address[ Position.SECOND ]
      response = urlopen( f'http://127.0.0.1:{ port }/', timeout=5 )
   finally:
      server.shutdown()
      server.server_close()

   assert response.geturl().endswith( '/stub.html' )


def Test_DoGet_TestStylesheet_ExpectCss(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   _stub_site( tmp_path, monkeypatch )
   server = _start_server()

   try:
      port = server.server_address[ Position.SECOND ]
      response = urlopen(
         f'http://127.0.0.1:{ port }/styles/app.css',
         timeout=5 )
      body = response.read()
   finally:
      server.shutdown()
      server.server_close()

   assert response.status == 200
   assert b'.stub {}' in body


def Test_DoGet_TestUnknownPath_ExpectNotFound(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   _stub_site( tmp_path, monkeypatch )
   server = _start_server()

   try:
      port = server.server_address[ Position.SECOND ]

      try:
         urlopen( f'http://127.0.0.1:{ port }/missing', timeout=5 )
         raise AssertionError( 'Expected HTTP 404' )
      except HTTPError as error:
         assert error.code == 404
   finally:
      server.shutdown()
      server.server_close()


def Test_DoPost_TestPlayerNames_ExpectJson(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   stub_summaries = [
      PlayerNameSummary(
         1,
         'Stub Alpha',
         list( SkaterPosition )[ Position.FIRST ],
         list( Team )[ Position.FIRST ],
         20202021 ),
   ]
   monkeypatch.setattr(
      player_names_controller.PlayerNamesCoordinator,
      'get_player_summaries',
      lambda: stub_summaries )
   path = PlayerNamesRoutes.GET_PLAYER_NAMES
   server = _start_server()

   try:
      port = server.server_address[ Position.SECOND ]
      request = Request(
         f'http://127.0.0.1:{ port }{ path }',
         data=b'{}',
         headers={ 'Content-Type': 'application/json' },
         method='POST' )
      response = urlopen( request, timeout=5 )
      body = json.loads( response.read().decode( 'utf-8' ) )
   finally:
      server.shutdown()
      server.server_close()

   assert response.status == 200
   assert body == [ summary.as_json() for summary in stub_summaries ]


def Test_DoPost_TestUnknownPath_ExpectNotFound() -> None:
   server = _start_server()

   try:
      port = server.server_address[ Position.SECOND ]
      request = Request(
         f'http://127.0.0.1:{ port }/missing',
         data=b'{}',
         headers={ 'Content-Type': 'application/json' },
         method='POST' )

      try:
         urlopen( request, timeout=5 )
         raise AssertionError( 'Expected HTTP 404' )
      except HTTPError as error:
         assert error.code == 404
   finally:
      server.shutdown()
      server.server_close()
