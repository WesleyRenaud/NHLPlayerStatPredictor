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
from ..projections.prospect_eligibility import ProspectEligibility
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

      year = Season.start_year( target_season_id )
      latest = priors[ Position.FIRST ]
      target_age = latest.age_in_year( year )
      projected_paces_by_stat: dict[ ScoringStat, float ] = {}
      nhl_priors = PriorYearBuilder.build( nhl_seasons, [], year, [], player_ice_scales )

      trajectory = cls._trajectory( model, priors, nhl_seasons, year )

      for stat in ScoringStat:
         projected_paces_by_stat[ stat ] = cls._pace( model, priors, target_age, stat, trajectory )

      return PaceValues(
         **{ stat.value: pace for stat, pace in projected_paces_by_stat.items() },
         penalty_minutes=NhlProductionRegression.pace(
            model.pim_coefficients, nhl_priors, year, NhlProductionStat.PIM, trajectory ),
         shots=NhlProductionRegression.pace(
            model.shots_coefficients, nhl_priors, year, NhlProductionStat.SHOTS, trajectory ) )


   @classmethod
   def _trajectory(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         nhl_seasons: list[ NhlSkaterSeason ],
         year: int ) -> ProductionTrajectoryFit:
      latest = priors[ Position.FIRST ]
      played = sum(
         season.games_played for season in nhl_seasons
         if Season.start_year( season.season_id ) < year )

      if (
            model.short_nhl_trajectory.by_age
            and ProspectEligibility.short_nhl(
               latest.age, latest.nhl_games, latest.games - latest.nhl_games, played ) ):
         return model.short_nhl_trajectory

      if (
            model.debut_trajectory.by_age
            and ProspectEligibility.pre_nhl( latest.age, latest.nhl_games, played ) ):
         return model.debut_trajectory

      if cls._rookie_rise( model, priors, nhl_seasons ):
         return model.rookie_trajectory

      return model.trajectory


   @classmethod
   def _rookie_rise(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         nhl_seasons: list[ NhlSkaterSeason ] ) -> bool:
      if len( priors ) < 2 or not model.rookie_trajectory.by_age:
         return False

      latest = priors[ Position.FIRST ]
      prior = priors[ Position.SECOND ]

      if prior.year != latest.year - 1 or prior.games < PriorYear.MIN_GAMES:
         return False

      seen = { item.year for item in priors }
      before = sum( item.nhl_games for item in priors if item.year < latest.year )
      before += sum(
         season.games_played for season in nhl_seasons
         if Season.start_year( season.season_id ) < latest.year
         and Season.start_year( season.season_id ) not in seen )

      if not ProspectEligibility.rookie_nhl( latest.age, latest.nhl_games, before ):
         return False

      latest_pace = latest.scoring.goals + latest.scoring.assists
      prior_pace = prior.scoring.goals + prior.scoring.assists
      peak = max( latest_pace, prior_pace )
      return peak > 0.0 and ( latest_pace - prior_pace ) / peak >= model.rookie_trajectory.move


   @classmethod
   def _pace(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_age: int,
         stat: ScoringStat,
         trajectory: ProductionTrajectoryFit ) -> float:
      if not priors:
         return 0.0

      return ProductionHistoryPredictor.pace(
         [ ProductionSeason( int( prior.age ), getattr( prior.scoring, stat.value ), prior.games ) for prior in priors ],
         target_age,
         partial( ProductionHistoryPredictor.coefficient, model.scoring_growth ),
         partial( ProductionHistoryPredictor.weight, model.history_weights ),
         trajectory )
