from __future__ import annotations

from ..availability.games_share import GamesShare
from .ice_usage import IceUsage
from .last_toi import LastToi
from ..skaters.skater_position import SkaterPosition
from ..skaters.team import Team
from ..team_factor.teammate_skater import TeammateSkater
from .usable_nhl_ice import UsableNhlIce


class LastCore():
   EXTRA = 1


   @classmethod
   def shares(
         cls,
         team: Team,
         ice_usages: dict[ int, IceUsage ],
         season_length: int,
         dressed_count: int,
         positions: set[ SkaterPosition ] ) -> list[ float ]:
      ranked = cls.ranked( team, ice_usages, positions )
      shares = [
         GamesShare.resolve( ice_usages[ player_id ].games, season_length )
         for player_id in ranked[ : dressed_count ]
      ]

      while len( shares ) < dressed_count:
         shares.append( GamesShare.FULL )

      return shares


   @classmethod
   def teammates(
         cls,
         team: Team,
         ice_usages: dict[ int, IceUsage ],
         paces: dict[ int, float ],
         season_length: int,
         dressed_count: int,
         extra_count: int,
         positions: set[ SkaterPosition ] ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      ranked = cls.ranked( team, ice_usages, positions )
      regulars = [
         cls._teammate(
            player_id,
            ice_usages,
            paces,
            season_length,
            False )
         for player_id in ranked[ : dressed_count ]
      ]
      extras = [
         cls._teammate(
            player_id,
            ice_usages,
            paces,
            season_length,
            True )
         for player_id in cls._extras(
            ice_usages,
            ranked[ dressed_count : ],
            extra_count )
      ]
      return regulars, extras


   @classmethod
   def ranked(
         cls,
         team: Team,
         ice_usages: dict[ int, IceUsage ],
         positions: set[ SkaterPosition ] ) -> list[ int ]:
      rows = [
         player_id
         for player_id, usage in ice_usages.items()
         if usage.team == team
         and usage.position in positions
      ]
      rows.sort(
         key=lambda player_id: LastToi.key(
            player_id,
            ice_usages[ player_id ].toi ) )
      return rows


   @classmethod
   def _extras(
         cls,
         ice_usages: dict[ int, IceUsage ],
         remaining: list[ int ],
         extra_count: int ) -> list[ int ]:
      extras = []

      for player_id in remaining:
         if ice_usages[ player_id ].games < UsableNhlIce.MIN_GAMES:
            continue

         extras.append( player_id )

         if len( extras ) == extra_count:
            break

      return extras


   @classmethod
   def _teammate(
         cls,
         player_id: int,
         ice_usages: dict[ int, IceUsage ],
         paces: dict[ int, float ],
         season_length: int,
         extra: bool ) -> TeammateSkater:
      availability = GamesShare.FULL if extra else (
         GamesShare.resolve( ice_usages[ player_id ].games, season_length ) )
      return TeammateSkater(
         player_id,
         paces.get( player_id, 0.0 ),
         availability,
         None )
