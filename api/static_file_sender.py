from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import mimetypes
from pathlib import Path

from .html_string_renderer import HtmlStringRenderer


class StaticFileSender():
   @classmethod
   def send( cls, handler: BaseHTTPRequestHandler, filepath: Path ) -> None:
      if not filepath.is_file():
         handler.send_error( 404, 'Not Found' )
         return

      content_type, _ = mimetypes.guess_type( str( filepath ) )

      if filepath.suffix == '.html':
         body = HtmlStringRenderer.render(
            filepath.read_text( encoding='utf-8' ) ).encode( 'utf-8' )
         content_type = 'text/html'
      else:
         body = filepath.read_bytes()

      handler.send_response( 200 )
      handler.send_header(
         'Content-Type',
         content_type or 'application/octet-stream' )
      handler.send_header( 'Content-Length', str( len( body ) ) )
      handler.end_headers()
      handler.wfile.write( body )
