from __future__ import annotations

from ..aging.aging_factor import AgingFactor
from ..aging.league_factor import LeagueFactor
from .aging_pace_adjuster import AgingPaceAdjuster
from ..recency.age_recency_weights import AgeRecencyWeights
from .season_pace import SeasonPace
from ..skaters.skater import Skater
from .translated_pace_averager import TranslatedPaceAverager


class BaselinePaceResolver():
   @classmethod
   def resolve(
         cls,
         skater: Skater,
         weights: list[ AgeRecencyWeights ],
         target_season_id: int,
         league_factors: list[ LeagueFactor ],
         aging_factors: list[ AgingFactor ] ) -> SeasonPace | None:
      if not skater.seasons:
         return None

      last = max( skater.seasons, key=lambda season: season.season_id )
      pace = TranslatedPaceAverager.average(
         skater.seasons,
         AgeRecencyWeights.for_age( weights, last.completed_age() + 1 ),
         target_season_id,
         league_factors )

      if pace is None:
         return None

      return AgingPaceAdjuster.adjust(
         pace,
         last.completed_age(),
         aging_factors,
         skater.nhl_seasons() )
