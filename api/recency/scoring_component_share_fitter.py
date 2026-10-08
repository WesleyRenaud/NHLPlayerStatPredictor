from __future__ import annotations

from .prior_year import PriorYear
from .production_coefficient_fitter import ProductionCoefficientFitter
from ..projections.scoring_component_shares import ScoringComponentShares
from ..skaters.nhl_skater_season import NhlSkaterSeason


class ScoringComponentShareFitter():
   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ ScoringComponentShares ]:
      qualified = [ season for season in seasons if season.games_played >= PriorYear.MIN_GAMES ]
      shares = []

      for age in sorted( { season.age for season in qualified } ):
         selected = [ season for season in qualified if season.age == age ]

         if len( selected ) < ProductionCoefficientFitter.MIN_SUPPORT:
            selected = [ season for season in qualified if abs( season.age - age ) <= 1 ]

         if len( selected ) < ProductionCoefficientFitter.MIN_SUPPORT:
            selected = qualified

         goals = sum( season.goals for season in selected )
         assists = sum( season.assists for season in selected )
         shares.append( ScoringComponentShares(
            age=age,
            even_strength_goals=1.0 if not goals else sum(
               season.even_strength_goals
               for season in selected ) / goals,
            even_strength_assists=1.0 if not assists else sum(
               season.even_strength_points - season.even_strength_goals
               for season in selected ) / assists,
            power_play_goals=0.0 if not goals else sum( season.power_play_goals for season in selected ) / goals,
            power_play_assists=0.0 if not assists else sum( season.power_play_points - season.power_play_goals for season in selected ) / assists,
            short_handed_goals=0.0 if not goals else sum( season.short_handed_goals for season in selected ) / goals,
            short_handed_assists=0.0 if not assists else sum( season.short_handed_points - season.short_handed_goals for season in selected ) / assists ) )

      return shares
