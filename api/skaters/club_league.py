from __future__ import annotations

from enum import Enum


class ClubLeague( str, Enum ):
   AHL = 'AHL'
   ALLSVENSKAN = 'Allsvenskan'
   CZE = 'CZE'
   CZECH = 'Czech'
   CZECHIA = 'Czechia'
   DEL = 'DEL'
   KHL = 'KHL'
   LIIGA = 'Liiga'
   MESTIS = 'Mestis'
   NCAA = 'NCAA'
   NL = 'NL'
   NLA = 'NLA'
   OHL = 'OHL'
   QMJHL = 'QMJHL'
   SHL = 'SHL'
   SLOVAKIA = 'Slovakia'
   USHL = 'USHL'
   VHL = 'VHL'
   WHL = 'WHL'


   @classmethod
   def contains( cls, league: str ) -> bool:
      try:
         cls( league )
      except ValueError:
         return False

      return True
