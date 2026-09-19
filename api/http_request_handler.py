from __future__ import annotations

from http.server import BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse

from .json_handler_mixin import JsonHandlerMixin
from .routes import PostRouteRegistry
from .static_page_routes import StaticPageRoutes


class HttpRequestHandler( JsonHandlerMixin, BaseHTTPRequestHandler ):
   def do_GET( self ) -> None:
      path = unquote( urlparse( self.path ).path )

      if StaticPageRoutes.serve( self, path ):
         return

      self.send_error( 404, 'Not Found' )


   def do_POST( self ) -> None:
      path = unquote( urlparse( self.path ).path )

      if PostRouteRegistry.serve( self, path ):
         return

      self.send_error( 404, 'Not Found' )
