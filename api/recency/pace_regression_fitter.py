from __future__ import annotations

from collections import defaultdict

from ..aging.league_factor import LeagueFactor
from .nhl_production_regression import NhlProductionRegression
from .nhl_production_stat import NhlProductionStat
from .pace_regression_model import PaceRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_coefficient_fitter import ProductionCoefficientFitter
from .production_pair import ProductionPair
from .production_trajectory_fitter import ProductionTrajectoryFitter
from .scoring_component_share_fitter import ScoringComponentShareFitter
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason


class PaceRegressionFitter():
   @classmethod
   def fit(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> PaceRegressionModel:
      by_player: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )
      component_shares = ScoringComponentShareFitter.fit( nhl_seasons )

      for season in [ *nhl_seasons, *other_seasons ]:
         by_player[ season.player_id ].append( season )

      history_by_player = {
         player_id: PriorYearBuilder.history( seasons, factors, component_shares )
         for player_id, seasons in by_player.items()
      }

      points_pairs: list[ ProductionPair ] = []

      for current in nhl_seasons:
         if current.games_played < PriorYear.MIN_GAMES:
            continue

         year = Season.start_year( current.season_id )
         priors = history_by_player[ current.player_id ]
         actual = current.scoring_paces()

         for prior in priors:
            lag = year - prior.year

            if prior.games < PriorYear.MIN_GAMES or not 0 < lag <= PriorYearBuilder.WIDTH:
               continue

            age = int( prior.age )
            games = float( min( prior.games, current.games_played ) )
            points_pairs.append( ProductionPair(
               from_age=age,
               to_age=age + lag,
               prior_pace=prior.scoring.goals + prior.scoring.assists,
               following_pace=actual.goals + actual.assists,
               games=games ) )

      nhl_history_by_player = (
         NhlProductionRegression.history( nhl_seasons ) if other_seasons else history_by_player )
      growth = ProductionCoefficientFitter.fit_growth( points_pairs )
      return PaceRegressionModel(
         growth,
         component_shares,
         pim_coefficients=NhlProductionRegression.fit( nhl_seasons, NhlProductionStat.PIM, nhl_history_by_player ),
         shots_coefficients=NhlProductionRegression.fit( nhl_seasons, NhlProductionStat.SHOTS, nhl_history_by_player ),
         history_weights=ProductionCoefficientFitter.fit_weights( points_pairs ),
         trajectory=ProductionTrajectoryFitter.fit(
            ProductionTrajectoryFitter.observe( nhl_history_by_player, growth ) ),
         debut_trajectory=ProductionTrajectoryFitter.fit(
            ProductionTrajectoryFitter.observe_debuts( history_by_player, growth ) ),
         short_nhl_trajectory=ProductionTrajectoryFitter.fit(
            ProductionTrajectoryFitter.observe_short_nhl( history_by_player, growth ) ) )
