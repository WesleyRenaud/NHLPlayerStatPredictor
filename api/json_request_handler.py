from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class JsonRequestHandler( Protocol ):
   headers: dict[ str, str ]
   rfile: Any
   wfile: Any


   def send_response( self, code: int, message: str | None = None ) -> None:
      ...


   def send_header( self, keyword: str, value: str ) -> None:
      ...


   def end_headers( self ) -> None:
      ...


   def _read_json_body( self ) -> dict[ str, Any ]:
      ...


   def _write_json( self, payload: Any, status: int = 200 ) -> None:
      ...


PostRouteHandler = Callable[ [ JsonRequestHandler ], None ]
