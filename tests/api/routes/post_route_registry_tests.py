from __future__ import annotations

import pytest

from api.json_handler_mixin import JsonHandlerMixin
from api.routes.post_route_registry import PostRouteRegistry


class _Handler( JsonHandlerMixin ):
   def __init__( self ) -> None:
      self.called = False


def Test_Serve_TestUnknownPath_ExpectFalse() -> None:
   assert PostRouteRegistry.serve( _Handler(), '/missing' ) is False


def Test_Serve_TestRegisteredPath_ExpectHandlerCalled(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   handler = _Handler()
   path = '/stub-route'

   def fake_route( received: _Handler ) -> None:
      received.called = True

   monkeypatch.setattr( PostRouteRegistry, 'ROUTES', { path: fake_route } )
   assert PostRouteRegistry.serve( handler, path ) is True
   assert handler.called is True
