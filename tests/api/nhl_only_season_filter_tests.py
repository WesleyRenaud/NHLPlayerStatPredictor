from __future__ import annotations

from datetime import date

from api.nhl_only_season_filter import NhlOnlySeasonFilter
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _nhl( player_id: int, season_id: int ) -> NhlSkaterSeason:
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
      gp_share=0.5 )


def _other(
      player_id: int,
      season_id: int,
      games_played: int,
      league: str = 'AAA' ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      league=league,
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=games_played,
      goals=0,
      assists=0,
      points=0,
      g_pace=0.0,
      a_pace=0.0 )


def Test_Keep_TestNoOtherSeasons_ExpectAllKept() -> None:
   nhl = [ _nhl( 1, 20252026 ), _nhl( 2, 20252026 ) ]
   assert NhlOnlySeasonFilter.keep( nhl, [] ) == nhl


def Test_Keep_TestOtherLeagueGames_ExpectExcluded() -> None:
   assert NhlOnlySeasonFilter.keep(
      [ _nhl( 1, 20252026 ) ],
      [ _other( 1, 20252026, 1 ) ]
      ) == []


def Test_Keep_TestZeroOtherGames_ExpectKept() -> None:
   nhl = [ _nhl( 1, 20252026 ) ]
   assert NhlOnlySeasonFilter.keep(
      nhl,
      [ _other( 1, 20252026, 0 ) ]
      ) == nhl


def Test_Keep_TestMultipleLeagues_ExpectExcluded() -> None:
   other = [
      _other( 1, 20252026, 1 ),
      _other( 1, 20252026, 1, 'BBB' ),
   ]
   assert NhlOnlySeasonFilter.keep( [ _nhl( 1, 20252026 ) ], other ) == []


def Test_Keep_TestOtherSeasonDifferentYear_ExpectUnrelatedKept() -> None:
   nhl = [ _nhl( 1, 20242025 ), _nhl( 1, 20252026 ) ]
   assert NhlOnlySeasonFilter.keep(
      nhl,
      [ _other( 1, 20242025, 1 ) ]
      ) == [ nhl[ Position.SECOND ] ]
