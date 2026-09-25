from __future__ import annotations

from ..aging.aging_factor import AgingFactor
from ..aging.league_factor import LeagueFactor
from .aging_pace_adjuster import AgingPaceAdjuster
from ..recency.recency_weight import RecencyWeight
from .season_pace import SeasonPace
from ..shared.enums.position import Position
from ..skaters.skater import Skater
from .translated_pace_averager import TranslatedPaceAverager


class BaselinePaceResolver():
   @classmethod
   def resolve(
         cls,
         skater: Skater,
         weights: list[ RecencyWeight ],
         target_season_id: int,
         league_factors: list[ LeagueFactor ],
         aging_factors: list[ AgingFactor ] ) -> SeasonPace | None:
      pace = TranslatedPaceAverager.average(
         skater.seasons,
         weights,
         target_season_id,
         league_factors )

      if pace is None:
         return None

      nhl = skater.nhl_seasons()
      return AgingPaceAdjuster.adjust(
         pace,
         ( nhl if nhl else skater.seasons )[ Position.LAST ].completed_age(),
         aging_factors,
         nhl )
