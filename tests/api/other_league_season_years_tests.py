from __future__ import annotations

from api.club_league import ClubLeague
from api.other_league_season_years import OtherLeagueSeasonYears
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.season import Season
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition


def _league( index: Position ) -> str:
   return list( ClubLeague )[ index ].value


def _season(
      player_id: int,
      season_id: int,
      league: str ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      league=league,
      position=SkaterPosition( 'C' ),
      age=17.0,
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      g_pace=0.0,
      a_pace=0.0 )


def Test_ByPlayerLeague_TestSeasons_ExpectYearsByPlayerAndLeague() -> None:
   league = _league( Position.FIRST )
   first = _season( 1, 20222023, league )
   second = _season( 1, 20232024, league )
   other = _season( 2, 20232024, league )
   by_player = OtherLeagueSeasonYears.by_player_league( [ first, second, other ] )
   assert by_player == {
      first.player_id: {
         league: {
            Season.start_year( first.season_id ): first,
            Season.start_year( second.season_id ): second,
         },
      },
      other.player_id: {
         league: {
            Season.start_year( other.season_id ): other,
         },
      },
   }


def Test_Consecutive_TestAdjacentYears_ExpectPair() -> None:
   league = _league( Position.FIRST )
   current = _season( 1, 20222023, league )
   following = _season( 1, 20232024, league )
   assert OtherLeagueSeasonYears.consecutive( [ following, current ] ) == [
      ( current, following )
   ]


def Test_Consecutive_TestGapYear_ExpectSkipped() -> None:
   league = _league( Position.FIRST )
   current = _season( 1, 20212022, league )
   later = _season( 1, 20232024, league )
   assert OtherLeagueSeasonYears.consecutive( [ current, later ] ) == []


def Test_Consecutive_TestCrossLeague_ExpectSkipped() -> None:
   current = _season( 1, 20222023, _league( Position.FIRST ) )
   following = _season( 1, 20232024, _league( Position.SECOND ) )
   assert OtherLeagueSeasonYears.consecutive( [ current, following ] ) == []
