from __future__ import annotations

from .league_factor import LeagueFactor
from .nhl_skater_season import NhlSkaterSeason
from .other_league_skater_season import OtherLeagueSkaterSeason
from .projections.last_season_group import LastSeasonGroup
from .projections.last_season_nhl_skater import LastSeasonNhlSkater
from .projections.last_season_skater import LastSeasonSkater
from .projections.last_season_skater_builder import LastSeasonSkaterBuilder
from .projections.team_quality_calculator import TeamQualityCalculator
from .roster_skater import RosterSkater
from .team import Team
from .team_factor import TeamFactor


class TeamFactorFitter():
   @classmethod
   def fit(
         cls,
         roster: list[ RosterSkater ],
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         league_factors: list[ LeagueFactor ],
         current_season: int,
         last_season_id: int,
         nhl_splits: list[ LastSeasonNhlSkater ] ) -> list[ TeamFactor ]:
      last_season = LastSeasonSkaterBuilder.build(
         nhl_seasons,
         other_seasons,
         league_factors )
      return sorted(
         [
            *cls._nhl_factors( last_season_id, nhl_splits ),
            *cls._roster_factors( current_season, roster, last_season ),
         ],
         key=lambda factor: ( factor.season, factor.team.value ) )


   @classmethod
   def _nhl_factors(
         cls,
         season: int,
         nhl: list[ LastSeasonNhlSkater ] ) -> list[ TeamFactor ]:
      league = TeamQualityCalculator.average( nhl )
      return [
         cls._factor(
            season,
            team,
            [ skater for skater in nhl if skater.team == team ],
            league )
         for team in { skater.team for skater in nhl }
      ]


   @classmethod
   def _roster_factors(
         cls,
         season: int,
         roster: list[ RosterSkater ],
         last_season: LastSeasonGroup ) -> list[ TeamFactor ]:
      paces = { skater.player_id: skater for skater in last_season.skaters() }
      skaters = [
         paces[ skater.player_id ]
         for skater in roster
         if skater.player_id in paces
      ]
      league = TeamQualityCalculator.average( skaters )
      return [
         cls._factor(
            season,
            team,
            [
               paces[ skater.player_id ]
               for skater in roster
               if skater.team == team and skater.player_id in paces
            ],
            league )
         for team in { skater.team for skater in roster }
      ]


   @classmethod
   def _factor(
         cls,
         season: int,
         team: Team,
         skaters: list[ LastSeasonSkater ],
         league: float ) -> TeamFactor:
      return TeamFactor(
         season,
         team,
         TeamQualityCalculator.average( skaters ) / league )
