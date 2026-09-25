from __future__ import annotations

from dataclasses import replace
from datetime import date

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater import Skater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl() -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=20252026,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=20,
      assists=30,
      points=50,
      schedule_games=82,
      pace_games=84,
      g_pace=20.0,
      a_pace=30.0,
      p_pace=50.0,
      gp_share=1.0 )


def _other() -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )


def Test_NhlSeasons_TestMixed_ExpectNhlRows() -> None:
   nhl = _nhl()
   other = _other()
   skater = Skater( [ nhl, other ] )

   seasons = skater.nhl_seasons()

   assert seasons == [ nhl ]


def Test_NhlSeasons_TestOtherLeagueOnly_ExpectEmpty() -> None:
   other = _other()
   skater = Skater( [ other ] )

   seasons = skater.nhl_seasons()

   assert seasons == []


def Test_LastPlayedSeasonId_TestNhlSeasons_ExpectLatest() -> None:
   later = _nhl()
   earlier_season_id = 20242025
   earlier = replace( later, season_id=earlier_season_id )
   other = _other()
   skater = Skater( [ later, earlier, other ] )

   last_played = skater.last_played_season_id()

   assert last_played == later.season_id


def Test_LastPlayedSeasonId_TestOtherLeagueOnly_ExpectNone() -> None:
   other = _other()
   skater = Skater( [ other ] )

   last_played = skater.last_played_season_id()

   assert last_played is None
