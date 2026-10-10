from __future__ import annotations

from functools import partial

from ..depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from .nhl_production_regression import NhlProductionRegression
from .nhl_production_stat import NhlProductionStat
from .pace_regression_model import PaceRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_history_predictor import ProductionHistoryPredictor
from .production_season import ProductionSeason
from .production_trajectory_fit import ProductionTrajectoryFit
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
         nhl_seasons: list[ NhlSkaterSeason ],
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None ) -> PaceValues | None:
      if not priors:
         return None

      priors = cls._history( priors )
      year = Season.start_year( target_season_id )
      latest = priors[ Position.FIRST ]
      target_age = latest.age_in_year( year )
      projected_paces_by_stat: dict[ ScoringStat, float ] = {}
      nhl_priors = PriorYearBuilder.build( nhl_seasons, [], year, [], player_ice_scales )
      curve = cls._scoring_curve( priors, nhl_seasons )

      for stat in ScoringStat:
         projected_paces_by_stat[ stat ] = cls._pace(
            model, priors, target_age, stat, model.trajectory, curve )

      return PaceValues(
         **{ stat.value: pace for stat, pace in projected_paces_by_stat.items() },
         penalty_minutes=NhlProductionRegression.pace(
            model.pim_coefficients, nhl_priors, year, NhlProductionStat.PIM, model.trajectory ),
         shots=NhlProductionRegression.pace(
            model.shots_coefficients, nhl_priors, year, NhlProductionStat.SHOTS, model.trajectory ) )


   @classmethod
   def _history( cls, priors: list[ PriorYear ] ) -> list[ PriorYear ]:
      arrived = priors[ Position.FIRST ].arrival is not None
      seen_nhl = False
      kept: list[ PriorYear ] = []

      for index, prior in enumerate( priors ):
         if prior.nhl_games:
            kept.append( prior )
            seen_nhl = True
         elif not seen_nhl and ( index == Position.FIRST or not arrived ):
            kept.append( prior )

      return kept


   @classmethod
   def _pace(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_age: int,
         stat: ScoringStat,
         trajectory: ProductionTrajectoryFit,
         curve: list[ ProductionSeason ] ) -> float:
      if not priors:
         return 0.0

      return ProductionHistoryPredictor.pace(
         [ ProductionSeason(
            prior.age,
            getattr( prior.scoring, stat.value ),
            prior.games,
            None if prior.arrival is None else getattr( prior.arrival, stat.value ) )
            for prior in priors ],
         target_age,
         partial( ProductionHistoryPredictor.coefficient, model.scoring_growth ),
         partial( ProductionHistoryPredictor.weight, model.history_weights ),
         trajectory,
         curve )


   @classmethod
   def _scoring_curve(
         cls,
         priors: list[ PriorYear ],
         nhl_seasons: list[ NhlSkaterSeason ] ) -> list[ ProductionSeason ]:
      # Judge the scoring line the player actually had. Ice rescaling is a minutes
      # adjustment and would redraw a level as a dip, or a dip as noise.
      played = {
         Season.start_year( season.season_id ): season.p_pace
         for season in nhl_seasons
      }
      return [
         ProductionSeason(
            prior.age,
            played.get( prior.year, cls._played_points( prior ) ),
            prior.games )
         for prior in priors
      ]


   @classmethod
   def _played_points( cls, prior: PriorYear ) -> float:
      scoring = prior.scoring if prior.arrival is None else prior.arrival
      return scoring.goals + scoring.assists
