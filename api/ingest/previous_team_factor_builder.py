from __future__ import annotations

from ..depth.ice_usage import IceUsage
from ..depth.slot_average import SlotAverage
from .nhl_team_split_builder import NhlTeamSplitBuilder
from ..season_length import SeasonLength
from ..team_factor.team_factor import TeamFactor
from ..team_factor.team_factor_fitter import TeamFactorFitter
from ..types import Types


class PreviousTeamFactorBuilder():
   @classmethod
   def build(
         cls,
         season_ids: list[ int ],
         landings: dict[ int, Types.JsonObject ],
         slots: list[ SlotAverage ],
         usages_by_season: dict[ int, dict[ int, IceUsage ] ],
         seasons: list[ SeasonLength ],
         pace_games: int ) -> list[ TeamFactor ]:
      games = { season.season_id: season.number_of_games for season in seasons }
      factors = []

      for season_id in season_ids:
         factors.extend(
            TeamFactorFitter.previous(
               season_id,
               NhlTeamSplitBuilder.build( landings, season_id, pace_games ),
               slots,
               usages_by_season[ season_id ],
               games[ season_id ] ) )

      return factors
