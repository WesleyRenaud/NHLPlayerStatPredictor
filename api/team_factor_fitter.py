from __future__ import annotations

from .projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from .projections.nhl_lineup_selector import NhlLineupSelector
from .projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from .projections.team_lineup import TeamLineup
from .team_factor import TeamFactor
from .team_factor_skater import TeamFactorSkater


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
               TeamLineup.group( nhl_splits ) ),
            *cls._factors(
               current_season,
               NhlLineupSelector.select( roster_paces ) ),
         ],
         key=lambda factor: ( factor.season, factor.team.value ) )


   @classmethod
   def _factors(
         cls,
         season: int,
         lineups: list[ TeamLineup ] ) -> list[ TeamFactor ]:
      if not lineups:
         return []

      league = sum( lineup.total() for lineup in lineups ) / len( lineups )
      return [
         TeamFactor(
            season,
            lineup.team,
            lineup.total() / league,
            [
               TeamFactorSkater( skater.player_id, skater.contribution )
               for skater in lineup.skaters ] )
         for lineup in lineups
      ]
