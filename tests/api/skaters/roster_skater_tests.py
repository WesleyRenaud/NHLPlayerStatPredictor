from __future__ import annotations

from datetime import date

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season( season_id: int, player_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=1.0 )


def Test_FromRow_TestStoredFields_ExpectValues() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   row = RosterSkater.from_row( {
      'PLAYER_ID': 7,
      'PLAYER_NAME': 'Stub Skater',
      'POSITION': position.value,
      'TEAM': team.value,
   } )
   assert row == RosterSkater( 7, 'Stub Skater', position, team )


def Test_WithLastPlayed_TestNhlSeasons_ExpectLatestPerPlayer() -> None:
   roster_id = 2
   other_id = 1
   team = list( Team )[ Position.FIRST ]
   roster = [
      RosterSkater(
         roster_id,
         'A',
         SkaterPosition( 'C' ),
         team )
   ]
   stamped = RosterSkater.with_last_played(
      roster,
      [
         _season( 20232024, other_id ),
         _season( 20242025, roster_id ),
         _season( 20232024, roster_id ),
      ] )
   assert stamped == [
      RosterSkater(
         roster_id,
         'A',
         SkaterPosition( 'C' ),
         team,
         last_played_season_id=20242025 )
   ]


def Test_WithLastPlayed_TestNoNhl_ExpectNone() -> None:
   team = list( Team )[ Position.FIRST ]
   roster = [
      RosterSkater(
         2,
         'A',
         SkaterPosition( 'C' ),
         team )
   ]
   assert RosterSkater.with_last_played(
      roster,
      [ _season( 20242025, 1 ) ] ) == roster
