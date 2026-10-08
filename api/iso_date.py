from __future__ import annotations

from datetime import date, datetime


class IsoDate():
   @classmethod
   def parse( cls, value: str ) -> date:
      text = value[ :10 ]

      try:
         return date.fromisoformat( text )
      except ValueError:
         return datetime.fromisoformat( value.replace( 'Z', '+00:00' ) ).date()
