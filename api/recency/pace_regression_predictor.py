from __future__ import annotations

from .nhl_production_regression import NhlProductionRegression
from .nhl_production_stat import NhlProductionStat
from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
from .prior_source import PriorSource
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_coefficient import ProductionCoefficient
from .production_history_predictor import ProductionHistoryPredictor
from ..projections.pace_values import PaceValues
from ..projections.scoring_stat import ScoringStat
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class PaceRegressionPredictor():
   @classmethod
   def paces(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_season_id: int,
         nhl_seasons: list[ NhlSkaterSeason ] ) -> PaceValues | None:
      if not priors:
         return None

      year = Season.start_year( target_season_id )
      latest = priors[ Position.FIRST ]
      target_age = latest.age_in_year( year )
      projected_paces_by_stat: dict[ ScoringStat, float ] = {}
      nhl_priors = PriorYearBuilder.build( nhl_seasons, [], year, [] )

      for stat in ScoringStat:
         projected_paces_by_stat[ stat ] = cls._pace( model.regressions, priors, target_age, stat )

      return PaceValues(
         **{ stat.value: pace for stat, pace in projected_paces_by_stat.items() },
         penalty_minutes=NhlProductionRegression.pace(
            model.pim_coefficients, nhl_priors, year, NhlProductionStat.PIM ),
         shots=NhlProductionRegression.pace(
            model.shots_coefficients, nhl_priors, year, NhlProductionStat.SHOTS ) )


   @classmethod
   def _pace(
         cls,
         regressions: list[ PaceRegression ],
         priors: list[ PriorYear ],
         target_age: int,
         stat: ScoringStat ) -> float:
      if not priors:
         return 0.0

      sources = { int( prior.age ): prior.source() for prior in priors }

      def lookup( from_age: int, to_age: int ) -> ProductionCoefficient:
         source = sources.get( from_age, priors[ Position.FIRST ].source() )
         return cls._coefficient( regressions, source, stat, from_age, to_age )

      return ProductionHistoryPredictor.pace(
         [ ( int( prior.age ), getattr( prior.scoring, stat.value ), prior.games ) for prior in priors ],
         target_age,
         lookup )


   @classmethod
   def _coefficient(
         cls,
         regressions: list[ PaceRegression ],
         source: PriorSource,
         stat: ScoringStat,
         from_age: int,
         to_age: int ) -> ProductionCoefficient:
      matching = [
         regression for regression in regressions
         if regression.source == source and regression.stat == stat
      ]

      if not matching:
         matching = [
            regression for regression in regressions
            if regression.source == PriorSource.NHL and regression.stat == stat
         ]

      coefficients = [ coefficient for regression in matching for coefficient in regression.coefficients ]
      return ProductionHistoryPredictor.coefficient( coefficients, from_age, to_age )
