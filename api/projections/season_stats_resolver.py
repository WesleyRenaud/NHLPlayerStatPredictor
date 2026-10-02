from __future__ import annotations

from datetime import date

from ..ingest.nhl_client import NhlClient
from ..season import Season
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

      return { 'seasonLabel': Season.label( season.season_id ), **summary.stats_dict() }
