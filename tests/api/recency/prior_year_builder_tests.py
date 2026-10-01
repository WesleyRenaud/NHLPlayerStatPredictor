from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.season_pace import SeasonPace
from api.recency.prior_year import PriorYear
from api.recency.prior_year_builder import PriorYearBuilder
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl(
      start_year: int,
      games_played: int,
      age: float = 25.4,
      goals: int = 0,
      assists: int = 0 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=start_year * 10000 + start_year + 1,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      goals=goals,
      assists=assists,
      points=goals + assists,
      schedule_games=82,
      pace_games=82,
      g_pace=20.0,
      a_pace=30.0,
      p_pace=50.0,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0 )


def _other( start_year: int, games_played: int, league: str = 'AAA' ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=start_year * 10000 + start_year + 1,
      league=league,
      position=SkaterPosition( 'C' ),
      age=25.2,
      games_played=games_played,
      goals=0,
      assists=0,
      points=0,
      g_pace=40.0,
      a_pace=60.0 )


def Test_Build_TestConsecutiveYears_ExpectMostRecentFirstUpToWidth() -> None:
   seasons = [ _nhl( year, 82 ) for year in range( 2020, 2025 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2025 )

   assert [ prior.year for prior in priors ] == [ 2024, 2023, 2022 ]


def Test_Build_TestTargetYearSeason_ExpectExcluded() -> None:
   seasons = [ _nhl( 2024, 82 ), _nhl( 2025, 82 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2025 )

   assert [ prior.year for prior in priors ] == [ 2024 ]


def Test_Build_TestMissedLatestSeason_ExpectEarlierRun() -> None:
   seasons = [ _nhl( 2021, 82 ), _nhl( 2022, 82 ), _nhl( 2023, 10 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2025 )

   assert [ prior.year for prior in priors ] == [ 2022, 2021 ]


def Test_Build_TestGapInsideRun_ExpectStopAtGap() -> None:
   seasons = [ _nhl( 2021, 82 ), _nhl( 2022, PriorYear.MIN_GAMES - 1 ), _nhl( 2023, 82 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2024 )

   assert [ prior.year for prior in priors ] == [ 2023 ]


def Test_Build_TestMixedYear_ExpectCombinedTranslatedPace() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   nhl = _nhl( 2024, 10, 20.8 )
   other = _other( 2024, 40 )
   games = nhl.games_played + other.games_played

   priors = PriorYearBuilder.build( [ nhl, other ], [ factor ], 2025 )

   assert len( priors ) == 1
   prior = priors[ Position.FIRST ]
   assert prior.games == games
   assert prior.nhl_games == nhl.games_played
   assert prior.age == other.age
   assert prior.pace.goals == pytest.approx(
      ( nhl.games_played * nhl.g_pace + other.games_played * other.g_pace * factor.rate )
      / games )


def Test_Build_TestUnknownLeague_ExpectSkipped() -> None:
   seasons = [ _other( 2024, 60, 'ZZZ' ) ]

   priors = PriorYearBuilder.build( seasons, [ LeagueFactor( 'AAA', 0.5 ) ], 2025 )

   assert priors == []


def Test_Build_TestPlayoffYear_ExpectSeasonSurplus() -> None:
   season = replace(
      _nhl( 2024, 80, goals=20, assists=40 ),
      playoff_games=20,
      playoff_goals=8,
      playoff_assists=6 )

   priors = PriorYearBuilder.build( [ season ], [], 2025 )

   assert priors[ Position.FIRST ].playoff_surplus == season.playoff_surplus()


def Test_Build_TestOtherLeagueYear_ExpectNoSurplus() -> None:
   season = _other( 2024, 60 )
   factor = LeagueFactor( season.league, 0.5 )

   priors = PriorYearBuilder.build( [ season ], [ factor ], 2025 )

   assert priors[ Position.FIRST ].playoff_surplus == SeasonPace.zero()
