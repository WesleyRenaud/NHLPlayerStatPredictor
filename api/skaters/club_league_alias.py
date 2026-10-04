from __future__ import annotations

from .club_league import ClubLeague


class ClubLeagueAlias():
   LABELS: dict[ ClubLeague, list[ str ] ] = {
      ClubLeague.ALLSVENSKAN: [ 'HockeyAllsvenskan' ],
      ClubLeague.CZECHIA: [ 'Czech', 'CZE', 'CzRep' ],
      ClubLeague.DEL: [ 'Germany' ],
      ClubLeague.KHL: [ 'Rus-KHL', 'Russia' ],
      ClubLeague.LIIGA: [ 'Finland' ],
      ClubLeague.NCAA: [ 'WCHA', 'CCHA', 'H-East', 'ECAC', 'NCHC', 'Big Ten', 'CHA' ],
      ClubLeague.NL: [ 'NLA', 'Swiss' ],
      ClubLeague.SHL: [ 'Sweden' ],
   }


   @classmethod
   def league( cls, label: str ) -> ClubLeague | None:
      if ClubLeague.contains( label ):
         return ClubLeague( label )

      for league, labels in ClubLeagueAlias.LABELS.items():
         if label in labels:
            return league

      return None


   @classmethod
   def rank( cls, label: str ) -> int:
      league = cls.league( label )

      if league is None or league.value == label:
         return 0

      return ClubLeagueAlias.LABELS[ league ].index( label ) + 1
