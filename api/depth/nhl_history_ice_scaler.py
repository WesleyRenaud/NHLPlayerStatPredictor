from __future__ import annotations

from .ice_usage_parser import IceUsageParser
from ..ingest.nhl_client import NhlClient
from .nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from ..recency.prior_year_builder import PriorYearBuilder
from ..skaters.nhl_skater_season import NhlSkaterSeason


class NhlHistoryIceScaler():
   @classmethod
   def scales(
         cls,
         seasons: list[ NhlSkaterSeason ],
         target_season: int,
         reference_toi: float ) -> list[ NhlPlayerSeasonIceScale ]:
      if reference_toi <= 0.0:
         raise ValueError( 'Historical TOI reference must be positive' )

      history = sorted(
         ( season for season in seasons
            if season.games_played and season.season_id < target_season ),
         key=lambda season: season.season_id,
         reverse=True )[ :PriorYearBuilder.WIDTH ]
      scales = []

      for season in history:
         usage = IceUsageParser.parse(
            NhlClient.skater_timeonice( season.season_id ) )[ season.player_id ]

         scales.append( NhlPlayerSeasonIceScale(
            season.player_id, season.season_id, reference_toi / usage.toi ) )

      return scales
