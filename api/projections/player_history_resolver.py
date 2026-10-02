from __future__ import annotations

from ..ingest.nhl_client import NhlClient
from .nhl_history_season import NhlHistorySeason
from ..paths import Paths
from .player_career_stats import PlayerCareerStats
from .player_history import PlayerHistory
from ..skaters.skater_season_provider import SkaterSeasonProvider
from ..skaters.skater_summary import SkaterSummary
from ..types import Types


class PlayerHistoryResolver():
   @classmethod
   def resolve( cls, player_id: int ) -> Types.JsonObject:
      seasons: list[ NhlHistorySeason ] = []
      summaries: list[ SkaterSummary ] = []
      for season in SkaterSeasonProvider.seasons_for_player_id( player_id, str( Paths.DB_PATH ) ):
         summary = next( row for row in NhlClient.skater_summary( season.season_id ) if row.player_id == player_id )
         summaries.append( summary )
         seasons.append( NhlHistorySeason.from_summary( season.season_id, summary ) )

      seasons.sort( key=lambda season: season.season_id )
      career = PlayerCareerStats.from_summaries( summaries ) if summaries else None
      return PlayerHistory( seasons, career ).to_dict()
