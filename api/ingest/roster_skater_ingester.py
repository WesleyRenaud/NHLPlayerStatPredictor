from __future__ import annotations

from .nhl_client import NhlClient
from .roster_skater_builder import RosterSkaterBuilder
from ..season import Season
from ..skaters.roster_skater import RosterSkater
from ..skaters.team import Team
from ..types import Types


class RosterSkaterIngester():
   @classmethod
   def build_rows( cls, force: bool = False ) -> list[ RosterSkater ]:
      rows: list[ RosterSkater ] = []
      seen: set[ int ] = set()
      teams = cls._teams( NhlClient.standings( force=force ) )

      for team in teams:
         print( f'Fetching roster { team.value }...', flush=True )
         cls._add( rows, seen, team, NhlClient.roster( team.value, force=force ) )

      previous_season_id = Season.prior( NhlClient.seasons( force=force ) ).season_id

      for team in teams:
         cls._add(
            rows,
            seen,
            team,
            NhlClient.season_roster( team.value, previous_season_id, force=force ) )

      return rows


   @classmethod
   def _add(
         cls,
         rows: list[ RosterSkater ],
         seen: set[ int ],
         team: Team,
         payload: Types.JsonObject ) -> None:
      for row in RosterSkaterBuilder.build( team, payload ):
         if row.player_id in seen:
            continue

         seen.add( row.player_id )
         rows.append( row )


   @classmethod
   def _teams( cls, standings: Types.JsonObject ) -> list[ Team ]:
      raw_rows = standings[ 'standings' ]

      if not isinstance( raw_rows, list ):
         raise TypeError( 'standings' )

      teams: list[ Team ] = []
      seen: set[ Team ] = set()

      for raw in raw_rows:
         if not isinstance( raw, dict ):
            continue

         team = Team( cls._abbrev( raw ) )

         if team in seen:
            continue

         seen.add( team )
         teams.append( team )

      return sorted( teams, key=lambda team: team.value )


   @classmethod
   def _abbrev( cls, raw: Types.JsonObject ) -> str:
      abbrev = raw[ 'teamAbbrev' ]

      if not isinstance( abbrev, dict ):
         raise TypeError( 'teamAbbrev' )

      return str( abbrev[ 'default' ] )
