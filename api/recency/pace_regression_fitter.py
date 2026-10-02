from __future__ import annotations

from collections import defaultdict

from ..aging.league_factor import LeagueFactor
from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
from .pace_regression_training_data import PaceRegressionTrainingData
from .prior_source import PriorSource
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_coefficient_fitter import ProductionCoefficientFitter
from .production_pair import ProductionPair
from ..projections.scoring_paces import ScoringPaces
from ..projections.scoring_stat import ScoringStat
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
      nhl_by_player: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in [ *nhl_seasons, *other_seasons ]:
         by_player[ season.player_id ].append( season )

      for season in nhl_seasons:
         nhl_by_player[ season.player_id ].append( season )

      training_datasets = [
         PaceRegressionTrainingData( source, stat )
         for source in sorted( PriorSource )
         for stat in sorted( ScoringStat )
      ]

      for current in nhl_seasons:
         if current.games_played < PriorYear.MIN_GAMES:
            continue

         year = Season.start_year( current.season_id )
         priors = PriorYearBuilder._qualified( by_player[ current.player_id ], factors, year )
         nhl_priors = PriorYearBuilder._qualified( nhl_by_player[ current.player_id ], [], year )
         actual = cls._paces( current )

         for dataset in training_datasets:
            training = priors if dataset.stat in ( ScoringStat.GOALS, ScoringStat.ASSISTS ) else nhl_priors

            for prior in training:
               lag = year - prior.year

               if prior.source() != dataset.source or lag > PriorYearBuilder.WIDTH:
                  continue

               age = int( prior.age )
               dataset.samples.append( ProductionPair(
                  from_age=age,
                  to_age=age + lag,
                  prior_pace=getattr( prior.scoring_paces(), dataset.stat.value ),
                  following_pace=getattr( actual, dataset.stat.value ),
                  games=float( min( prior.games, current.games_played ) ) ) )

      return PaceRegressionModel( [
         PaceRegression( dataset.source, dataset.stat, ProductionCoefficientFitter.fit( dataset.samples ) )
         for dataset in training_datasets
         if dataset.samples
      ] )


   @classmethod
   def _paces( cls, season: NhlSkaterSeason ) -> ScoringPaces:
      power_play = season.power_play_pace()
      short_handed = season.short_handed_pace()
      return ScoringPaces(
         season.g_pace,
         season.a_pace,
         power_play.goals,
         power_play.assists,
         short_handed.goals,
         short_handed.assists )
