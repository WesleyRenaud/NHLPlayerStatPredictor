from __future__ import annotations

from typing import ClassVar

from ..json_request_handler import JsonRequestHandler, PostRouteHandler


class PostRouteRegistry():
   ROUTES: ClassVar[ dict[ str, PostRouteHandler ] ] = {}


   @classmethod
   def register( cls, routes: dict[ str, PostRouteHandler ] ) -> None:
      cls.ROUTES.update( routes )


   @classmethod
   def serve( cls, handler: JsonRequestHandler, path: str ) -> bool:
      if path not in cls.ROUTES:
         return False

      cls.ROUTES[ path ]( handler )
      return True
