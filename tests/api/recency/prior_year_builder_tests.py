from __future__ import annotations

from dataclasses import replace
from datetime import date
from unittest.mock import Mock

import pytest

from api.aging.league_arrival import LeagueArrival
from api.aging.league_arrival_averager import LeagueArrivalAverager
from api.aging.league_factor import LeagueFactor
from api.projections.scoring_component_shares import ScoringComponentShares
from api.projections.scoring_paces import ScoringPaces
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.projections.year_pace import YearPace
from api.recency.prior_year import PriorYear
from api.recency.prior_year_builder import PriorYearBuilder
from api.recency.production_growth import ProductionGrowth
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl(
      start_year: int,
      games_played: int,
      age: int = 25,
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
      even_strength_goals=goals,
      even_strength_points=( goals + assists ),
      goals=goals,
      assists=assists,
      points=goals + assists,
      schedule_games=82,
      pace_games=82,
      g_pace=Season.pace( goals, games_played, 82 ),
      a_pace=Season.pace( assists, games_played, 82 ),
      p_pace=Season.pace( goals + assists, games_played, 82 ),
      gp_share=1.0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      shots=0,
      penalty_minutes=0 )


def _other( start_year: int, games_played: int, league: str = 'AAA' ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=start_year * 10000 + start_year + 1,
      league=league,
      position=SkaterPosition( 'C' ),
      age=25,
      games_played=games_played,
      goals=0,
      assists=0,
      points=0,
      g_pace=40.0,
      a_pace=60.0 )


def Test_Build_TestConsecutiveYears_ExpectMostRecentFirstUpToWidth() -> None:
   seasons = [ _nhl( year, 82 ) for year in range( 2020, 2025 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2025, [] )

   assert [ prior.year for prior in priors ] == [ 2024, 2023, 2022 ]


def Test_Build_TestTargetYearSeason_ExpectExcluded() -> None:
   seasons = [ _nhl( 2024, 82 ), _nhl( 2025, 82 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2025, [] )

   assert [ prior.year for prior in priors ] == [ 2024 ]


def Test_Build_TestSmallLatestSeason_ExpectLeftOut() -> None:
   seasons = [ _nhl( 2021, 82 ), _nhl( 2022, 82 ), _nhl( 2023, 10 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2025, [] )

   assert [ prior.year for prior in priors ] == [ 2022, 2021 ]


def Test_Build_TestSmallSeasonInsideRun_ExpectLeftOut() -> None:
   seasons = [ _nhl( 2021, 82 ), _nhl( 2022, PriorYear.MIN_GAMES - 1 ), _nhl( 2023, 82 ) ]

   priors = PriorYearBuilder.build( seasons, [], 2024, [] )

   assert [ prior.year for prior in priors ] == [ 2023, 2021 ]


@pytest.mark.parametrize( 'games', [ 1, 5, 10, 19, 20, 60 ] )
def Test_Build_TestPositiveGameCount_ExpectHistoryPreserved( games: int ) -> None:
   priors = PriorYearBuilder.build( [ _nhl( 2024, games ) ], [], 2025, [] )

   assert len( priors ) == 1
   assert priors[ 0 ].games == games


def Test_Build_TestZeroGames_ExpectExcluded() -> None:
   season = replace( _nhl( 2024, 1 ), games_played=0 )

   assert PriorYearBuilder.build( [ season ], [], 2025, [] ) == []


def Test_Build_TestEnteringCallUp_ExpectNhlStintInArrival() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   rate = 0.9
   age_step = 3.0
   shares = ScoringComponentShares( 25, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0 )
   call_up_games = PriorYear.MIN_GAMES // 2 - 1
   call_up = _nhl( 2024, call_up_games, goals=10, assists=10 )
   college = _other( 2024, 40 )
   arrival = LeagueArrival( college.league, college.age, rate )
   growth = ProductionGrowth( college.age, college.age + 1, age_step, 1 )
   expected = LeagueArrivalAverager.scoring(
      [ call_up, college ], [ factor ], [ arrival ], [ shares ], age_step )

   priors = PriorYearBuilder.build(
      [ call_up, college ],
      [ factor ],
      2025,
      [ shares ],
      arrivals=[ arrival ],
      scoring_growth=[ growth ] )

   assert len( priors ) == 1
   prior = priors[ Position.FIRST ]
   assert prior.games == college.games_played
   assert prior.nhl_games == 0
   assert expected is not None
   assert prior.arrival is not None
   assert prior.arrival.goals == pytest.approx( expected.goals )


def Test_Build_TestPartialStintOnArrival_ExpectNhlGamesInArrival() -> None:
   stint_games = PriorYear.MIN_GAMES // 2
   college_games = 40
   rate = 0.9
   age_step = 3.0
   stint = _nhl( 2024, stint_games, goals=10, assists=0 )
   college = _other( 2024, college_games )
   factor = LeagueFactor( college.league, 0.5 )
   shares = ScoringComponentShares( college.age, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0 )
   growth = ProductionGrowth( college.age, college.age + 1, age_step, 1 )
   arrival = LeagueArrival( college.league, college.age, rate )
   expected = LeagueArrivalAverager.scoring(
      [ stint, college ], [ factor ], [ arrival ], [ shares ], age_step )

   priors = PriorYearBuilder.build(
      [ stint, college ],
      [ factor ],
      2025,
      [ shares ],
      arrivals=[ arrival ],
      scoring_growth=[ growth ] )

   prior = priors[ Position.FIRST ]
   assert prior.games == college_games
   assert prior.nhl_games == 0
   assert expected is not None
   assert prior.arrival is not None
   assert prior.arrival.goals == pytest.approx( expected.goals )


def Test_Build_TestCallUpBesideFullSeason_ExpectCallUpLeftOut() -> None:
   call_up_games = 5
   college_games = 37
   full = _nhl( 2025, PriorYear.MIN_GAMES, age=21 )
   call_up = _nhl( 2024, call_up_games, age=20 )
   college = _other( 2024, college_games )
   factor = LeagueFactor( college.league, 0.5 )
   shares = ScoringComponentShares( 20, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )

   priors = PriorYearBuilder.build(
      [ full, call_up, college ], [ factor ], 2026, [ shares ] )

   by_year = { prior.year: prior for prior in priors }
   full_year = Season.start_year( full.season_id )
   assert Season.start_year( call_up.season_id ) not in by_year
   assert by_year[ full_year ].games == full.games_played
   assert by_year[ full_year ].nhl_games == full.games_played


def Test_Build_TestPartialSeasonWithOtherLeague_ExpectLeftOut() -> None:
   partial_games = PriorYear.MIN_GAMES // 2
   other_games = 36
   full = _nhl( 2025, PriorYear.MIN_GAMES, age=22 )
   partial = _nhl( 2024, partial_games, age=21, goals=2, assists=0 )
   other = _other( 2024, other_games )
   factor = LeagueFactor( other.league, 0.5 )
   shares = ScoringComponentShares( 21, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )

   priors = PriorYearBuilder.build(
      [ full, partial, other ], [ factor ], 2026, [ shares ] )

   by_year = { prior.year: prior for prior in priors }
   assert Season.start_year( partial.season_id ) not in by_year
   assert by_year[ Season.start_year( full.season_id ) ].games == full.games_played
   assert by_year[ Season.start_year( full.season_id ) ].nhl_games == full.games_played


def Test_Build_TestFullSeasonWithOtherLeague_ExpectNoArrival() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   rate = 0.9
   shares = ScoringComponentShares( 25, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0 )
   nhl = _nhl( 2024, PriorYear.MIN_GAMES, goals=10, assists=10 )
   other = _other( 2024, 20 )

   priors = PriorYearBuilder.build(
      [ nhl, other ],
      [ factor ],
      2025,
      [ shares ],
      arrivals=[ LeagueArrival( other.league, other.age, rate ) ],
      scoring_growth=[ ProductionGrowth( other.age, other.age + 1, 3.0, 1 ) ] )

   prior = priors[ Position.FIRST ]
   assert prior.games == nhl.games_played
   assert prior.nhl_games == nhl.games_played
   assert prior.arrival is None
   assert prior.scoring.even_strength_goals == pytest.approx(
      nhl.scoring_paces().even_strength_goals )


def Test_Build_TestLaterOtherLeague_ExpectNhlYearOnly() -> None:
   full = _nhl( 2023, PriorYear.MIN_GAMES )
   later = _other( 2025, 40 )
   shares = ScoringComponentShares( 25, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0 )

   priors = PriorYearBuilder.build(
      [ full, later ], [ LeagueFactor( later.league, 0.5 ) ], 2026, [ shares ] )

   assert [ prior.year for prior in priors ] == [ Season.start_year( full.season_id ) ]
   assert priors[ Position.FIRST ].nhl_games == full.games_played


def Test_Build_TestUnknownLeague_ExpectSkipped() -> None:
   seasons = [ _other( 2024, 60, 'ZZZ' ) ]

   priors = PriorYearBuilder.build( seasons, [ LeagueFactor( 'AAA', 0.5 ) ], 2025, [] )

   assert priors == []


def Test_Build_TestEnteringYear_ExpectArrivalOnlyOnThatSeason() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   rate = 0.9
   shares = ScoringComponentShares( 25, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0 )
   entering = _other( 2024, 40 )
   earlier = _other( 2023, 40 )

   priors = PriorYearBuilder.build(
      [ entering, earlier ],
      [ factor ],
      2025,
      [ shares ],
      arrivals=[ LeagueArrival( 'AAA', 25, rate ) ],
      scoring_growth=[ ProductionGrowth( 25, 26, 3.0, 1 ) ] )

   assert priors[ 0 ].year == 2024
   assert priors[ 0 ].arrival is not None
   assert priors[ 0 ].arrival.goals == pytest.approx( entering.g_pace * rate )
   assert priors[ 1 ].arrival is None
   assert priors[ 1 ].scoring.goals == pytest.approx( earlier.g_pace * factor.rate )


def Test_Build_TestOtherLeagueYear_ExpectMissingPim() -> None:
   season = _other( 2024, 60 )
   factor = LeagueFactor( season.league, 0.5 )
   shares = ScoringComponentShares( 25, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )

   priors = PriorYearBuilder.build( [ season ], [ factor ], 2025, [ shares ] )

   assert priors[ Position.FIRST ].pim_pace is None


def Test_History_TestPreparedYear_ExpectReuseOfScoringAndGameCounts(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season = _nhl( 2024, 82 )
   scoring = ScoringPaces( 10.0, 20.0, 2.0, 4.0, 1.0, 1.0 )
   prepared = YearPace( scoring, 12.0, season.games_played, season.games_played )
   averaging = Mock( return_value=prepared )
   monkeypatch.setattr( TranslatedPaceAverager, 'year', averaging )

   history = PriorYearBuilder.history( [ season ], [], [] )

   averaging.assert_called_once_with( [ season ], [], [], None )
   prior = history[ Position.FIRST ]
   assert prior.scoring is scoring
   assert prior.games == prepared.games
   assert prior.nhl_games == prepared.nhl_games
   assert prior.pim_pace == prepared.penalty_minutes
