from __future__ import annotations

import html
import re

from .page_strings import PageStrings
from ..shared.enums.position import Position


HTML_STRING_TOKEN_RE = re.compile( r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}' )


class HtmlStringRenderer():
   @classmethod
   def render( cls, content: str ) -> str:
      values = PageStrings.VALUES

      def replace_token( match: re.Match[ str ] ) -> str:
         value = values.get( match.group( Position.SECOND ) )

         if value is None:
            return match.group( Position.FIRST )

         return html.escape( value, quote=True )

      return HTML_STRING_TOKEN_RE.sub( replace_token, content )
