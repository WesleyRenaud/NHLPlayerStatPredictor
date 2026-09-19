from __future__ import annotations

from typing import Any

import pytest

import api.json_http_client as json_http_client
from api.json_http_client import JsonHttpClient
from api.shared.enums.position import Position
from api.types import Types


class _FakeResponse:
   def __init__(
         self,
         payload: Types.JsonObject | Types.JsonObjectList,
         status_code: int = 200 ) -> None:
      self._payload = payload
      self.status_code = status_code


   def raise_for_status( self ) -> None:
      return None


   def json( self ) -> Types.JsonObject | Types.JsonObjectList:
      return self._payload


class _FakeHttpxClient:
   def __init__( self, **kwargs: Any ) -> None:
      self.requests: list[ tuple[ str, dict[ str, str | int ] | None ] ] = []
      self.responses: list[ _FakeResponse ] = []


   def queue(
         self,
         payload: Types.JsonObject | Types.JsonObjectList,
         status_code: int = 200 ) -> None:
      self.responses.append( _FakeResponse( payload, status_code ) )


   def get(
         self,
         url: str,
         params: dict[ str, str | int ] | None = None ) -> _FakeResponse:
      self.requests.append( ( url, params ) )
      return self.responses.pop( Position.FIRST )


   def close( self ) -> None:
      return None


def Test_GetJson_TestObjectPayload_ExpectDict(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   fake_client = _FakeHttpxClient()
   fake_client.queue( { 'id': 1 } )
   monkeypatch.setattr( json_http_client.httpx, 'Client', lambda **kwargs: fake_client )

   payload = JsonHttpClient.get_json( 'https://example.test/season' )

   assert payload == { 'id': 1 }
   assert fake_client.requests == [ ( 'https://example.test/season', None ) ]


def Test_GetJson_TestListPayload_ExpectDictRows(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   fake_client = _FakeHttpxClient()
   fake_client.queue( [ { 'id': 1 }, { 'id': 2 } ] )
   monkeypatch.setattr( json_http_client.httpx, 'Client', lambda **kwargs: fake_client )

   payload = JsonHttpClient.get_json( 'https://example.test/skaters' )

   assert payload == [ { 'id': 1 }, { 'id': 2 } ]
