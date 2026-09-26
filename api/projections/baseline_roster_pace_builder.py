from __future__ import annotations

from collections import defaultdict

from ..aging.aging_factor import AgingFactor
from ..aging.league_factor import LeagueFactor
from .baseline_pace_resolver import BaselinePaceResolver
from .current_season_nhl_skater import CurrentSeasonNhlSkater
from ..recency.age_recency_weights import AgeRecencyWeights
from ..skaters.roster_skater import RosterSkater
from ..skaters.skater import Skater
from ..skaters.skater_season import SkaterSeason


class BaselineRosterPaceBuilder():
   @classmethod
   def build(
         cls,
         roster: list[ RosterSkater ],
         seasons: list[ SkaterSeason ],
         weights: list[ AgeRecencyWeights ],
         target_season_id: int,
         league_factors: list[ LeagueFactor ],
         aging_factors: list[ AgingFactor ] ) -> list[ CurrentSeasonNhlSkater ]:
      by_id: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_id[ season.player_id ].append( season )

      rows: list[ CurrentSeasonNhlSkater ] = []

      for skater in roster:
         pace = BaselinePaceResolver.resolve(
            Skater( by_id[ skater.player_id ] ),
            weights,
            target_season_id,
            league_factors,
            aging_factors )

         if pace is None:
            continue

         rows.append(
            CurrentSeasonNhlSkater(
               skater.player_id,
               pace,
               skater.team,
               skater.position ) )

      return rows
