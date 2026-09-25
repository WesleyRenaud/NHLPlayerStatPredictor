from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from ..paths import Paths
from .static_file_sender import StaticFileSender


class StaticPageRoutes():
   PAGES = {
      '/nhl-stat-predictor.html': 'pages/nhl-stat-predictor.html',
   }
   REDIRECTS = {
      '/': '/nhl-stat-predictor.html',
      '/index.html': '/nhl-stat-predictor.html',
   }
   PREFIXES = ( '/scripts/', '/styles/' )


   @classmethod
   def serve( cls, handler: BaseHTTPRequestHandler, path: str ) -> bool:
      destination = cls.REDIRECTS.get( path )

      if destination is not None:
         cls._redirect( handler, destination )
         return True

      page = cls.PAGES.get( path )

      if page is not None:
         StaticFileSender.send( handler, Paths.ROOT / page )
         return True

      for prefix in cls.PREFIXES:
         if path.startswith( prefix ):
            cls._serve_prefix( handler, path )
            return True

      return False


   @classmethod
   def _redirect( cls, handler: BaseHTTPRequestHandler, destination: str ) -> None:
      handler.send_response( 302 )
      handler.send_header( 'Location', destination )
      handler.end_headers()


   @classmethod
   def _serve_prefix( cls, handler: BaseHTTPRequestHandler, path: str ) -> None:
      root = Paths.ROOT.resolve()
      filepath = ( root / path.lstrip( '/' ) ).resolve()
      allowed = tuple(
         ( root / prefix.strip( '/' ) ).resolve()
         for prefix in cls.PREFIXES )

      if not any( filepath.is_relative_to( directory ) for directory in allowed ):
         handler.send_error( 404, 'Not Found' )
         return

      StaticFileSender.send( handler, filepath )
