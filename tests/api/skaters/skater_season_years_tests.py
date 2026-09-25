from __future__ import annotations

from datetime import date

from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season_years import SkaterSeasonYears
from api.skaters.team import Team


def _season( player_id: int, season_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.0,
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


def Test_ByPlayer_TestSeasons_ExpectYearsByPlayer() -> None:
   first = _season( 1, 20222023 )
   second = _season( 1, 20232024 )
   other = _season( 2, 20232024 )
   seasons = [ first, second, other ]

   by_player = SkaterSeasonYears.by_player( seasons )

   assert by_player == {
      first.player_id: [ first, second ],
      other.player_id: [ other ],
   }


def Test_Consecutive_TestAdjacentYears_ExpectPair() -> None:
   current = _season( 1, 20222023 )
   following = _season( 1, 20232024 )

   pairs = SkaterSeasonYears.consecutive( [ following, current ] )

   assert pairs == [ ( current, following ) ]


def Test_Consecutive_TestGapYear_ExpectSkipped() -> None:
   current = _season( 1, 20212022 )
   later = _season( 1, 20232024 )

   pairs = SkaterSeasonYears.consecutive( [ current, later ] )

   assert pairs == []


def Test_AtYear_TestMatchingSeason_ExpectSeason() -> None:
   first = _season( 1, 20222023 )
   second = _season( 1, 20232024 )
   year = Season.start_year( second.season_id )

   found = SkaterSeasonYears.at_year( [ first, second ], year )

   assert found == second


def Test_AtYear_TestMissingYear_ExpectNone() -> None:
   first = _season( 1, 20222023 )
   missing_year = Season.start_year( first.season_id ) + 1

   found = SkaterSeasonYears.at_year( [ first ], missing_year )

   assert found is None
