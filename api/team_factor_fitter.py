from __future__ import annotations

from .projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from .projections.nhl_lineup_row import NhlLineupRow
from .projections.nhl_lineup_selector import NhlLineupSelector
from .projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from .projections.team_quality_calculator import TeamQualityCalculator
from .team_factor import TeamFactor


class TeamFactorFitter():
   @classmethod
   def fit(
         cls,
         current_season: int,
         previous_season_id: int,
         nhl_splits: list[ PreviousSeasonNhlSkater ],
         roster_paces: list[ CurrentSeasonNhlSkater ] ) -> list[ TeamFactor ]:
      return sorted(
         [
            *cls._factors(
               previous_season_id,
               NhlLineupSelector.select( nhl_splits ) ),
            *cls._factors(
               current_season,
               NhlLineupSelector.select( roster_paces ) ),
         ],
         key=lambda factor: ( factor.season, factor.team.value ) )


   @classmethod
   def _factors(
         cls,
         season: int,
         rows: list[ NhlLineupRow ] ) -> list[ TeamFactor ]:
      teams = { skater.team for skater in rows }

      if not teams:
         return []

      totals = {
         team: TeamQualityCalculator.total(
            [ skater for skater in rows if skater.team == team ] )
         for team in teams
      }
      league = sum( totals.values() ) / len( totals )
      return [
         TeamFactor( season, team, total / league )
         for team, total in totals.items()
      ]
