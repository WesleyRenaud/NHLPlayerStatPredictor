from __future__ import annotations

from enum import Enum


class TeamNameChange( str, Enum ):
   UTAH_HOCKEY_CLUB = 'UTAH_MAMMOTH'


   @classmethod
   def current( cls, key: str ) -> str:
      try:
         return cls[ key ].value
      except KeyError:
         return key
