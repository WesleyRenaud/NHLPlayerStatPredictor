from __future__ import annotations

from datetime import date

from ..ingest.nhl_client import NhlClient
from ..paths import Paths
from ..season import Season
from ..season_length import SeasonLength
from ..skaters.roster_skater_provider import RosterSkaterProvider
from ..types import Types


class SeasonStatsResolver():
   @classmethod
   def resolve( cls, player_id: int, on_date: date ) -> Types.JsonObject | None:
      started_seasons = [ season for season in NhlClient.seasons() if season.start_date <= on_date ]

      season = Season.latest( started_seasons )
      summary = next(
         ( row for row in NhlClient.skater_summary( season.season_id ) if row.player_id == player_id ),
         None )

      if summary is None:
         return None

      games_remaining = cls._games_remaining( player_id, season, on_date )
      return {
         'seasonLabel': Season.label( season.season_id ),
         **summary.stats_dict(),
         'fullSeasonPace': summary.full_season_pace( games_remaining ),
      }


   @classmethod
   def _games_remaining( cls, player_id: int, season: SeasonLength, on_date: date ) -> int:
      if on_date > season.regular_season_end_date:
         return 0

      team = RosterSkaterProvider.team( player_id, str( Paths.DB_PATH ) )
      standing = next(
         row for row in NhlClient.standings()[ 'standings' ]
         if int( row[ 'seasonId' ] ) == season.season_id and row[ 'teamAbbrev' ][ 'default' ] == team.value )
      return season.number_of_games - int( standing[ 'gamesPlayed' ] )
