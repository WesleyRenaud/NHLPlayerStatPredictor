from __future__ import annotations

from datetime import date

from api.availability.games_share import GamesShare
from api.availability.mixed_season_share_binder import MixedSeasonShareBinder
from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl( gp_share: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=20252026,
      player_name='Stub',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=9,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=gp_share )


def _other( games_played: int, season_id: int = 20252026 ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=season_id,
      league=list( ClubLeague )[ Position.FIRST ].value,
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=games_played,
      goals=0,
      assists=0,
      points=0,
      g_pace=0.0,
      a_pace=0.0 )


def Test_Bind_TestNhlOnly_ExpectShareUnchanged() -> None:
   share = 0.11
   assert MixedSeasonShareBinder.bind( [ _nhl( share ) ], [] )[ Position.FIRST ].gp_share == (
      share )


def Test_Bind_TestOtherLeagueGames_ExpectFull() -> None:
   share = 0.11
   bound = MixedSeasonShareBinder.bind( [ _nhl( share ) ], [ _other( 35 ) ] )
   assert bound[ Position.FIRST ].gp_share == GamesShare.FULL


def Test_Bind_TestZeroOtherGames_ExpectShareUnchanged() -> None:
   share = 0.11
   bound = MixedSeasonShareBinder.bind( [ _nhl( share ) ], [ _other( 0 ) ] )
   assert bound[ Position.FIRST ].gp_share == share


def Test_Bind_TestOtherSeasonDifferentYear_ExpectUnrelatedUnchanged() -> None:
   share = 0.11
   bound = MixedSeasonShareBinder.bind(
      [ _nhl( share ) ],
      [ _other( 35, 20242025 ) ] )
   assert bound[ Position.FIRST ].gp_share == share
