from __future__ import annotations

from api.depth.ice_usage import IceUsage
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.projections.team_lineup import TeamLineup
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.team_factor.team_factor import TeamFactor
from api.team_factor.team_factor_previous_builder import TeamFactorPreviousBuilder


def _split(
      player_id: int,
      team: Team,
      games: int,
      points: float ) -> PreviousSeasonNhlSkater:
   return PreviousSeasonNhlSkater(
      player_id,
      games,
      SeasonPace( points / 2.0, points / 2.0 ),
      SkaterPosition( 'D' ),
      team )


def _defense(
      team: Team,
      callup_games: int,
      callup_pace: float ) -> list[ PreviousSeasonNhlSkater ]:
   veterans = [
      _split( player_id, team, 82, 20.0 )
      for player_id in range( 2, NhlLineupSelector.DRESSED_DEFENSE + 1 )
   ]
   extra = _split( NhlLineupSelector.DEFENSE, team, 82, 10.0 )
   return [ _split( 1, team, callup_games, callup_pace ), *veterans, extra ]


def Test_Build_TestCallUpByToi_ExpectGamesShare() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   callup_pace = 168.0
   veteran_pace = 20.0
   extra_pace = 10.0
   usages = {
      1: IceUsage( 16.5, 1, team, SkaterPosition( 'D' ) ),
      **{
         player_id: IceUsage( 15.0, season_length, team, SkaterPosition( 'D' ) )
         for player_id in range( 2, NhlLineupSelector.DRESSED_DEFENSE + 1 )
      },
      NhlLineupSelector.DEFENSE: IceUsage(
         extra_pace,
         season_length,
         team,
         SkaterPosition( 'D' ) ),
   }

   rows = TeamFactorPreviousBuilder.build(
      TeamLineup( team, _defense( team, 1, callup_pace ) ),
      [],
      usages,
      season_length )

   callup = next( row for row in rows if row.player_id == 1 )
   present = callup_pace + veteran_pace * ( NhlLineupSelector.DRESSED_DEFENSE - 1 )
   replacement = (
      veteran_pace * ( NhlLineupSelector.DRESSED_DEFENSE - 1 ) + extra_pace )
   expected = (
      present / season_length
      + replacement * ( season_length - 1 ) / season_length )
   total = TeamFactor( 20252026, team, 1.0, rows ).dressed_total()
   assert callup.availability == 1 / season_length
   assert callup.contribution == callup_pace
   assert callup.extra is False
   assert abs( total - expected ) < 0.001


def Test_Build_TestCallUpWithoutUsage_ExpectGamesShare() -> None:
   team = list( Team )[ Position.FIRST ]
   season_length = 82
   callup_pace = 168.0

   rows = TeamFactorPreviousBuilder.build(
      TeamLineup( team, _defense( team, 1, callup_pace ) ),
      [],
      {},
      season_length )

   callup = next( row for row in rows if row.player_id == 1 )
   assert callup.availability == 1 / season_length
   assert callup.contribution == callup_pace
   assert callup.extra is False
