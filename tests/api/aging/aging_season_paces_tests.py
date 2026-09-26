from __future__ import annotations

from api.aging.aging_season_paces import AgingSeasonPaces
from api.depth.usable_nhl_ice import UsableNhlIce
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason


def _season(
      g_pace: float,
      a_pace: float,
      games_played: int,
      goals: int = 0,
      assists: int = 0 ) -> SkaterSeason:
   return SkaterSeason(
      player_id=1,
      season_id=20232024,
      age=28.0,
      games_played=games_played,
      goals=goals,
      assists=assists,
      points=goals + assists,
      g_pace=g_pace,
      a_pace=a_pace,
      position=SkaterPosition( 'C' ) )


def Test_Resolve_TestEnoughGames_ExpectOwnPaces() -> None:
   season = _season( 0.0, 84.0, UsableNhlIce.MIN_GAMES, assists=1 )
   mix_from = _season( 20.0, 24.0, UsableNhlIce.MIN_GAMES, goals=20, assists=24 )

   paces = AgingSeasonPaces.resolve( season, mix_from )

   assert paces == ( season.g_pace, season.a_pace )


def Test_Resolve_TestOneAssistGame_ExpectDonorMix() -> None:
   season = _season( 0.0, 84.0, 1, assists=1 )
   mix_from = _season( 20.0, 24.0, UsableNhlIce.MIN_GAMES, goals=20, assists=24 )
   points = season.g_pace + season.a_pace
   mix_points = mix_from.g_pace + mix_from.a_pace
   share = mix_from.g_pace / mix_points

   paces = AgingSeasonPaces.resolve( season, mix_from )

   assert paces == ( points * share, points * ( 1.0 - share ) )


def Test_Resolve_TestOneGoalGame_ExpectDonorMix() -> None:
   season = _season( 84.0, 0.0, 1, goals=1 )
   mix_from = _season( 20.0, 24.0, UsableNhlIce.MIN_GAMES, goals=20, assists=24 )
   points = season.g_pace + season.a_pace
   mix_points = mix_from.g_pace + mix_from.a_pace
   share = mix_from.g_pace / mix_points

   paces = AgingSeasonPaces.resolve( season, mix_from )

   assert paces == ( points * share, points * ( 1.0 - share ) )


def Test_Resolve_TestThinDonor_ExpectOwnPaces() -> None:
   season = _season( 0.0, 84.0, 1, assists=1 )
   mix_from = _season( 20.0, 24.0, 1, goals=20, assists=24 )

   paces = AgingSeasonPaces.resolve( season, mix_from )

   assert paces == ( season.g_pace, season.a_pace )


def Test_Resolve_TestZeroDonorPace_ExpectOwnPaces() -> None:
   season = _season( 0.0, 84.0, 1, assists=1 )
   mix_from = _season( 0.0, 0.0, UsableNhlIce.MIN_GAMES )

   paces = AgingSeasonPaces.resolve( season, mix_from )

   assert paces == ( season.g_pace, season.a_pace )
