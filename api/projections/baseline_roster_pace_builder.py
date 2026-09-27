from __future__ import annotations

from collections import defaultdict

from ..aging.league_factor import LeagueFactor
from .baseline_pace_resolver import BaselinePaceResolver
from .current_season_nhl_skater import CurrentSeasonNhlSkater
from ..recency.pace_regression_model import PaceRegressionModel
from ..skaters.roster_skater import RosterSkater
from ..skaters.skater import Skater
from ..skaters.skater_season import SkaterSeason


class BaselineRosterPaceBuilder():
   @classmethod
   def build(
         cls,
         roster: list[ RosterSkater ],
         seasons: list[ SkaterSeason ],
         target_season_id: int,
         league_factors: list[ LeagueFactor ],
         model: PaceRegressionModel ) -> list[ CurrentSeasonNhlSkater ]:
      by_id: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_id[ season.player_id ].append( season )

      rows: list[ CurrentSeasonNhlSkater ] = []

      for skater in roster:
         pace = BaselinePaceResolver.resolve(
            Skater( by_id[ skater.player_id ] ),
            target_season_id,
            league_factors,
            model )

         if pace is None:
            continue

         rows.append(
            CurrentSeasonNhlSkater(
               skater.player_id,
               pace,
               skater.team,
               skater.position ) )

      return rows
