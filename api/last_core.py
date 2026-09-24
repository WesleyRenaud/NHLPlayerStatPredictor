from __future__ import annotations

from .games_share import GamesShare
from .ice_usage import IceUsage
from .last_toi import LastToi
from .shared.enums.position import Position
from .skater_position import SkaterPosition
from .team import Team
from .teammate_skater import TeammateSkater


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
         GamesShare.resolve( usage.games, season_length )
         for _player_id, usage in ranked[ : dressed_count ]
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
         healthy: bool,
         dressed_count: int,
         extra_count: int,
         positions: set[ SkaterPosition ] ) -> tuple[
            list[ TeammateSkater ],
            list[ TeammateSkater ] ]:
      ranked = cls.ranked( team, ice_usages, positions )
      regulars = [
         cls._teammate( player_id, usage, paces, season_length, False, healthy )
         for player_id, usage in ranked[ : dressed_count ]
      ]
      extras = [
         cls._teammate(
            player_id,
            usage,
            paces,
            season_length,
            True,
            False )
         for player_id, usage in ranked[ dressed_count: dressed_count + extra_count ]
      ]
      return regulars, extras


   @classmethod
   def ranked(
         cls,
         team: Team,
         ice_usages: dict[ int, IceUsage ],
         positions: set[ SkaterPosition ] ) -> list[
            tuple[ int, IceUsage ] ]:
      rows = [
         ( player_id, usage )
         for player_id, usage in ice_usages.items()
         if usage.team == team
         and usage.position in positions
      ]
      rows.sort(
         key=lambda item: LastToi.key(
            item[ Position.FIRST ],
            item[ Position.LAST ].toi ) )
      return rows


   @classmethod
   def _teammate(
         cls,
         player_id: int,
         usage: IceUsage,
         paces: dict[ int, float ],
         season_length: int,
         extra: bool,
         healthy: bool ) -> TeammateSkater:
      availability = GamesShare.FULL if extra or healthy else (
         GamesShare.resolve( usage.games, season_length ) )
      return TeammateSkater(
         player_id,
         paces.get( player_id, 0.0 ),
         availability,
         None )
